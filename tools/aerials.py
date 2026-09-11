#!/usr/bin/env python3
"""Generate the lot imagery from USGS NAIP aerial photography (public domain, 30 cm).

Three images per lot, written into assets/photos/ where the artifact picks them up:

  lotN-1.jpg  the parcel at close range with its recorded boundary and the A-B section line
  lotN-2.jpg  the water frontage, centred on point B
  lotN-3.jpg  the neighbourhood context, with the parcel outlined

    python3 tools/aerials.py

Source: USGS NAIPPlus ImageServer, imagery.nationalmap.gov. NAIP is US Department of
Agriculture aerial photography in the public domain.
"""
import json
import math
import os
import urllib.parse
import urllib.request

from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTDIR = os.path.join(ROOT, 'assets', 'photos')
NAIP = "https://imagery.nationalmap.gov/arcgis/rest/services/USGSNAIPPlus/ImageServer/exportImage"
UA = {'User-Agent': '4lots-feasibility-research/1.0'}
R = 6378137.0

INK = (18, 30, 36)
BOUND = (255, 214, 64)
SECT = (255, 74, 60)
WHITE = (255, 255, 255)


def to3857(lon, lat):
    x = R * math.radians(lon)
    y = R * math.log(math.tan(math.pi / 4 + math.radians(lat) / 2))
    return x, y


def fetch(cx, cy, half_w, aspect=4 / 3.0, px=1600):
    """Export a NAIP image centred on a web-mercator point, half_w metres either side."""
    half_h = half_w / aspect
    bbox = (cx - half_w, cy - half_h, cx + half_w, cy + half_h)
    q = urllib.parse.urlencode({
        'bbox': '%f,%f,%f,%f' % bbox, 'bboxSR': 3857, 'imageSR': 3857,
        'size': '%d,%d' % (px, int(px / aspect)),
        'format': 'jpg', 'interpolation': 'RSP_BilinearInterpolation', 'f': 'image'})
    req = urllib.request.Request(NAIP + '?' + q, headers=UA)
    data = urllib.request.urlopen(req, timeout=180).read()
    tmp = os.path.join(OUTDIR, '.tmp.jpg')
    open(tmp, 'wb').write(data)
    im = Image.open(tmp).convert('RGB')
    os.remove(tmp)
    return im, bbox


def mapper(bbox, size):
    x0, y0, x1, y1 = bbox
    w, h = size

    def f(x, y):
        return ((x - x0) / (x1 - x0) * w, (y1 - y) / (y1 - y0) * h)
    return f


def outline(dr, pts, colour, width, shadow=True):
    if shadow:
        dr.line(pts + [pts[0]], fill=(0, 0, 0), width=width + 3, joint='curve')
    dr.line(pts + [pts[0]], fill=colour, width=width, joint='curve')


_FONTS = {}


