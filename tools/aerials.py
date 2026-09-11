#!/usr/bin/env python3
"""Generate the lot imagery from USGS NAIP aerial photography (public domain, 30 cm).

Three images per lot, written into assets/photos/:

  lotN-1.jpg  hero — the parcel wide, with its recorded boundary and the A-B section line
  lotN-2.jpg  the water frontage, close, centred on point B
  lotN-3.jpg  neighbourhood context, with the parcel outlined

Resolution policy
-----------------
NAIP is 30 cm native and nothing better is published for this area (Esri World Imagery tops
out near 26 cm here and returns empty tiles above zoom 19). So these are sampled at a fixed
**0.15 m per pixel** — a 2x oversample of the source, which is the practical ceiling for a
print — and then unsharp-masked. Asking the server for 0.06 m/px, as the first version did,
just interpolated 30 cm data five times over and looked soft.

Needs Pillow:  pip install Pillow

    python3 tools/aerials.py

Source: USGS NAIPPlus ImageServer, imagery.nationalmap.gov. NAIP is US Department of
Agriculture aerial photography in the public domain.
"""
import json
import math
import os
import urllib.parse
import urllib.request

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageOps

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTDIR = os.path.join(ROOT, 'assets', 'photos')
NAIP = "https://imagery.nationalmap.gov/arcgis/rest/services/USGSNAIPPlus/ImageServer/exportImage"
UA = {'User-Agent': '4lots-feasibility-research/1.0'}
R = 6378137.0

M_PER_PX = 0.15          # 2x oversample of 30 cm NAIP — the honest ceiling
MAX_PX = 2600            # 2600 px across 176 mm is ~375 dpi
MIN_PX = 1500            # never hand the page a frame too small to print well

BOUND = (255, 209, 61)
BOUND_HALO = (26, 18, 4)
SECT = (255, 86, 66)
WHITE = (255, 255, 255)
_FONTS = {}
_FONT_FILE = None


def font_file():
    """Find a bold sans TTF on the system.

    The first version hardcoded DejaVu paths that do not exist here, silently fell through to
    PIL's 11-pixel bitmap default, and stamped unreadable type onto every image.
    """
    global _FONT_FILE
    if _FONT_FILE:
        return _FONT_FILE
    import glob
    prefer = ('NotoSans-Bold', 'DejaVuSans-Bold', 'LiberationSans-Bold', 'Arial-Bold',
              'NotoSans-SemiBold', 'NotoSans-Regular', 'DejaVuSans')
    found = []
    for root in ('/usr/share/fonts', '/usr/local/share/fonts', os.path.expanduser('~/.fonts')):
        found += glob.glob(os.path.join(root, '**', '*.ttf'), recursive=True)
    for want in prefer:
        for f in found:
            if os.path.splitext(os.path.basename(f))[0] == want:
                _FONT_FILE = f
                return f
    if found:
        _FONT_FILE = found[0]
        return _FONT_FILE
    raise RuntimeError("no TrueType font found — install a sans font (e.g. google-noto)")


def font(size):
    size = max(8, int(size))
    if size not in _FONTS:
        from PIL import ImageFont
        _FONTS[size] = ImageFont.truetype(font_file(), size)
    return _FONTS[size]


def to3857(lon, lat):
    return (R * math.radians(lon),
            R * math.log(math.tan(math.pi / 4 + math.radians(lat) / 2)))


NATIVE_M = 0.30          # NAIP ground sample distance; asking for finer only interpolates


