#!/usr/bin/env python3
"""Compose the full-page satellite plate showing all five parcels.

Stitches Esri World Imagery tiles at zoom 18 over an extent that covers every
parcel, draws the recorded boundaries, a numbered map pin at each centroid and a
name tag with a leader line, then downsamples to print resolution.

Output: assets/satellite/all-lots-satellite.jpg  (portrait, ~300 dpi at 180 mm)

Google's own tiles are deliberately not used: the Static Maps API needs a key and
scraping the tile endpoints breaches its terms. Esri World Imagery is the same
basemap the interactive map in the artifact already uses.

    python3 tools/satmap.py
"""
import io
import json
import math
import os
import urllib.request
from concurrent.futures import ThreadPoolExecutor

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GEO = os.path.join(ROOT, 'data', 'parcels.geojson')
OUTDIR = os.path.join(ROOT, 'assets', 'satellite')
OUT = os.path.join(OUTDIR, 'all-lots-satellite.jpg')

TILES = ('https://server.arcgisonline.com/ArcGIS/rest/services/'
         'World_Imagery/MapServer/tile/{z}/{y}/{x}')
UA = {'User-Agent': '4lots-feasibility-research/1.0'}

Z = 18                      # fetch zoom — supersampled, then reduced
TARGET_W = 2400             # final pixel width  (~340 dpi at 180 mm)
PAGE_ASPECT = 0.715         # w/h of the printable image box on an A4 page
PAD_M = 70                  # mercator-metre padding around the parcels

R = 6378137.0
ORIGIN = 2 * math.pi * R    # 40075016.686
FONT_DIRS = ['/usr/share/fonts', '/usr/local/share/fonts']

COL = {1: (15, 118, 110), 2: (28, 59, 168), 3: (21, 96, 47),
       4: (169, 31, 20), 5: (91, 33, 166)}

# Label placement, tuned by eye against the plate: (dx, dy) from the pin tip in
# final-image pixels, and which corner of the tag the leader attaches to.
LABEL = {
    1: (165, -40, 'left'),
    2: (-165, -55, 'right'),
    3: (150, -95, 'left'),
    4: (-185, 45, 'right'),
    5: (165, 105, 'left'),
}


def merc(lon, lat):
    x = R * math.radians(lon)
    y = R * math.log(math.tan(math.pi / 4 + math.radians(lat) / 2))
    return x, y


def res(z):
    """Mercator metres per pixel."""
    return ORIGIN / (256 * 2 ** z)


def font(size, bold=False):
    names = (['DejaVuSans-Bold.ttf', 'LiberationSans-Bold.ttf'] if bold
             else ['DejaVuSans.ttf', 'LiberationSans-Regular.ttf'])
    for d in FONT_DIRS:
        for root, _, files in os.walk(d):
            for n in names:
                if n in files:
                    return ImageFont.truetype(os.path.join(root, n), size)
    return ImageFont.load_default()


CACHE = os.path.join(ROOT, '.tilecache')


def fetch(args):
    z, x, y = args
    cp = os.path.join(CACHE, '%d_%d_%d.jpg' % (z, x, y))
    if os.path.exists(cp):
        try:
            return (x, y, Image.open(cp).convert('RGB'))
        except Exception:
            pass
    url = TILES.format(z=z, x=x, y=y)
    for _ in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA),
                                        timeout=60) as r:
                raw = r.read()
            im = Image.open(io.BytesIO(raw)).convert('RGB')
            os.makedirs(CACHE, exist_ok=True)
            im.save(cp, 'JPEG', quality=95)
            return (x, y, im)
        except Exception:
            pass
    return (x, y, None)


def rounded(draw, box, r, fill=None, outline=None, width=1):
    draw.rounded_rectangle(box, radius=r, fill=fill, outline=outline, width=width)


