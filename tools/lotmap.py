#!/usr/bin/env python3
"""Annotated aerial views of a single lot, from Esri World Imagery.

Renders two figures per lot:

  context — a wide view placing the parcel in the subdivision, with a leader
            arrow and the acreage of record
  close   — a tight view with the *recorded* BCAD boundary drawn on it

Street names come from Brazoria County's own 911 road centreline service, so the
labels are the county's spelling rather than a basemap vendor's. The boundary is
the recorded polygon from data/parcels.geojson — not a hand-drawn outline — which
is the point: a marketing graphic shows you where somebody says the lines are,
this shows you where the county says they are.

    python3 tools/lotmap.py 3

Output: assets/lot-photos/lot<N>-gal-1.jpg  (context)
        assets/lot-photos/lot<N>-gal-2.jpg  (close)
"""
import json
import math
import os
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor

from PIL import Image, ImageDraw

from satmap import CACHE, ORIGIN, R, fetch, font, merc, res, rounded  # noqa: F401

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GEO = os.path.join(ROOT, 'data', 'parcels.geojson')
OUTDIR = os.path.join(ROOT, 'assets', 'lot-photos')

ROADS = ('https://arcgis-web.brazoriacountytx.gov/arcgis/rest/services/'
         'general/Parcels/MapServer/2/query')
UA = {'User-Agent': '4lots-feasibility-research/1.0'}

RED = (220, 30, 24)
OUT_H = 620                 # printed at 48 mm tall => 328 dpi
SUPER = 2                   # render at 2x, then reduce
ASPECT = 1.50               # w/h — keeps a pair inside the 180 mm column

# Which roads to label, and at which view. Anything not listed is left unlabelled
# rather than crowding the frame.
LABEL_CTX = {'SH 35', 'JIMMY PHILLIPS BLVD', 'BROKEN ARROW TRL', 'WAGON WHEEL TRL',
             'STAGECOACH TRL', 'CAMPFIRE TRL', 'BRANDING IRON TRL', 'RODEO TRL',
             'CATTLE DRIVE TRL', 'TURNING BAYOU TRL'}
LABEL_CLOSE = {'SH 35', 'BROKEN ARROW TRL', 'JIMMY PHILLIPS BLVD'}

VIEWS = {                   # span across the frame, in ground feet, and zoom
    'context': (2600, 18),
    'close':   (1100, 19),
}


def parcel(lot_n):
    g = json.load(open(GEO))
    for f in g['features']:
        if f['properties']['lot'] == lot_n:
            ring = f['geometry']['coordinates'][0]
            if isinstance(ring[0][0], list):
                ring = ring[0]
            return f['properties'], ring
    raise SystemExit('no lot %s in %s' % (lot_n, GEO))


def roads(lon0, lat0, half_deg):
    q = ('?geometry=%%7B%%22xmin%%22%%3A%.6f%%2C%%22ymin%%22%%3A%.6f%%2C'
         '%%22xmax%%22%%3A%.6f%%2C%%22ymax%%22%%3A%.6f%%7D'
         '&geometryType=esriGeometryEnvelope&inSR=4326'
         '&spatialRel=esriSpatialRelIntersects&outFields=Full_Name'
         '&returnGeometry=true&outSR=4326&f=json'
         % (lon0 - half_deg * 1.6, lat0 - half_deg, lon0 + half_deg * 1.6, lat0 + half_deg))
    try:
        req = urllib.request.Request(ROADS + q, headers=UA)
        d = json.load(urllib.request.urlopen(req, timeout=90))
    except Exception as e:                                   # labels are a nicety
        print('  roads unavailable (%s) — rendering without street labels' % e)
        return []
    out = []
    for f in d.get('features', []):
        nm = (f['attributes'].get('Full_Name') or '').strip().upper()
        for path in f['geometry'].get('paths', []):
            if nm and len(path) > 1:
                out.append((nm, path))
    return out