def fetch(cx, cy, ground_w, aspect, target_px=None):
    """Export NAIP at its native 30 cm, centred on a web-mercator point."""
    px = int(round(ground_w / NATIVE_M))
    py = int(round(px / aspect))
    half_w = ground_w / 2.0
    half_h = half_w / aspect
    bbox = (cx - half_w, cy - half_h, cx + half_w, cy + half_h)
    q = urllib.parse.urlencode({
        'bbox': '%f,%f,%f,%f' % bbox, 'bboxSR': 3857, 'imageSR': 3857,
        'size': '%d,%d' % (px, py), 'format': 'png',
        'interpolation': 'RSP_BilinearInterpolation', 'f': 'image'})
    data = urllib.request.urlopen(urllib.request.Request(NAIP + '?' + q, headers=UA),
                                  timeout=240).read()
    tmp = os.path.join(OUTDIR, '.tmp')
    open(tmp, 'wb').write(data)
    im = Image.open(tmp).convert('RGB')
    os.remove(tmp)
    want = target_px or min(MAX_PX, max(MIN_PX, int(round(ground_w / M_PER_PX))))
    if want and want != im.size[0]:
        im = im.resize((want, int(round(want * im.size[1] / im.size[0]))), Image.LANCZOS)
    return im, bbox


def enhance(im, sharpen=True):
    """NAIP comes out flat and hazy over bare ground.

    The haze is stretched out on the **luminance** channel only. Doing it per RGB channel,
    as the first attempt did, throws a colour cast and clips the shadows to black.
    """
    lab = im.convert('LAB')
    L, a, b = lab.split()
    L = ImageOps.autocontrast(L, cutoff=(0.4, 0.1))
    im = Image.merge('LAB', (L, a, b)).convert('RGB')
    im = ImageEnhance.Color(im).enhance(1.14)
    im = ImageEnhance.Contrast(im).enhance(1.03)
    if sharpen:
        im = im.filter(ImageFilter.UnsharpMask(radius=1.7, percent=130, threshold=2))
    return im


def mapper(bbox, size):
    x0, y0, x1, y1 = bbox
    w, h = size
    return lambda x, y: ((x - x0) / (x1 - x0) * w, (y1 - y) / (y1 - y0) * h)


def scrim(im, px, strength=190, edge='bottom'):
    """A soft dark gradient along one edge so white type stays legible."""
    w, h = im.size
    hh = max(2, int(px))
    grad = Image.new('L', (1, hh))
    for i in range(hh):
        t = i / hh if edge == 'bottom' else 1 - i / hh
        grad.putpixel((0, i), int(strength * t ** 1.4))
    mask = grad.resize((w, hh))
    dark = Image.new('RGB', (w, hh), (7, 12, 16))
    im.paste(dark, (0, h - hh if edge == 'bottom' else 0), mask)
    return im


def draw_boundary(dr, pts, w_halo, w_line):
    dr.line(pts + [pts[0]], fill=BOUND_HALO, width=w_halo, joint='curve')
    dr.line(pts + [pts[0]], fill=BOUND, width=w_line, joint='curve')


def text(dr, xy, s, size, fill=WHITE, halo=(0, 0, 0), anchor=None):
    f = font(size)
    x, y = xy
    if halo:
        for dx, dy in ((-2, 0), (2, 0), (0, -2), (0, 2), (-1, -1), (1, 1), (-1, 1), (1, -1)):
            dr.text((x + dx, y + dy), s, font=f, fill=halo, anchor=anchor)
    dr.text((x, y), s, font=f, fill=fill, anchor=anchor)


def scalebar(im, mpp, metres, size):
    """A scale bar in a translucent plate, top-right, clear of the parcel geometry."""
    w, h = im.size
    px = metres / mpp
    bar_h = max(7, int(size * 0.24))
    pad = int(size * 0.5)
    plate_w = int(px) + pad * 2
    plate_h = int(size * 1.55) + bar_h + pad
    px0 = w - plate_w - int(w * 0.018)
    py0 = int(w * 0.012)
    region = im.crop((px0, py0, px0 + plate_w, py0 + plate_h))
    im.paste(Image.blend(region, Image.new('RGB', region.size, (8, 13, 17)), 0.66), (px0, py0))
    dr = ImageDraw.Draw(im)
    bx = px0 + pad
    by = py0 + plate_h - pad - bar_h + int(bar_h * 0.2)
    dr.rectangle([bx, by, bx + px / 2, by + bar_h], fill=WHITE)
    dr.rectangle([bx + px / 2, by, bx + px, by + bar_h], fill=(138, 147, 152))
    dr.rectangle([bx, by, bx + px, by + bar_h], outline=(18, 24, 28), width=1)
    text(dr, (bx + px / 2, py0 + int(pad * 0.55)),
         "%d m   ·   %d ft" % (metres, round(metres / 0.3048)),
         int(size * 0.78), anchor='ma', halo=None)


