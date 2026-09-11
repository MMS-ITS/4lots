#!/usr/bin/env python3
"""Derive true-scale terrain data for each of the four lots.

For every parcel this produces, into data/terrain.json:

  * the boundary in a local metre grid (origin = parcel centroid, +x east, +y north)
  * the county 1-foot LiDAR contours clipped to the parcel and a 40 m halo
  * an A-B transect running from the road frontage to the water frontage
  * a dense elevation profile along that transect, sampled from the USGS 3DEP
    1-metre DEM, in feet
  * segment slope angles, the steepest break, and the earth-curvature correction

Sources
  Brazoria County ArcGIS  general/LiDAR/MapServer/0        1 ft contours
  Brazoria County ArcGIS  general/Roads/MapServer/1        street centrelines
  USGS 3DEP ImageServer   getSamples                       1 m DEM, metres
  OpenStreetMap Overpass                                   water bodies
"""
import json, math, os, time, urllib.request, urllib.parse

UA = {'User-Agent': '4lots-feasibility-research/1.0'}
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GEO = os.path.join(ROOT, 'data', 'parcels.geojson')
OUT = os.path.join(ROOT, 'data', 'terrain.json')

CONTOURS = "https://arcgis-web.brazoriacountytx.gov/arcgis/rest/services/general/LiDAR/MapServer/0/query"
ROADS = "https://arcgis-web.brazoriacountytx.gov/arcgis/rest/services/general/Roads/MapServer/1/query"
DEM = "https://elevation.nationalmap.gov/arcgis/rest/services/3DEPElevation/ImageServer/getSamples"
M_PER_FT = 0.3048
R_EARTH = 6371008.8

STREET = {'lot1': 'SADDLE HORN', 'lot2': 'WAGON WHEEL', 'lot3': 'BROKEN ARROW', 'lot4': 'WAGON WHEEL'}


def post(url, params, timeout=180, tries=4):
    last = None
    for i in range(tries):
        try:
            r = urllib.request.Request(url, data=urllib.parse.urlencode(params).encode(), headers=UA)
            return json.load(urllib.request.urlopen(r, timeout=timeout))
        except Exception as ex:
            last = ex
            time.sleep(3 + 4 * i)
    raise last


# ---------------------------------------------------------------- local metre frame
class Frame:
    """Equirectangular projection about an origin; good to <1 cm over a few hundred m."""

    def __init__(self, lat0, lon0):
        self.lat0, self.lon0 = lat0, lon0
        self.mlat = 111132.92 - 559.82 * math.cos(2 * math.radians(lat0)) \
            + 1.175 * math.cos(4 * math.radians(lat0))
        self.mlon = 111412.84 * math.cos(math.radians(lat0)) \
            - 93.5 * math.cos(3 * math.radians(lat0))

    def fwd(self, lon, lat):
        return ((lon - self.lon0) * self.mlon, (lat - self.lat0) * self.mlat)

    def inv(self, x, y):
        return (self.lon0 + x / self.mlon, self.lat0 + y / self.mlat)


def seg_point_dist(px, py, ax, ay, bx, by):
    """Distance from P to segment AB, plus the closest point."""
    dx, dy = bx - ax, by - ay
    L2 = dx * dx + dy * dy
    t = 0.0 if L2 == 0 else max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / L2))
    cx, cy = ax + t * dx, ay + t * dy
    return math.hypot(px - cx, py - cy), cx, cy


def poly_point_dist(px, py, ring):
    best = (float('inf'), 0, 0)
    for i in range(len(ring) - 1):
        d, cx, cy = seg_point_dist(px, py, ring[i][0], ring[i][1], ring[i + 1][0], ring[i + 1][1])
        if d < best[0]:
            best = (d, cx, cy)
    return best


def point_in_ring(px, py, ring):
    inside = False
    n = len(ring)
    for i in range(n - 1):
        x1, y1 = ring[i]
        x2, y2 = ring[i + 1]
        if (y1 > py) != (y2 > py):
            xin = x1 + (py - y1) * (x2 - x1) / (y2 - y1)
            if px < xin:
                inside = not inside
    return inside


