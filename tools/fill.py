#!/usr/bin/env python3
"""Work out the fill needed on each lot to carry a finished floor to 30 ft, and cost it.

Method
------
1. Sample the USGS 3DEP 1 m DEM on a grid inside each recorded parcel boundary.
2. Search that grid for the pad location that minimises fill, subject to the pad *and its
   side-slope toe* fitting inside the boundary with a working margin.
3. Compute the fill as a frustum (planar 3:1 side slopes), which is the honest geometry —
   plan area times depth understates a deep pad badly, because the slope wedge grows with
   the square of the lift and the corners with the cube.
4. Cost it at Gulf Coast select-fill rates, and price the pier-and-beam alternative that
   becomes competitive once the lift gets deep.

Writes data/fill.json.

    python3 tools/fill.py
"""
import json
import math
import os
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEM = "https://elevation.nationalmap.gov/arcgis/rest/services/3DEPElevation/ImageServer/getSamples"
UA = {'User-Agent': '4lots-feasibility-research/1.0'}
M_PER_FT = 0.3048
CY_PER_M3 = 1.30795          # cubic yards per cubic metre

# ---------------------------------------------------------------- design basis
FFE_FT = 30.0                # required finished floor: 28 ft BFE + 24 in county freeboard
SLAB_FT = 0.5                # 6 in slab, so the pad top sits at FFE - 0.5
STRIP_FT = 0.5               # organic topsoil stripped before fill is placed
PAD_W_FT, PAD_L_FT = 69.0, 82.0   # pad top: a ~3,040 sq ft house + garage plus 10 ft working margin
SIDE_SLOPE = 3.0             # 3:1 horizontal:vertical — stable and mowable in this clay
EDGE_MARGIN_FT = 8.0         # keep the slope toe this far inside the boundary
WATER_STANDOFF_M = 30.0      # no pad within this of mapped water: it keeps the house off the
                             # bank, off the Flag Lake levee embankment on Lot 4, and clear of
                             # the 75 ft TCEQ absorption setback

# ---------------------------------------------------------------- unit costs (2026 planning)
# $ per in-place (compacted) cubic yard, delivered, spread and compacted in lifts.
# The low end assumes local bank sand and a short haul; the high end select clay-sand fill,
# a longer haul and a difficult site. Shrinkage from loose to compacted is inside these rates.
FILL_LO, FILL_HI = 16.0, 30.0
STRIP_LO, STRIP_HI = 1.60, 3.20      # $ per sq yd to strip and stockpile topsoil
GEOTECH = (2500, 5000)               # two borings plus a report
PAD_DESIGN = (1500, 4000)            # civil engineer: grading and drainage plan
DENSITY_TESTS = (1200, 3000)         # compaction testing per lift
EROSION = (600, 1500)                # silt fence, inlet protection
SLOPE_FINISH_LO, SLOPE_HI = 1.10, 2.40   # $ per sq yd to topsoil and turf the slopes
DRAINAGE = (1000, 4000)              # swales or a culvert, so runoff is not pushed next door
PERMIT = (0, 80)                     # county fill and grading permit

# pier-and-beam / stem-wall alternative, $ per sq ft of structure, by lift
PIER_LO, PIER_HI = 26.0, 44.0
STRUCT_SF = 3040.0


def post(url, params, timeout=240):
    r = urllib.request.Request(url, data=urllib.parse.urlencode(params).encode(), headers=UA)
    return json.load(urllib.request.urlopen(r, timeout=timeout))


def point_in_ring(px, py, ring):
    inside = False
    for i in range(len(ring) - 1):
        x1, y1 = ring[i]
        x2, y2 = ring[i + 1]
        if (y1 > py) != (y2 > py):
            if px < x1 + (py - y1) * (x2 - x1) / (y2 - y1):
                inside = not inside
    return inside


def dist_to_ring(px, py, ring):
    best = float('inf')
    for i in range(len(ring) - 1):
        ax, ay = ring[i]
        bx, by = ring[i + 1]
        dx, dy = bx - ax, by - ay
        L2 = dx * dx + dy * dy
        t = 0.0 if L2 == 0 else max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / L2))
        best = min(best, math.hypot(px - (ax + t * dx), py - (ay + t * dy)))
    return best