def caption(im, title, sub, mpp):
    """Title block bottom-left, so the top of the frame stays clear for the parcel."""
    w, h = im.size
    s = max(26, int(min(w, h * 2.1) * 0.030))
    scrim(im, s * 4.3, strength=200, edge='bottom')
    dr = ImageDraw.Draw(im)
    x = int(w * 0.022)
    text(dr, (x, h - int(s * 3.55)), title, s)
    text(dr, (x, h - int(s * 2.25)), sub, int(s * 0.60), fill=(226, 236, 240))
    text(dr, (x, h - int(s * 1.20)),
         "USGS NAIP aerial · 30 cm native · public domain   ·   %.2f m/px" % mpp,
         max(15, int(s * 0.46)), fill=(206, 219, 224))
    return s


def hero(ring, A, B, aspect=2.42, target_px=2200):
    """A hero frame with the A-B section axis running left to right.

    NAIP cannot be exported pre-rotated, so a square is fetched, the pixels are rotated to
    put A-B horizontal, and the frame is cropped from the middle. The crop is centred on the
    *parcel*, not on the midpoint of A-B — on a wedge-shaped lot the chord is nowhere near a
    symmetry axis, and centring on it blows the frame out to several hundred metres.
    """
    cxm, cym = (A[0] + B[0]) / 2.0, (A[1] + B[1]) / 2.0
    th = math.atan2(B[1] - A[1], B[0] - A[0])
    c, sn = math.cos(-th), math.sin(-th)

    def rot(x, y):
        dx, dy = x - cxm, y - cym
        return (dx * c - dy * sn, dx * sn + dy * c)

    def unrot(u, v):
        return (cxm + u * c + v * sn, cym - u * sn + v * c)

    pts_uv = [rot(*q) for q in ring] + [rot(*A), rot(*B)]
    us = [q[0] for q in pts_uv]
    vs = [q[1] for q in pts_uv]
    ou, ov = (min(us) + max(us)) / 2.0, (min(vs) + max(vs)) / 2.0

    # a floor on the frame width: 30 cm imagery over a 160 m frame cannot fill 2,200 px
    # with real detail, and a wider frame buys both genuine pixels and useful context
    Wg = max((max(us) - min(us)) * 1.14, 210.0)
    Hg = Wg / aspect
    need_h = (max(vs) - min(vs)) * 1.22
    if need_h > Hg:
        Hg = need_h
        Wg = Hg * aspect

    # never enlarge beyond 2x the 30 cm ground sample; past that it is interpolation, not detail
    target_px = int(min(target_px, max(1300, round(Wg / M_PER_PX))))
    Cx, Cy = unrot(ou, ov)
    side = math.hypot(Wg, Hg)
    im, _ = fetch(Cx, Cy, side, 1.0, target_px=int(round(side / (Wg / target_px))))
    im = enhance(im, sharpen=False)
    im = im.rotate(-math.degrees(th), resample=Image.BICUBIC, expand=False)
    mpp = side / im.size[0]

    cw, ch = int(round(Wg / mpp)), int(round(Hg / mpp))
    left = (im.size[0] - cw) // 2
    top = (im.size[1] - ch) // 2
    im = im.crop((left, top, left + cw, top + ch))
    if abs(im.size[0] - target_px) > 2:
        im = im.resize((target_px, int(round(target_px * im.size[1] / im.size[0]))),
                       Image.LANCZOS)
    mpp = Wg / im.size[0]
    im = im.filter(ImageFilter.UnsharpMask(radius=1.7, percent=130, threshold=2))

    W, H = im.size

    def topx(u, v):
        return (W / 2.0 + (u - ou) / mpp, H / 2.0 - (v - ov) / mpp)

    ring_uv = [rot(*q) for q in ring]
    return im, mpp, ring_uv, [topx(*rot(*A)), topx(*rot(*B))], topx