def stitch(cx, cy, pw, ph, z):
    """Mercator-centred crop of the Esri tile mosaic at zoom z."""
    m = res(z)
    x0 = (cx + ORIGIN / 2) / m - pw / 2.0
    y0 = (ORIGIN / 2 - cy) / m - ph / 2.0
    tx0, ty0 = int(x0 // 256), int(y0 // 256)
    tx1, ty1 = int((x0 + pw) // 256), int((y0 + ph) // 256)
    jobs = [(z, x, y) for x in range(tx0, tx1 + 1) for y in range(ty0, ty1 + 1)]
    canvas = Image.new('RGB', ((tx1 - tx0 + 1) * 256, (ty1 - ty0 + 1) * 256), (32, 40, 32))
    got = 0
    with ThreadPoolExecutor(max_workers=12) as ex:
        for x, y, im in ex.map(fetch, jobs):
            if im is not None:
                canvas.paste(im, ((x - tx0) * 256, (y - ty0) * 256))
                got += 1
    print('  z%d  %d/%d tiles' % (z, got, len(jobs)))
    ox, oy = x0 - tx0 * 256, y0 - ty0 * 256
    crop = canvas.crop((int(round(ox)), int(round(oy)),
                        int(round(ox)) + pw, int(round(oy)) + ph))
    return crop, x0, y0, m


def rot_text(base, xy, text, ang, fnt, fill=(255, 255, 255)):
    """Text drawn along a road, with a dark halo so it reads over imagery."""
    pad = 6
    tmp = Image.new('RGBA', (10, 10))
    w, h = ImageDraw.Draw(tmp).textbbox((0, 0), text, font=fnt)[2:]
    lay = Image.new('RGBA', (w + pad * 2, h + pad * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.text((pad, pad), text, font=fnt, fill=(0, 0, 0, 210),
           stroke_width=max(3, fnt.size // 4), stroke_fill=(0, 0, 0, 210))
    d.text((pad, pad), text, font=fnt, fill=fill + (255,))
    while ang > 90:
        ang -= 180
    while ang < -90:
        ang += 180
    lay = lay.rotate(ang, expand=True, resample=Image.BICUBIC)
    base.alpha_composite(lay, (int(xy[0] - lay.width / 2), int(xy[1] - lay.height / 2)))


def _finish(img, ov, od, pw, ph, m, lat0, mode, lot_n):
    """Scale bar, attribution, reduce to print size, write."""
    ft = 200 if mode == 'close' else 500
    fs = font(max(11, pw // 78), bold=True)
    bar = (ft * 0.3048) / math.cos(math.radians(lat0)) / m
    sx, sy = 14, ph - 20
    od.line([(sx, sy), (sx + bar, sy)], fill=(255, 255, 255, 245), width=4)
    for e in (sx, sx + bar):
        od.line([(e, sy - 6), (e, sy + 6)], fill=(255, 255, 255, 245), width=4)
    od.text((sx, sy - 20), '%d ft' % ft, font=fs, fill=(255, 255, 255, 245),
            stroke_width=3, stroke_fill=(0, 0, 0, 200))
    cr = 'Imagery \u00a9 Esri, Maxar, Earthstar Geographics \u00b7 boundary: BCAD record'
    cw = od.textbbox((0, 0), cr, font=fs)[2]
    od.text((pw - cw - 10, ph - 18), cr, font=fs, fill=(255, 255, 255, 220),
            stroke_width=3, stroke_fill=(0, 0, 0, 200))

    out = Image.alpha_composite(img, ov).convert('RGB')
    out = out.resize((int(round(OUT_H * ASPECT)), OUT_H), Image.LANCZOS)
    os.makedirs(OUTDIR, exist_ok=True)
    name = 'lot%d-gal-%d.jpg' % (lot_n, 1 if mode == 'context' else 2)
    out.save(os.path.join(OUTDIR, name), quality=93, optimize=True)
    print('  wrote %s  %dx%d' % (name, out.width, out.height))


def render(lot_n, mode):
    props, ring = parcel(lot_n)
    span_ft, z = VIEWS[mode]
    lat0, lon0 = props['centroid']
    cx, cy = merc(lon0, lat0)

    ground_m = span_ft * 0.3048
    merc_w = ground_m / math.cos(math.radians(lat0))     # mercator metres across
    pw = int(round(merc_w / res(z)))
    ph = int(round(pw / ASPECT))

    img, x0, y0, m = stitch(cx, cy, pw, ph, z)
    img = img.convert('RGBA')

    def to_px(lon, lat):
        mx, my = merc(lon, lat)
        return ((mx + ORIGIN / 2) / m - x0, (ORIGIN / 2 - my) / m - y0)

    ov = Image.new('RGBA', img.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(ov)

    # street labels first, so the parcel graphic sits on top of them
    want = LABEL_CTX if mode == 'context' else LABEL_CLOSE
    half_deg = (merc_w / 2) / 110540.0 * 1.15
    done = {}
    fnt = font(max(13, pw // 60), bold=True)
    for nm, path in roads(lon0, lat0, half_deg):
        if nm not in want:
            continue
        pts = [to_px(x, y) for x, y in path]
        vis = [p for p in pts if -60 < p[0] < pw + 60 and -60 < p[1] < ph + 60]
        if len(vis) < 2:
            continue
        # longest visible run gets the label, one label per name
        a, b = vis[0], vis[-1]
        length = math.hypot(b[0] - a[0], b[1] - a[1])
        if length < pw * 0.10 or done.get(nm, 0) >= length:
            continue
        done[nm] = length
        mid = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
        ang = -math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))
        rot_text(ov, mid, nm.title().replace('Trl', 'Trail').replace('Sh 35', 'SH 35'),
                 ang, fnt)

    pts = [to_px(x, y) for x, y in ring]
    if mode == 'close':
        od.polygon(pts, fill=RED + (46,))
        od.line(pts + [pts[0]], fill=RED + (255,), width=max(4, pw // 190),
                joint='curve')
        for p in pts:                                        # vertex ticks
            r = max(3, pw // 380)
            od.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], fill=RED + (255,))
    else:
        od.line(pts + [pts[0]], fill=RED + (255,), width=max(3, pw // 260),
                joint='curve')

    # Acreage tag with a leader arrow — context view only. On the close view the
    # drawn boundary already says which parcel it is, and an arrow across it just
    # obscures the ground the reader is trying to look at.
    if mode == 'close':
        return _finish(img, ov, od, pw, ph, m, lat0, mode, lot_n)

    fb = font(max(15, pw // 42), bold=True)
    txt = '%.2f ac' % props['acres_of_record']
    tw, th = od.textbbox((0, 0), txt, font=fb)[2:]
    px, py = to_px(lon0, lat0)
    off = (-(tw + 90), -(ph * 0.26)) if mode == 'context' else (-(tw + 80), -(ph * 0.30))
    bx, by = px + off[0], py + off[1]
    bx = min(max(bx, 8), pw - tw - 26)
    by = min(max(by, 8), ph - th - 22)
    box = [bx, by, bx + tw + 18, by + th + 12]
    rounded(od, box, 6, fill=RED + (238,), outline=(255, 255, 255, 235), width=2)
    od.text((bx + 9, by + 5), txt, font=fb, fill=(255, 255, 255, 255))
    ax, ay = box[2], (box[1] + box[3]) / 2
    od.line([(ax, ay), (px, py)], fill=(255, 255, 255, 245), width=max(3, pw // 300))
    ang = math.atan2(py - ay, px - ax)
    hl = max(10, pw // 90)
    od.polygon([(px, py),
                (px - hl * math.cos(ang - 0.42), py - hl * math.sin(ang - 0.42)),
                (px - hl * math.cos(ang + 0.42), py - hl * math.sin(ang + 0.42))],
               fill=(255, 255, 255, 245))

    return _finish(img, ov, od, pw, ph, m, lat0, mode, lot_n)


if __name__ == '__main__':
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    print('lot %d' % n)
    for mode in ('context', 'close'):
        render(n, mode)