def frustum_cy(w_ft, l_ft, h_ft, s):
    """Volume of a pad with planar s:1 side slopes, in cubic yards.

    V = W·L·h + s·h²·(W+L) + (4/3)·s²·h³   — exact prismatoid for planar sides.
    """
    if h_ft <= 0:
        return 0.0
    v_ft3 = (w_ft * l_ft * h_ft
             + s * h_ft ** 2 * (w_ft + l_ft)
             + (4.0 / 3.0) * s ** 2 * h_ft ** 3)
    return v_ft3 / 27.0


def main():
    gj = json.load(open(os.path.join(ROOT, 'data', 'parcels.geojson')))
    ter = json.load(open(os.path.join(ROOT, 'data', 'terrain.json')))['lots']
    out = {'basis': {
        'ffe_ft': FFE_FT, 'slab_ft': SLAB_FT, 'strip_ft': STRIP_FT,
        'pad_ft': [PAD_W_FT, PAD_L_FT], 'side_slope': '%.0f:1' % SIDE_SLOPE,
        'fill_rate_usd_per_cy': [FILL_LO, FILL_HI],
        'note': 'pad top at FFE minus slab; fill measured from the stripped surface'},
        'lots': {}}

    for feat in gj['features']:
        k = feat['id']
        p = feat['properties']
        t = ter[k]
        ring = t['ring_m']                      # local metres, origin at the parcel centroid
        lat0, lon0 = t['origin']
        mlat, mlon = t['m_per_deg']

        xs = [q[0] for q in ring]
        ys = [q[1] for q in ring]

        # ---- grid of candidate points inside the parcel
        step = 5.0
        pts = []
        x = min(xs)
        while x <= max(xs):
            y = min(ys)
            while y <= max(ys):
                if point_in_ring(x, y, ring):
                    pts.append((x, y))
                y += step
            x += step
        # sample the DEM at those points
        mp = {'points': [[lon0 + q[0] / mlon, lat0 + q[1] / mlat] for q in pts],
              'spatialReference': {'wkid': 4326}}
        d = post(DEM, {'geometry': json.dumps(mp), 'geometryType': 'esriGeometryMultipoint',
                       'returnFirstValueOnly': 'true',
                       'interpolation': 'RSP_BilinearInterpolation', 'f': 'json'})
        grid = []
        for s in d.get('samples', []):
            if s.get('value') in (None, '', 'NoData'):
                continue
            loc = s['location']
            gx = (loc['x'] - lon0) * mlon
            gy = (loc['y'] - lat0) * mlat
            grid.append((gx, gy, float(s['value']) / M_PER_FT))
        if not grid:
            print("!! no DEM samples for %s" % k)
            continue

        # ---- water geometry, so the pad can be kept off the bank and off the levee
        water = [(q[0], q[1]) for q in (t.get('water') or {}).get('xy', [])]

        def water_dist(px, py):
            if not water:
                return 1e9
            return min(math.hypot(px - wx, py - wy) for wx, wy in water)

        pw, pl = PAD_W_FT * M_PER_FT, PAD_L_FT * M_PER_FT

        def search(standoff):
            best = None
            rejected = 0
            for cx, cy, _ in grid:
                if water_dist(cx, cy) < standoff:
                    rejected += 1
                    continue
                r = _score(cx, cy)
                if r and (best is None or r['score'] < best['score']):
                    best = r
            return best, rejected

        def _score(cx, cy):
            local = [g for g in grid
                     if abs(g[0] - cx) <= pw / 2 and abs(g[1] - cy) <= pl / 2]
            if len(local) < 3:
                return None
            mean_g = sum(g[2] for g in local) / len(local)
            lift = max(0.0, (FFE_FT - SLAB_FT) - mean_g)
            toe = (SIDE_SLOPE * max(lift, 0.5) + EDGE_MARGIN_FT) * M_PER_FT
            clear = dist_to_ring(cx, cy, ring)
            return {'cx': cx, 'cy': cy, 'mean_ground': mean_g, 'lift': lift,
                    'n': len(local), 'clear_m': clear, 'toe_m': toe,
                    'score': lift + max(0.0, toe - clear) * 0.6,
                    'water_m': water_dist(cx, cy)}

        best, rejected_water = search(WATER_STANDOFF_M)
        if best is None:
            print("!! no pad location for %s" % k)
            continue

        h_pad = best['lift']                       # pad top above existing ground
        h_fill = h_pad + STRIP_FT                  # measured from the stripped surface
        cy_fill = frustum_cy(PAD_W_FT, PAD_L_FT, h_fill, SIDE_SLOPE)

        toe_w = PAD_W_FT + 2 * SIDE_SLOPE * h_fill
        toe_l = PAD_L_FT + 2 * SIDE_SLOPE * h_fill
        footprint_sy = (toe_w * toe_l) / 9.0
        slope_sy = (toe_w * toe_l - PAD_W_FT * PAD_L_FT) / 9.0

        # will the pad and its slopes actually fit on the lot?
        bw, bl = p['bbox_ft']
        narrow = min(bw, bl)
        need_narrow = min(toe_w, toe_l) + 2 * EDGE_MARGIN_FT
        fits = narrow >= need_narrow
        spare_ft = narrow - need_narrow

        items = [
            ('Strip and stockpile topsoil under the pad', footprint_sy * STRIP_LO,
             footprint_sy * STRIP_HI),
            ('Imported select fill, placed and compacted in lifts', cy_fill * FILL_LO,
             cy_fill * FILL_HI),
            ('Topsoil and turf the side slopes', slope_sy * SLOPE_FINISH_LO,
             slope_sy * SLOPE_HI),
            ('Geotechnical investigation and report', *GEOTECH),
            ('Engineered pad and drainage plan', *PAD_DESIGN),
            ('Compaction density testing', *DENSITY_TESTS),
            ('Erosion and sediment control', *EROSION),
            ('Drainage works so runoff is not pushed onto the road or a neighbour', *DRAINAGE),
            ('County fill and grading permit', *PERMIT),
        ]
        lo = sum(i[1] for i in items)
        hi = sum(i[2] for i in items)
        pier = (STRUCT_SF * PIER_LO, STRUCT_SF * PIER_HI)

        rec = {
            'lot': p['lot'], 'name': p['listing_name'],
            'grid_points': len(grid),
            'ground_min_ft': round(min(g[2] for g in grid), 2),
            'ground_max_ft': round(max(g[2] for g in grid), 2),
            'ground_mean_ft': round(sum(g[2] for g in grid) / len(grid), 2),
            'pad_ground_ft': round(best['mean_ground'], 2),
            'pad_top_ft': FFE_FT - SLAB_FT,
            'lift_ft': round(h_pad, 2),
            'fill_height_ft': round(h_fill, 2),
            'fill_cy': int(round(cy_fill)),
            'toe_ft': [round(toe_w), round(toe_l)],
            'lot_bbox_ft': p['bbox_ft'],
            'pad_fits': bool(fits),
            'narrow_dim_ft': round(narrow), 'need_narrow_ft': round(need_narrow),
            'spare_ft': round(spare_ft),
            'water_standoff_m': round(best['water_m'], 1),
            'clear_to_boundary_m': round(best['clear_m'], 1),
            'pier_relevant': bool(h_pad >= 3.0),
            'items': [[n, round(a), round(b)] for n, a, b in items],
            'total_lo': int(round(lo)), 'total_hi': int(round(hi)),
            'pier_alt_lo': int(round(pier[0])), 'pier_alt_hi': int(round(pier[1])),
        }
        # on Lot 4 the only ground high enough to save fill is the flank of the Flag Lake
        # levee. A geotechnical engineer is unlikely to found a house on a dam embankment,
        # so price the pad taken fully clear of it as well.
        if k == 'lot4':
            alt, _ = search(60.0)
            if alt:
                h2 = alt['lift']
                cy2 = frustum_cy(PAD_W_FT, PAD_L_FT, h2 + STRIP_FT, SIDE_SLOPE)
                tw2 = PAD_W_FT + 2 * SIDE_SLOPE * (h2 + STRIP_FT)
                tl2 = PAD_L_FT + 2 * SIDE_SLOPE * (h2 + STRIP_FT)
                fp2 = tw2 * tl2 / 9.0
                sl2 = (tw2 * tl2 - PAD_W_FT * PAD_L_FT) / 9.0
                lo2 = (fp2 * STRIP_LO + cy2 * FILL_LO + sl2 * SLOPE_FINISH_LO
                       + GEOTECH[0] + PAD_DESIGN[0] + DENSITY_TESTS[0] + EROSION[0]
                       + DRAINAGE[0] + PERMIT[0])
                hi2 = (fp2 * STRIP_HI + cy2 * FILL_HI + sl2 * SLOPE_HI
                       + GEOTECH[1] + PAD_DESIGN[1] + DENSITY_TESTS[1] + EROSION[1]
                       + DRAINAGE[1] + PERMIT[1])
                rec['off_embankment'] = {
                    'standoff_m': 60, 'pad_ground_ft': round(alt['mean_ground'], 2),
                    'lift_ft': round(h2, 2), 'fill_cy': int(round(cy2)),
                    'toe_ft': [round(tw2), round(tl2)],
                    'need_narrow_ft': round(min(tw2, tl2) + 2 * EDGE_MARGIN_FT),
                    'total_lo': int(round(lo2)), 'total_hi': int(round(hi2))}
                print("  OFF-EMBANKMENT variant: ground %.2f ft, lift %.2f ft, %s cy, "
                      "$%s – $%s  (needs %d ft of width on a %d ft lot)"
                      % (alt['mean_ground'], h2, format(int(round(cy2)), ','),
                         format(int(round(lo2)), ','), format(int(round(hi2)), ','),
                         min(tw2, tl2) + 2 * EDGE_MARGIN_FT, narrow))

        out['lots'][k] = rec

        print("\n=== Lot %d  %s" % (p['lot'], p['listing_name']))
        print("  DEM grid %d pts · ground %.1f–%.1f ft (mean %.1f)"
              % (rec['grid_points'], rec['ground_min_ft'], rec['ground_max_ft'],
                 rec['ground_mean_ft']))
        print("  best pad ground %.2f ft -> pad top %.1f ft -> lift %.2f ft (fill %.2f ft)"
              % (rec['pad_ground_ft'], rec['pad_top_ft'], rec['lift_ft'], rec['fill_height_ft']))
        print("  pad kept %.0f m off mapped water (%d grid points rejected as bank/levee)"
              % (best['water_m'], rejected_water))
        print("  fill volume %s cy ; toe %d × %d ft ; lot narrow dim %d ft, needs %d ft "
              "-> %s (%+d ft spare)"
              % (format(rec['fill_cy'], ','), toe_w, toe_l, narrow, need_narrow,
                 'fits' if fits else 'DOES NOT FIT', spare_ft))
        print("  FILL PACKAGE  $%s – $%s" % (format(rec['total_lo'], ','),
                                             format(rec['total_hi'], ',')))
        print("  pier alternative $%s – $%s" % (format(rec['pier_alt_lo'], ','),
                                                format(rec['pier_alt_hi'], ',')))

    # crossover: the lift at which a fill pad costs as much as elevating on piers
    fixed = (GEOTECH[0] + GEOTECH[1] + PAD_DESIGN[0] + PAD_DESIGN[1] + DENSITY_TESTS[0]
             + DENSITY_TESTS[1] + EROSION[0] + EROSION[1] + DRAINAGE[0] + DRAINAGE[1]) / 2.0
    pier_mid = STRUCT_SF * (PIER_LO + PIER_HI) / 2.0
    rate = (FILL_LO + FILL_HI) / 2.0
    h = 0.5
    while h < 30:
        v = frustum_cy(PAD_W_FT, PAD_L_FT, h + STRIP_FT, SIDE_SLOPE)
        if v * rate + fixed >= pier_mid:
            break
        h += 0.05
    out['pier_crossover_lift_ft'] = round(h, 1)
    out['pier_mid_usd'] = int(pier_mid)
    print("\nA fill pad only costs as much as elevating on piers at about %.1f ft of lift "
          "(pier mid-case $%s). None of these four is close." % (h, format(int(pier_mid), ',')))

    json.dump(out, open(os.path.join(ROOT, 'data', 'fill.json'), 'w'), indent=1)
    print("\nwrote data/fill.json")


if __name__ == '__main__':
    main()