def main():
    os.makedirs(OUTDIR, exist_ok=True)
    gj = json.load(open(os.path.join(ROOT, 'data', 'parcels.geojson')))
    ter = json.load(open(os.path.join(ROOT, 'data', 'terrain.json')))['lots']

    for feat in gj['features']:
        k, p = feat['id'], feat['properties']
        n = p['lot']
        ring = [to3857(lo, la) for lo, la in feat['geometry']['coordinates'][0]]
        xs = [q[0] for q in ring]
        ys = [q[1] for q in ring]
        cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
        span_x, span_y = max(xs) - min(xs), max(ys) - min(ys)

        t = ter[k]
        lat0, lon0 = t['origin']
        mlat, mlon = t['m_per_deg']

        def loc(xy):
            return to3857(lon0 + xy[0] / mlon, lat0 + xy[1] / mlat)

        A, B = loc(t['A_m']), loc(t['B_m'])

        ctx_w = max(span_x, span_y) * 3.4

        ux, uy = B[0] - A[0], B[1] - A[1]
        ul = math.hypot(ux, uy) or 1.0
        Bx = B[0] + ux / ul * 32.0
        By = B[1] + uy / ul * 32.0

        jobs = [
            (1, None, None, None, None, True, True,
             'the parcel, boundary of record, and section A\u2013B running left to right', 30),
            (2, Bx, By, 150.0, 16 / 9.0, True, True, 'the water frontage at B', 20),
            (3, cx, cy, ctx_w, 16 / 9.0, True, False, 'neighbourhood context', 100),
        ]
        for idx, mx, my, gw, asp, bound, sect, cap, sb in jobs:
            if idx == 1:
                im, mpp, ru, ab, topx = hero(ring, A, B)
                pts = [topx(*q) for q in ru]
                a, b = ab
                gw = im.size[0] * mpp
                f = None
            else:
                im, bbox = fetch(mx, my, gw, asp, target_px=MIN_PX)
                im = enhance(im)
                f = mapper(bbox, im.size)
                mpp = (bbox[2] - bbox[0]) / im.size[0]
                pts = [f(*q) for q in ring]
                a, b = f(*A), f(*B)
            dr = ImageDraw.Draw(im)
            w = im.size[0]
            if bound:
                draw_boundary(dr, pts, max(7, int(w * 0.0055)), max(3, int(w * 0.0026)))
            if sect:
                dr.line([a, b], fill=(20, 12, 8), width=max(8, int(w * 0.0055)))
                dr.line([a, b], fill=SECT, width=max(3, int(w * 0.0026)))
                r = max(14, int(w * 0.0105))
                for pt, tx in ((a, 'A'), (b, 'B')):
                    dr.ellipse([pt[0] - r, pt[1] - r, pt[0] + r, pt[1] + r],
                               fill=WHITE, outline=SECT, width=max(3, int(r * 0.24)))
                    text(dr, (pt[0], pt[1] - r * 0.86), tx, int(r * 1.5),
                         fill=(150, 32, 22), halo=None, anchor='ma')
            sz = caption(im, "Lot %d · %s" % (n, p['listing_name']), cap, mpp)
            scalebar(im, mpp, sb, sz)
            path = os.path.join(OUTDIR, 'lot%d-%d.jpg' % (n, idx))
            im.save(path, quality=92, optimize=True, progressive=True)
            print("  lot%d-%d.jpg  %5dx%-5d %.2f m/px  %4.0f m across  %4.0f kB  %s"
                  % (n, idx, im.size[0], im.size[1], mpp, gw,
                     os.path.getsize(path) / 1024, cap))


if __name__ == '__main__':
    main()