def font(size):
    if size in _FONTS:
        return _FONTS[size]
    from PIL import ImageFont
    for path in ("/usr/share/fonts/dejavu-sans-fonts/DejaVuSans-Bold.ttf",
                 "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                 "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf"):
        try:
            _FONTS[size] = ImageFont.truetype(path, size)
            return _FONTS[size]
        except Exception:
            continue
    _FONTS[size] = ImageFont.load_default()
    return _FONTS[size]


def label(dr, xy, text, size=34, pad=10, bg=(18, 30, 36), fg=WHITE):
    fnt = font(size)
    x, y = xy
    box = dr.textbbox((x, y), text, font=fnt)
    if bg is not None:
        dr.rectangle([box[0] - pad, box[1] - pad, box[2] + pad, box[3] + pad], fill=bg)
    dr.text((x, y), text, font=fnt, fill=fg)


def scalebar(dr, size, mpp, metres=30):
    w, h = size
    px = metres / mpp
    if px > w * 0.45:
        metres, px = 10, 10 / mpp
    x0 = w - px - 40
    y0 = h - 46
    dr.rectangle([x0 - 8, y0 - 26, x0 + px + 8, y0 + 18], fill=(0, 0, 0, 255))
    dr.rectangle([x0, y0, x0 + px / 2, y0 + 9], fill=WHITE)
    dr.rectangle([x0 + px / 2, y0, x0 + px, y0 + 9], fill=(120, 120, 120))
    label(dr, (x0, y0 - 24), "%d m / %d ft" % (metres, round(metres / 0.3048)),
          size=20, pad=4, bg=(0, 0, 0))


def main():
    os.makedirs(OUTDIR, exist_ok=True)
    gj = json.load(open(os.path.join(ROOT, 'data', 'parcels.geojson')))
    ter = json.load(open(os.path.join(ROOT, 'data', 'terrain.json')))['lots']

    for feat in gj['features']:
        k = feat['id']
        p = feat['properties']
        n = p['lot']
        ring_ll = feat['geometry']['coordinates'][0]
        ring = [to3857(lo, la) for lo, la in ring_ll]
        xs = [q[0] for q in ring]
        ys = [q[1] for q in ring]
        cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
        extent = max(max(xs) - min(xs), (max(ys) - min(ys)) * 4 / 3.0)

        # A and B in lat/lon, from the terrain transect
        t = ter[k]
        lat0, lon0 = t['origin']
        mlat, mlon = t['m_per_deg']

        def local_to_3857(xy):
            lon = lon0 + xy[0] / mlon
            lat = lat0 + xy[1] / mlat
            return to3857(lon, lat)

        A = local_to_3857(t['A_m'])
        B = local_to_3857(t['B_m'])

        jobs = [
            (1, cx, cy, extent * 0.62, 'the parcel and its recorded boundary', True, True, 30),
            (2, B[0], B[1], 45.0, 'the water frontage at B', True, True, 20),
            (3, cx, cy, extent * 2.1, 'neighbourhood context', True, False, 100),
        ]
        for idx, mx, my, half, cap, draw_bound, draw_sect, sb in jobs:
            im, bbox = fetch(mx, my, half)
            dr = ImageDraw.Draw(im)
            f = mapper(bbox, im.size)
            if draw_bound:
                outline(dr, [f(*q) for q in ring], BOUND, 6 if idx != 3 else 4)
            if draw_sect:
                a, b = f(*A), f(*B)
                dr.line([a, b], fill=(0, 0, 0), width=8)
                dr.line([a, b], fill=SECT, width=4)
                for pt, tx in ((a, 'A'), (b, 'B')):
                    dr.ellipse([pt[0] - 22, pt[1] - 22, pt[0] + 22, pt[1] + 22],
                               fill=WHITE, outline=SECT, width=5)
                    fnt = font(34)
                    bx = dr.textbbox((0, 0), tx, font=fnt)
                    dr.text((pt[0] - (bx[2] - bx[0]) / 2, pt[1] - (bx[3] - bx[1]) / 2 - bx[1]),
                            tx, font=fnt, fill=SECT)
            mpp = (bbox[2] - bbox[0]) / im.size[0]
            scalebar(dr, im.size, mpp, sb)
            label(dr, (26, 22), "Lot %d · %s" % (n, p['listing_name']), size=32)
            label(dr, (26, 74), cap, size=22, bg=(18, 30, 36))
            label(dr, (26, im.size[1] - 40), "USGS NAIP aerial imagery · public domain",
                  size=18, bg=(0, 0, 0))
            path = os.path.join(OUTDIR, 'lot%d-%d.jpg' % (n, idx))
            im.save(path, quality=86, optimize=True)
            print("  lot%d-%d.jpg  %dx%d  %.2f m/px  %.0f kB  — %s"
                  % (n, idx, im.size[0], im.size[1], mpp,
                     os.path.getsize(path) / 1024, cap))


if __name__ == '__main__':
    main()