def clip_to_box(pts, box):
    """Split a polyline into runs that fall inside an axis-aligned box."""
    x0, y0, x1, y1 = box
    runs, cur = [], []
    for p in pts:
        if x0 <= p[0] <= x1 and y0 <= p[1] <= y1:
            cur.append(p)
        else:
            if len(cur) > 1:
                runs.append(cur)
            cur = []
    if len(cur) > 1:
        runs.append(cur)
    return runs


# ---------------------------------------------------------------- data fetchers
def fetch_contours(frame, ring_ll, halo_m=45.0):
    """1-ft LiDAR contours intersecting the parcel envelope plus a halo."""
    lons = [p[0] for p in ring_ll]
    lats = [p[1] for p in ring_ll]
    dlon = halo_m / frame.mlon
    dlat = halo_m / frame.mlat
    env = {'xmin': min(lons) - dlon, 'ymin': min(lats) - dlat,
           'xmax': max(lons) + dlon, 'ymax': max(lats) + dlat,
           'spatialReference': {'wkid': 4326}}
    d = post(CONTOURS, {'geometry': json.dumps(env), 'geometryType': 'esriGeometryEnvelope',
                        'inSR': 4326, 'outSR': 4326, 'spatialRel': 'esriSpatialRelIntersects',
                        'outFields': 'CONTOUR', 'returnGeometry': 'true', 'f': 'json'})
    out = []
    for f in d.get('features', []):
        elev = f['attributes'].get('CONTOUR')
        for path in f.get('geometry', {}).get('paths', []):
            xy = [frame.fwd(p[0], p[1]) for p in path]
            if len(xy) > 1:
                out.append({'elev_ft': elev, 'xy': xy})
    return out


def fetch_street(frame, ring_ll, want):
    """Centreline of the fronting street, in the local frame."""
    lons = [p[0] for p in ring_ll]
    lats = [p[1] for p in ring_ll]
    cy, cx = sum(lats) / len(lats), sum(lons) / len(lons)
    d = post(ROADS, {'geometry': json.dumps({'x': cx, 'y': cy, 'spatialReference': {'wkid': 4326}}),
                     'geometryType': 'esriGeometryPoint', 'inSR': 4326, 'outSR': 4326,
                     'distance': 1400, 'units': 'esriSRUnit_Foot',
                     'spatialRel': 'esriSpatialRelIntersects',
                     'outFields': 'Full_Name,StreetName', 'returnGeometry': 'true', 'f': 'json'})
    cands = []
    for f in d.get('features', []):
        nm = (f['attributes'].get('Full_Name') or f['attributes'].get('StreetName') or '').strip()
        for path in f.get('geometry', {}).get('paths', []):
            xy = [frame.fwd(p[0], p[1]) for p in path]
            if len(xy) > 1:
                cands.append({'name': nm, 'xy': xy})
    named = [c for c in cands if want.upper() in c['name'].upper()]
    pool = named or cands
    # the street whose centreline passes closest to the parcel boundary
    ring = [frame.fwd(p[0], p[1]) for p in ring_ll]
    best, bestd = None, float('inf')
    for c in pool:
        dmin = min(poly_point_dist(p[0], p[1], ring)[0] for p in c['xy'])
        if dmin < bestd:
            best, bestd = c, dmin
    return best, bestd


def fetch_water(frame, ring_ll):
    q = ('[out:json][timeout:120];('
         'way["natural"="water"](29.10,-95.60,29.18,-95.50);'
         'rel["natural"="water"](29.10,-95.60,29.18,-95.50);'
         ');out geom tags;')
    for url in ('https://overpass-api.de/api/interpreter',
                'https://overpass.kumi.systems/api/interpreter'):
        try:
            r = urllib.request.Request(url, data=urllib.parse.urlencode({'data': q}).encode(),
                                       headers=UA)
            d = json.load(urllib.request.urlopen(r, timeout=200))
            break
        except Exception:
            time.sleep(5)
    else:
        return None
    ring = [frame.fwd(p[0], p[1]) for p in ring_ll]
    best = None
    for e in d['elements']:
        t = e.get('tags', {})
        pts = [(g['lon'], g['lat']) for g in e.get('geometry', []) if 'lat' in g]
        for m in e.get('members', []) or []:
            pts += [(g['lon'], g['lat']) for g in (m.get('geometry') or []) if 'lat' in g]
        if len(pts) < 4:
            continue
        xy = [frame.fwd(p[0], p[1]) for p in pts]
        # only keep features within 400 m of the parcel
        dmin = min(poly_point_dist(p[0], p[1], ring)[0] for p in xy)
        if dmin > 400:
            continue
        if best is None or dmin < best['dist']:
            best = {'name': t.get('name'), 'xy': xy, 'dist': dmin}
    return best