def main():
    os.makedirs(OUTDIR, exist_ok=True)
    gj = json.load(open(GEO))
    feats = sorted(gj['features'], key=lambda f: f['properties']['lot'])

    # ---------------------------------------------------------------- extent
    xs, ys = [], []
    for f in feats:
        for lon, lat in f['geometry']['coordinates'][0]:
            x, y = merc(lon, lat)
            xs.append(x)
            ys.append(y)
    x0, x1 = min(xs) - PAD_M, max(xs) + PAD_M
    y0, y1 = min(ys) - PAD_M, max(ys) + PAD_M
    w, h = x1 - x0, y1 - y0
    # grow to the page aspect, keeping the parcels centred
    if w / h > PAGE_ASPECT:
        nh = w / PAGE_ASPECT
        cy = (y0 + y1) / 2
        y0, y1 = cy - nh / 2, cy + nh / 2
    else:
        nw = h * PAGE_ASPECT
        cx = (x0 + x1) / 2
        x0, x1 = cx - nw / 2, cx + nw / 2
    w, h = x1 - x0, y1 - y0
    print('extent %.0f x %.0f mercator m  (aspect %.3f)' % (w, h, w / h))

    # ---------------------------------------------------------------- tiles
    r = res(Z)
    px0 = (x0 + ORIGIN / 2) / r
    px1 = (x1 + ORIGIN / 2) / r
    py0 = (ORIGIN / 2 - y1) / r          # note: y flips
    py1 = (ORIGIN / 2 - y0) / r
    tx0, tx1 = int(px0 // 256), int(px1 // 256)
    ty0, ty1 = int(py0 // 256), int(py1 // 256)
    jobs = [(Z, x, y) for x in range(tx0, tx1 + 1) for y in range(ty0, ty1 + 1)]
    print('fetching %d tiles at z%d …' % (len(jobs), Z))

    canvas = Image.new('RGB', ((tx1 - tx0 + 1) * 256, (ty1 - ty0 + 1) * 256), (32, 40, 44))
    ok = 0
    with ThreadPoolExecutor(max_workers=12) as ex:
        for x, y, im in ex.map(fetch, jobs):
            if im is None:
                continue
            canvas.paste(im, ((x - tx0) * 256, (y - ty0) * 256))
            ok += 1
    print('  %d/%d tiles' % (ok, len(jobs)))
    if ok < len(jobs) * 0.9:
        raise SystemExit('too many tiles failed — refusing to publish a holed plate')

    # crop to the exact extent, then reduce to print size
    cx0 = px0 - tx0 * 256
    cy0 = py0 - ty0 * 256
    big = canvas.crop((int(cx0), int(cy0),
                       int(cx0 + (px1 - px0)), int(cy0 + (py1 - py0))))
    scale = TARGET_W / big.width
    img = big.resize((TARGET_W, int(big.height * scale)), Image.LANCZOS)
    W, H = img.size
    print('plate %d x %d px  (%.2f m/px ground)'
          % (W, H, (w / W) * math.cos(math.radians(29.137))))

    def to_px(lon, lat):
        x, y = merc(lon, lat)
        return ((x - x0) / w * W, (y1 - y) / h * H)

    # ------------------------------------------------------- boundaries
    ov = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(ov)
    for f in feats:
        n = f['properties']['lot']
        pts = [to_px(lon, lat) for lon, lat in f['geometry']['coordinates'][0]]
        od.polygon(pts, fill=COL[n] + (58,))
        od.line(pts + [pts[0]], fill=(255, 255, 255, 235), width=7, joint='curve')
        od.line(pts + [pts[0]], fill=COL[n] + (255,), width=4, joint='curve')
    img = Image.alpha_composite(img.convert('RGBA'), ov).convert('RGB')
    d = ImageDraw.Draw(img)

    f_num = font(40, True)
    f_name = font(46, True)
    f_sub = font(34)
    f_small = font(27)

    # ------------------------------------------------------- pins + tags
    for f in feats:
        p = f['properties']
        n = p['lot']
        cx, cy = to_px(p['centroid'][1], p['centroid'][0])
        col = COL[n]

        dx, dy, side = LABEL[n]
        # tag geometry
        name = p['listing_name']
        sub = 'PID %s · %s ac of record' % (p['pid'], p['acres_of_record'])
        tw = max(d.textlength(name, font=f_name), d.textlength(sub, font=f_sub))
        pad, barw = 22, 12
        tagw = int(tw + pad * 2 + barw + 74)
        tagh = 118
        tx = cx + dx if side == 'left' else cx + dx - tagw
        ty = cy + dy - tagh // 2
        tx = max(12, min(W - tagw - 12, tx))
        ty = max(12, min(H - tagh - 12, ty))

        # leader line, pin tip -> tag edge
        ax = tx if side == 'left' else tx + tagw
        ay = ty + tagh / 2
        d.line([(cx, cy), (ax, ay)], fill=(255, 255, 255), width=9)
        d.line([(cx, cy), (ax, ay)], fill=col, width=5)

        # the tag
        rounded(d, [tx, ty, tx + tagw, ty + tagh], 16, fill=(255, 255, 255),
                outline=(20, 30, 36), width=4)
        rounded(d, [tx + 7, ty + 9, tx + 7 + barw, ty + tagh - 9], 5, fill=col)
        # number badge
        bx = tx + 7 + barw + 16
        by = ty + tagh // 2
        d.ellipse([bx, by - 28, bx + 56, by + 28], fill=col)
        _bb = d.textbbox((0, 0), str(n), font=f_num)
        d.text((bx + 28 - (_bb[2] - _bb[0]) / 2 - _bb[0],
                by - (_bb[3] - _bb[1]) / 2 - _bb[1]), str(n), font=f_num,
               fill=(255, 255, 255))
        d.text((bx + 72, ty + 18), name, font=f_name, fill=(18, 28, 34))
        d.text((bx + 72, ty + 70), sub, font=f_sub, fill=(90, 105, 112))

        # the stamp pin, drawn last so it sits above the leader
        rr = 29
        d.polygon([(cx, cy + 4), (cx - 19, cy - 34), (cx + 19, cy - 34)],
                  fill=(255, 255, 255))
        d.ellipse([cx - rr - 4, cy - 2 * rr - 32, cx + rr + 4, cy - 24],
                  fill=(255, 255, 255))
        d.polygon([(cx, cy - 2), (cx - 13, cy - 36), (cx + 13, cy - 36)], fill=col)
        cyc = cy - rr - 28                      # centre of the pin head
        d.ellipse([cx - rr, cyc - rr, cx + rr, cyc + rr], fill=col)
        _pb = d.textbbox((0, 0), str(n), font=f_num)
        d.text((cx - (_pb[2] - _pb[0]) / 2 - _pb[0],
                cyc - (_pb[3] - _pb[1]) / 2 - _pb[1]), str(n), font=f_num,
               fill=(255, 255, 255))

    # ------------------------------------------------------- scale bar
    gm_per_px = (w / W) * math.cos(math.radians(29.137))
    for target in (500, 400, 300, 200):
        barpx = target / gm_per_px
        if barpx < W * 0.34:
            break
    bx, by = 44, H - 70
    d.rectangle([bx - 16, by - 56, bx + barpx + 190, by + 34], fill=(255, 255, 255))
    d.rectangle([bx, by, bx + barpx, by + 15], fill=(20, 30, 36))
    d.rectangle([bx, by, bx + barpx / 2, by + 15], fill=(255, 255, 255),
                outline=(20, 30, 36), width=3)
    d.text((bx, by - 48), '%d m' % target, font=f_name, fill=(20, 30, 36))
    d.text((bx + barpx + 18, by - 8), '%.0f ft' % (target * 3.28084),
           font=f_sub, fill=(90, 105, 112))

    # north arrow
    nx, ny = W - 92, H - 126
    d.ellipse([nx - 46, ny - 46, nx + 46, ny + 46], fill=(255, 255, 255))
    d.polygon([(nx, ny - 34), (nx - 17, ny + 24), (nx, ny + 11), (nx + 17, ny + 24)],
              fill=(20, 30, 36))
    _nb = d.textbbox((0, 0), 'N', font=f_name)
    d.text((nx - (_nb[2] - _nb[0]) / 2 - _nb[0], ny + 22), 'N', font=f_name,
           fill=(20, 30, 36))

    # attribution
    att = 'Imagery © Esri, Maxar, Earthstar Geographics · boundaries: Brazoria County ArcGIS parcel service'
    aw = d.textlength(att, font=f_small)
    d.rectangle([W - aw - 32, 12, W - 10, 54], fill=(255, 255, 255))
    d.text((W - aw - 21, 21), att, font=f_small, fill=(90, 105, 112))

    img.save(OUT, 'JPEG', quality=92, optimize=True, progressive=True)
    print('wrote %s — %d x %d, %.0f kB' % (OUT, W, H, os.path.getsize(OUT) / 1024))


if __name__ == '__main__':
    main()