def sample_dem(frame, a, b, n=180, over=(12.0, 25.0)):
    """Elevation profile along A->B, extended by `over` metres at each end.
    Returns list of (station_m_from_A, elev_ft)."""
    ux, uy = b[0] - a[0], b[1] - a[1]
    L = math.hypot(ux, uy)
    ux, uy = ux / L, uy / L
    a2 = (a[0] - ux * over[0], a[1] - uy * over[0])
    b2 = (b[0] + ux * over[1], b[1] + uy * over[1])
    ll = [frame.inv(*a2), frame.inv(*b2)]
    line = {'paths': [[[ll[0][0], ll[0][1]], [ll[1][0], ll[1][1]]]],
            'spatialReference': {'wkid': 4326}}
    d = post(DEM, {'geometry': json.dumps(line), 'geometryType': 'esriGeometryPolyline',
                   'sampleCount': n, 'returnFirstValueOnly': 'true',
                   'interpolation': 'RSP_BilinearInterpolation', 'f': 'json'}, timeout=240)
    prof, res = [], set()
    for s in d.get('samples', []):
        if s.get('value') in (None, '', 'NoData'):
            continue
        loc = s['location']
        x, y = frame.fwd(loc['x'], loc['y'])
        st = (x - a[0]) * ux + (y - a[1]) * uy      # station measured from A
        prof.append([round(st, 3), round(float(s['value']) / M_PER_FT, 3)])
        res.add(s.get('resolution'))
    prof.sort()
    return prof, sorted(r for r in res if r is not None), L


def slopes(prof, win=8):
    """Segment slopes on a smoothed profile. win in samples (~1 m spacing => ~8 m baseline)."""
    if len(prof) < win + 2:
        return [], None
    sm = []
    for i in range(len(prof)):
        lo, hi = max(0, i - 2), min(len(prof), i + 3)
        sm.append([prof[i][0], sum(p[1] for p in prof[lo:hi]) / (hi - lo)])
    segs = []
    for i in range(0, len(sm) - win, max(1, win // 2)):
        j = i + win
        run_m = (sm[j][0] - sm[i][0])
        rise_ft = sm[j][1] - sm[i][1]
        if run_m <= 0:
            continue
        rise_m = rise_ft * M_PER_FT
        ang = math.degrees(math.atan2(rise_m, run_m))
        segs.append({'from_m': round(sm[i][0], 1), 'to_m': round(sm[j][0], 1),
                     'from_ft_elev': round(sm[i][1], 2), 'to_ft_elev': round(sm[j][1], 2),
                     'rise_ft': round(rise_ft, 2), 'run_m': round(run_m, 1),
                     'angle_deg': round(ang, 2),
                     'grade_pct': round(100 * rise_m / run_m, 1)})
    steep = max(segs, key=lambda s: abs(s['angle_deg'])) if segs else None
    return segs, steep


def main():
    gj = json.load(open(GEO))
    out = {'generated': '2026-09-11',
           'datum': 'elevations in feet; USGS 3DEP 1 m DEM (metres) converted at 1 ft = 0.3048 m',
           'note': 'local grid in metres, origin at each parcel centroid, +x east +y north',
           'lots': {}}

    for feat in gj['features']:
        k = feat['id']
        prop = feat['properties']
        ring_ll = feat['geometry']['coordinates'][0]
        lat0, lon0 = prop['centroid']
        fr = Frame(lat0, lon0)
        ring = [fr.fwd(p[0], p[1]) for p in ring_ll]
        print("\n=== %s  %s" % (k, prop['listing_name']))

        street, sdist = fetch_street(fr, ring_ll, STREET[k])
        water = fetch_water(fr, ring_ll)
        print("   street: %s (centreline %.1f m off boundary)"
              % (street['name'] if street else '?', sdist))
        print("   water : %s (%.1f m off boundary)"
              % ((water['name'] or 'unnamed'), water['dist']) if water else "   water : none")

        # A = boundary point closest to the street centreline
        A = None
        if street:
            best = (float('inf'), 0, 0)
            for p in street['xy']:
                d, cx, cy = poly_point_dist(p[0], p[1], ring)
                if d < best[0]:
                    best = (d, cx, cy)
            A = (best[1], best[2])
        # B = boundary point closest to the water body
        B = None
        if water:
            best = (float('inf'), 0, 0)
            for p in water['xy']:
                d, cx, cy = poly_point_dist(p[0], p[1], ring)
                if d < best[0]:
                    best = (d, cx, cy)
            B = (best[1], best[2])
        if A is None or B is None:
            print("   !! cannot define transect")
            continue

        prof, resns, Lm = sample_dem(fr, A, B)
        segs, steep = slopes(prof)
        elevs = [p[1] for p in prof]
        # curvature drop across the transect: h = d^2 / 2R
        curv_m = (Lm ** 2) / (2 * R_EARTH)

        contours = fetch_contours(fr, ring_ll)
        cvals = sorted({c['elev_ft'] for c in contours if c['elev_ft'] is not None})
        inside = [c['elev_ft'] for c in contours
                  if any(point_in_ring(p[0], p[1], ring) for p in c['xy'])
                  and c['elev_ft'] is not None]

        print("   transect %.1f m (%.0f ft) A->B ; DEM samples %d at res %s"
              % (Lm, Lm / M_PER_FT, len(prof), resns))
        print("   elevation along transect: %.2f - %.2f ft (relief %.2f ft)"
              % (min(elevs), max(elevs), max(elevs) - min(elevs)))
        if steep:
            print("   steepest %.1f m run: %.2f ft over %.1f m = %.2f deg (%.1f%%)"
                  % (steep['run_m'], steep['rise_ft'], steep['run_m'],
                     steep['angle_deg'], steep['grade_pct']))
        print("   contours fetched %d runs, values %s ; crossing the parcel: %s"
              % (len(contours), cvals, sorted(set(inside))))
        print("   earth-curvature drop over the transect: %.4f m (%.1f mm)"
              % (curv_m, curv_m * 1000))

        out['lots'][k] = {
            'lot': prop['lot'], 'name': prop['listing_name'], 'pid': prop['pid'],
            'origin': [lat0, lon0], 'm_per_deg': [fr.mlat, fr.mlon],
            'ring_m': [[round(x, 2), round(y, 2)] for x, y in ring],
            'street': {'name': street['name'],
                       'xy': [[round(x, 2), round(y, 2)] for x, y in street['xy']],
                       'offset_m': round(sdist, 1)},
            'water': ({'name': water['name'],
                       'xy': [[round(x, 2), round(y, 2)] for x, y in water['xy']],
                       'offset_m': round(water['dist'], 1)} if water else None),
            'A_m': [round(A[0], 2), round(A[1], 2)],
            'B_m': [round(B[0], 2), round(B[1], 2)],
            'transect_len_m': round(Lm, 2), 'transect_len_ft': round(Lm / M_PER_FT, 1),
            'profile': prof, 'dem_resolutions': resns,
            'min_ft': round(min(elevs), 2), 'max_ft': round(max(elevs), 2),
            'relief_ft': round(max(elevs) - min(elevs), 2),
            'segments': segs, 'steepest': steep,
            'curvature_drop_m': round(curv_m, 5),
            'contours': [{'elev_ft': c['elev_ft'],
                          'xy': [[round(x, 2), round(y, 2)] for x, y in c['xy']]}
                         for c in contours],
            'contour_values': cvals,
            'contours_crossing_parcel': sorted(set(inside)),
        }
        time.sleep(1)

    json.dump(out, open(OUT, 'w'), separators=(',', ':'))
    print("\nwrote %s (%.0f kB)" % (OUT, os.path.getsize(OUT) / 1024))


if __name__ == '__main__':
    main()
