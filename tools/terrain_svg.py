#!/usr/bin/env python3
"""True-scale SVG drawings from data/terrain.json.

terrain_figs(lot) -> (plan_svg, section_svg, meta)

The plan is rotated so the A-B section line runs horizontally, and the section below it is
drawn at the *same* horizontal scale, so the two figures line up station for station.

  plan     boundary, 1 ft LiDAR contours (labelled), water, street centreline, dotted A-B
  section  a vertically exaggerated panel carrying the real slope angles, the same ground
           again at 1:1 with no exaggeration, and an earth-curvature check

Emitted in millimetres with an explicit scale ratio and scale bar: printed at 100% these
are true-scale drawings.
"""
import math

M_PER_FT = 0.3048
R_EARTH = 6371008.8
NICE = [100, 125, 150, 200, 250, 300, 400, 500, 600, 750, 800, 1000, 1250, 1500, 2000]
INK, MUTED, FAINT = '#16262c', '#54666d', '#9aa8ad'
TEAL, BLUE, RED, AMBER, GREEN = '#0f766e', '#1c3ba8', '#a91f14', '#a8560a', '#15602f'
WATER, WATER_L = '#cfe3ee', '#7fa9c4'
SOIL, SOIL_L = '#efe3d2', '#7a5a33'


# ---------------------------------------------------------------- helpers
def rdp(pts, eps):
    out = [pts[0]]
    stack = [(0, len(pts) - 1)]
    keep = {0, len(pts) - 1}
    while stack:
        i, j = stack.pop()
        ax, ay = pts[i]
        bx, by = pts[j]
        dx, dy = bx - ax, by - ay
        L = math.hypot(dx, dy)
        imax, dmax = -1, -1.0
        for m in range(i + 1, j):
            px, py = pts[m]
            d = (abs(dy * px - dx * py + bx * ay - by * ax) / L) if L > 0 \
                else math.hypot(px - ax, py - ay)
            if d > dmax:
                imax, dmax = m, d
        if imax > 0 and dmax > eps:
            keep.add(imax)
            stack.append((i, imax))
            stack.append((imax, j))
    return [pts[i] for i in sorted(keep)]


def clip_box(pts, box):
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


def esc(s):
    return str(s).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def rotator(A, B):
    th = math.atan2(B[1] - A[1], B[0] - A[0])
    c, s = math.cos(-th), math.sin(-th)
    ax, ay = A

    def f(x, y):
        dx, dy = x - ax, y - ay
        return (dx * c - dy * s, dx * s + dy * c)
    return f, th


# ---------------------------------------------------------------- the pair of figures
def terrain_figs(lot, avail_w_mm=176.0, plan_h_mm=98.0):
    rot, th = rotator(lot['A_m'], lot['B_m'])
    ring = [rot(*p) for p in lot['ring_m']]
    Lm = lot['transect_len_m']
    prof = lot['profile']
    st0, stN = prof[0][0], prof[-1][0]

    xs = [p[0] for p in ring] + [st0, stN]
    ys = [p[1] for p in ring]
    padx, pady = 6.0, 7.0
    x0, x1 = min(xs) - padx, max(xs) + padx
    y0, y1 = min(ys) - pady, max(ys) + pady
    w_m, h_m = x1 - x0, y1 - y0

    ml, mr, mt, mb = 6.0, 17.0, 5.0, 13.0
    availw = avail_w_mm - ml - mr
    availh = plan_h_mm - mt - mb
    ratio = None
    for r in NICE:
        k = 1000.0 / r
        if w_m * k <= availw and h_m * k <= availh:
            ratio = r
            break
    if ratio is None:
        ratio = NICE[-1]
    k = 1000.0 / ratio

    W = w_m * k + ml + mr
    H = h_m * k + mt + mb

    def PX(x):
        return ml + (x - x0) * k

    def PY(y):
        return mt + (y1 - y) * k

    box = (x0, y0, x1, y1)
    o = ['<svg xmlns="http://www.w3.org/2000/svg" width="%.2fmm" height="%.2fmm" '
         'viewBox="0 0 %.2f %.2f" class="dwg" role="img" aria-label="True-scale plan of %s '
         'with 1 ft contours and the A-B section line">' % (W, H, W, H, esc(lot['name'])),
         '<rect width="%.2f" height="%.2f" fill="#fff"/>' % (W, H),
         '<defs><clipPath id="pc%d"><rect x="%.2f" y="%.2f" width="%.2f" height="%.2f"/></clipPath>'
         '</defs>' % (lot['lot'], ml, mt, w_m * k, h_m * k),
         '<g clip-path="url(#pc%d)">' % lot['lot']]

    def dpath(pts):
        return 'M' + 'L'.join('%.2f %.2f' % (PX(p[0]), PY(p[1])) for p in pts)

    # water
    if lot.get('water'):
        wxy = [rot(*p) for p in lot['water']['xy']]
        o.append('<path d="%sZ" fill="%s" fill-opacity=".6" stroke="none"/>'
                 % (dpath(rdp(wxy, 0.5)), WATER))
        for run in clip_box(wxy, box):
            o.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.0"/>'
                     % (dpath(rdp(run, 0.4)), WATER_L))

    # contours — drop the sub-15 m squiggles, which on ground this flat are LiDAR micro-relief
    # rather than landform, and would otherwise bury the drawing in noise
    def run_len(r):
        return sum(math.dist(r[i], r[i + 1]) for i in range(len(r) - 1))

    for c in lot['contours']:
        e = c['elev_ft']
        if e is None:
            continue
        idx = int(round(e)) % 5 == 0
        for run in clip_box([rot(*p) for p in c['xy']], box):
            if run_len(run) < 15.0:
                continue
            run = rdp(run, 0.35)
            if len(run) > 1:
                o.append('<path d="%s" fill="none" stroke="%s" stroke-width="%.2f" '
                         'stroke-opacity="%.2f" stroke-linecap="round"/>'
                         % (dpath(run), '#9c6b30' if idx else '#c49a68',
                            .55 if idx else .32, .95 if idx else .8))

    # street
    if lot.get('street'):
        for run in clip_box([rot(*p) for p in lot['street']['xy']], box):
            o.append('<path d="%s" fill="none" stroke="%s" stroke-width="3.0" '
                     'stroke-opacity=".16" stroke-linecap="round"/>' % (dpath(run), INK))
            o.append('<path d="%s" fill="none" stroke="%s" stroke-width=".38" '
                     'stroke-dasharray="2.6 1.7" stroke-opacity=".6"/>' % (dpath(run), INK))
    o.append('</g>')

    # contour labels — several per elevation where they fit, but never on top of each other
    cands = []
    for c in lot['contours']:
        e = c['elev_ft']
        if e is None:
            continue
        for run in clip_box([rot(*p) for p in c['xy']], box):
            L = run_len(run)
            if L < 22:
                continue
            for frac in (0.5, 0.22, 0.78):
                idx_p = max(0, min(len(run) - 1, int(frac * (len(run) - 1))))
                cands.append((L, e, run[idx_p]))
    cands.sort(key=lambda z: -z[0])
    placed, per_elev = [], {}
    for L, e, (px, py) in cands:
        if per_elev.get(e, 0) >= 2:          # two labels per contour value is plenty
            continue
        X, Y = PX(px), PY(py)
        if not (ml + 5 < X < ml + w_m * k - 5 and mt + 4 < Y < mt + h_m * k - 4):
            continue
        if any(math.hypot(X - qx, Y - qy) < 13.0 for qx, qy in placed):
            continue
        placed.append((X, Y))
        per_elev[e] = per_elev.get(e, 0) + 1
        o.append('<g><rect x="%.2f" y="%.2f" width="7.8" height="3.4" rx=".6" fill="#fff" '
                 'fill-opacity=".9"/><text x="%.2f" y="%.2f" font-size="2.45" fill="#8a5a24" '
                 'text-anchor="middle">%g ft</text></g>' % (X - 3.9, Y - 2.45, X, Y + .15, e))
        if len(placed) >= 14:
            break

    # boundary
    o.append('<path d="%sZ" fill="none" stroke="%s" stroke-width=".9" stroke-linejoin="round"/>'
             % (dpath(lot and ring), INK))

    # A-B dotted line
    o.append('<line x1="%.2f" y1="%.2f" x2="%.2f" y2="%.2f" stroke="%s" stroke-width=".75" '
             'stroke-dasharray="2.4 1.6"/>' % (PX(0), PY(0), PX(Lm), PY(0), RED))
    for st, lab, sub in ((0.0, 'A', 'roadside'), (Lm, 'B', 'lakeside')):
        X, Y = PX(st), PY(0)
        o.append('<circle cx="%.2f" cy="%.2f" r="1.85" fill="#fff" stroke="%s" stroke-width=".65"/>'
                 '<text x="%.2f" y="%.2f" font-size="3.0" font-weight="700" fill="%s" '
                 'text-anchor="middle">%s</text>'
                 '<text x="%.2f" y="%.2f" font-size="2.35" fill="%s" text-anchor="middle">%s</text>'
                 % (X, Y, RED, X, Y + 1.1, RED, lab, X, Y - 2.9, RED, sub))

    # north arrow — the needle rotates with the drawing, the letter stays upright
    nx, ny, rr = W - mr + 8.0, mt + 11.0, 6.4
    # in the rotated frame, grid north sits at bearing -th from the +y axis
    nvx, nvy = math.sin(-th), math.cos(-th)          # unit vector toward north, drawing frame
    tipx, tipy = nx + nvx * rr, ny - nvy * rr
    tailx, taily = nx - nvx * rr * .55, ny + nvy * rr * .55
    o.append('<line x1="%.2f" y1="%.2f" x2="%.2f" y2="%.2f" stroke="%s" stroke-width=".55"/>'
             % (tailx, taily, tipx, tipy, INK))
    o.append('<g transform="rotate(%.2f %.2f %.2f)">'
             '<path d="M%.2f %.2f l1.45 3.0 l-1.45 -1.0 l-1.45 1.0 Z" fill="%s"/></g>'
             % (math.degrees(-th), tipx, tipy, tipx, tipy, INK))
    o.append('<text x="%.2f" y="%.2f" font-size="2.7" font-weight="700" fill="%s" '
             'text-anchor="middle">N</text>'
             % (nx + nvx * (rr + 3.4), ny - nvy * (rr + 3.4) + .9, INK))

    # scale bar
    for ftb in (200, 150, 100, 50, 30, 20):
        bar = ftb * M_PER_FT * k
        if bar <= (w_m * k) * 0.4:
            break
    bx, by = ml + 1.0, H - mb + 5.4
    o.append('<g><rect x="%.2f" y="%.2f" width="%.2f" height="1.5" fill="%s"/>'
             '<rect x="%.2f" y="%.2f" width="%.2f" height="1.5" fill="#fff" stroke="%s" '
             'stroke-width=".25"/>'
             '<text x="%.2f" y="%.2f" font-size="2.4" fill="%s">0</text>'
             '<text x="%.2f" y="%.2f" font-size="2.4" fill="%s" text-anchor="middle">%d ft / %.0f m</text>'
             '<text x="%.2f" y="%.2f" font-size="2.7" font-weight="700" fill="%s" text-anchor="end">'
             'PLAN · TRUE SCALE 1:%d</text></g>'
             % (bx, by, bar / 2, INK, bx + bar / 2, by, bar / 2, INK,
                bx, by + 4.3, MUTED, bx + bar / 2, by + 4.3, MUTED, ftb, ftb * M_PER_FT,
                W - 1.0, by + 1.3, INK, ratio))
    o.append('</svg>')
    plan = ''.join(o)

    # ============================================================ section
    sml = ml + (0 - x0) * k          # keep station 0 under the plan's A
    plot_w = (stN - st0) * k
    xoff = ml + (st0 - x0) * k

    def SX(st):
        return xoff + (st - st0) * k

    lo = math.floor(min(p[1] for p in prof) - 1)
    hi = max(math.ceil(max(p[1] for p in prof) + 1), 31)
    rng = hi - lo
    h_ex = 44.0
    kv = h_ex / rng
    vex = kv / (M_PER_FT * k)
    h_true = rng * M_PER_FT * k

    top_ex = 9.0
    top_tr = top_ex + h_ex + 20.0
    top_cu = top_tr + max(h_true, 4.0) + 19.0
    h_cu = 14.0
    SH = top_cu + h_cu + 10.0

    def EY(ft):
        return top_ex + (hi - ft) * kv

    def TY(ft):
        return top_tr + (hi - ft) * M_PER_FT * k

    s = ['<svg xmlns="http://www.w3.org/2000/svg" width="%.2fmm" height="%.2fmm" '
         'viewBox="0 0 %.2f %.2f" class="dwg" role="img" aria-label="Longitudinal section A to B '
         'of %s">' % (W, SH, W, SH, esc(lot['name'])),
         '<rect width="%.2f" height="%.2f" fill="#fff"/>' % (W, SH)]
    s.append('<text x="%.2f" y="%.2f" font-size="2.85" font-weight="700" fill="%s">SECTION A–B'
             '<tspan fill="%s" font-weight="400">   horizontal 1:%d true · vertical ×%.0f '
             'exaggerated so the shape is visible</tspan></text>'
             % (ml, top_ex - 3.6, INK, MUTED, ratio, vex))

    ft = lo
    while ft <= hi:
        y = EY(ft)
        maj = int(ft) % 5 == 0
        s.append('<line x1="%.2f" y1="%.2f" x2="%.2f" y2="%.2f" stroke="%s" stroke-width="%.2f" '
                 'stroke-opacity="%.2f"/>' % (xoff, y, xoff + plot_w, y, INK,
                                              .32 if maj else .16, .30 if maj else .13))
        if maj:
            s.append('<text x="%.2f" y="%.2f" font-size="2.35" fill="%s" text-anchor="end">%d</text>'
                     % (xoff - 1.3, y + .8, MUTED, ft))
        ft += 1
    s.append('<text font-size="2.25" fill="%s" text-anchor="middle" transform="rotate(-90 %.2f %.2f)" '
             'x="%.2f" y="%.2f">elevation, ft NAVD88</text>'
             % (MUTED, xoff - 8.6, top_ex + h_ex / 2, xoff - 8.6, top_ex + h_ex / 2))

    for lev, col, lab in ((28, AMBER, 'BFE 28 ft — nearest published line on the effective FIRM'),
                          (30, RED, 'finished floor must reach 30 ft (BFE + 24 in)')):
        if lo <= lev <= hi:
            y = EY(lev)
            s.append('<line x1="%.2f" y1="%.2f" x2="%.2f" y2="%.2f" stroke="%s" stroke-width=".5" '
                     'stroke-dasharray="3 1.7"/>' % (xoff, y, xoff + plot_w, y, col))
            s.append('<text x="%.2f" y="%.2f" font-size="2.25" fill="%s">%s</text>'
                     % (xoff + 1.2, y - 1.1, col, lab))

    g = [(SX(p[0]), EY(p[1])) for p in prof]
    d = 'M' + 'L'.join('%.2f %.2f' % p for p in g)
    s.append('<path d="%s L%.2f %.2f L%.2f %.2f Z" fill="%s"/>'
             % (d, g[-1][0], EY(lo), g[0][0], EY(lo), SOIL))
    s.append('<path d="%s" fill="none" stroke="%s" stroke-width=".85" stroke-linejoin="round"/>'
             % (d, SOIL_L))

    # water surface: the pond edge sits at the low end (or, on lot 4, beyond the levee crest)
    wl = min(p[1] for p in prof[-12:])
    xw0, xw1 = SX(prof[-1][0] - 20), SX(prof[-1][0])
    s.append('<rect x="%.2f" y="%.2f" width="%.2f" height="%.2f" fill="%s" fill-opacity=".75"/>'
             '<line x1="%.2f" y1="%.2f" x2="%.2f" y2="%.2f" stroke="%s" stroke-width=".5"/>'
             % (xw0, EY(wl), xw1 - xw0, max(.5, EY(lo) - EY(wl)), WATER,
                xw0, EY(wl), xw1, EY(wl), WATER_L))

    for st, lab, sub in ((0.0, 'A', 'boundary at road'), (Lm, 'B', 'boundary at water')):
        x = SX(st)
        s.append('<line x1="%.2f" y1="%.2f" x2="%.2f" y2="%.2f" stroke="%s" stroke-width=".42" '
                 'stroke-dasharray="1.7 1.3"/>' % (x, top_ex, x, EY(lo), RED))
        s.append('<text x="%.2f" y="%.2f" font-size="3.0" font-weight="700" fill="%s" '
                 'text-anchor="middle">%s</text>'
                 '<text x="%.2f" y="%.2f" font-size="2.2" fill="%s" text-anchor="middle">%s</text>'
                 % (x, top_ex - .9, RED, lab, x, EY(lo) + 3.3, MUTED, sub))

    pmin = min(prof, key=lambda p: p[1])
    pmax = max(prof, key=lambda p: p[1])
    for p, col, lab, dy in ((pmax, GREEN, 'highest %.1f ft' % pmax[1], -2.1),
                            (pmin, BLUE, 'lowest %.1f ft' % pmin[1], 3.3)):
        x, y = SX(p[0]), EY(p[1])
        s.append('<circle cx="%.2f" cy="%.2f" r="1.0" fill="%s"/>'
                 '<text x="%.2f" y="%.2f" font-size="2.4" font-weight="600" fill="%s" '
                 'text-anchor="middle">%s</text>' % (x, y, col, x, y + dy, col, lab))

    # slope callouts
    used, shown = [], 0
    for seg in sorted(lot['segments'], key=lambda z: -abs(z['angle_deg'])):
        if shown >= 3 or abs(seg['angle_deg']) < 1.8:
            break
        mid = (seg['from_m'] + seg['to_m']) / 2
        if any(abs(mid - u) < (stN - st0) * 0.14 for u in used):
            continue
        used.append(mid)
        shown += 1
        xa, xb = SX(seg['from_m']), SX(seg['to_m'])
        ya, yb = EY(seg['from_ft_elev']), EY(seg['to_ft_elev'])
        s.append('<line x1="%.2f" y1="%.2f" x2="%.2f" y2="%.2f" stroke="%s" stroke-width="1.05"/>'
                 % (xa, ya, xb, yb, RED))
        lx, ly = (xa + xb) / 2, (ya + yb) / 2
        up = -1 if seg['angle_deg'] < 0 else 1
        s.append('<g><rect x="%.2f" y="%.2f" width="29" height="4.7" rx=".8" fill="#fff" '
                 'fill-opacity=".93" stroke="%s" stroke-width=".22"/>'
                 '<text x="%.2f" y="%.2f" font-size="2.3" font-weight="700" fill="%s" '
                 'text-anchor="middle">%.1f° · %.0f%% · %.1f ft in %.0f m</text></g>'
                 % (lx - 14.5, ly + 3.0 * up - 2.35, RED, lx, ly + 3.0 * up + 1.0, RED,
                    abs(seg['angle_deg']), abs(seg['grade_pct']), abs(seg['rise_ft']), seg['run_m']))

    s.append('<line x1="%.2f" y1="%.2f" x2="%.2f" y2="%.2f" stroke="%s" stroke-width=".45"/>'
             % (xoff, EY(lo), xoff + plot_w, EY(lo), INK))
    t = 0
    while t * M_PER_FT <= stN:
        if t * M_PER_FT >= st0:
            x = SX(t * M_PER_FT)
            s.append('<line x1="%.2f" y1="%.2f" x2="%.2f" y2="%.2f" stroke="%s" stroke-width=".4"/>'
                     '<text x="%.2f" y="%.2f" font-size="2.2" fill="%s" text-anchor="middle">%d</text>'
                     % (x, EY(lo), x, EY(lo) + 1.3, INK, x, EY(lo) + 6.4, MUTED, t))
        t += 50
    s.append('<text x="%.2f" y="%.2f" font-size="2.25" fill="%s" text-anchor="middle">'
             'distance from A along the section, ft</text>'
             % (xoff + plot_w / 2, EY(lo) + 9.7, MUTED))

    # 1:1 panel
    s.append('<text x="%.2f" y="%.2f" font-size="2.85" font-weight="700" fill="%s">THE SAME GROUND '
             'AT 1:1<tspan fill="%s" font-weight="400">   no vertical exaggeration — this is the '
             'real shape of the slope</tspan></text>' % (ml, top_tr - 4.2, INK, MUTED))
    g2 = [(SX(p[0]), TY(p[1])) for p in prof]
    d2 = 'M' + 'L'.join('%.2f %.2f' % p for p in g2)
    s.append('<path d="%s L%.2f %.2f L%.2f %.2f Z" fill="%s" stroke="%s" stroke-width=".5"/>'
             % (d2, g2[-1][0], TY(lo), g2[0][0], TY(lo), SOIL, SOIL_L))
    s.append('<line x1="%.2f" y1="%.2f" x2="%.2f" y2="%.2f" stroke="%s" stroke-width=".4" '
             'stroke-dasharray="2 1.5"/>'
             '<text x="%.2f" y="%.2f" font-size="2.2" fill="%s">30 ft</text>'
             % (xoff, TY(30), xoff + plot_w, TY(30), RED, xoff + plot_w + .8, TY(30) + .8, RED))
    for lev in (hi, lo):
        s.append('<text x="%.2f" y="%.2f" font-size="2.2" fill="%s" text-anchor="end">%d ft</text>'
                 % (xoff - 1.3, TY(lev) + .8, MUTED, lev))

    # curvature panel
    drop = ((stN - st0) ** 2) / (2 * R_EARTH)
    s.append('<text x="%.2f" y="%.2f" font-size="2.85" font-weight="700" fill="%s">'
             'EARTH-CURVATURE CHECK<tspan fill="%s" font-weight="400">   over the %.0f ft section, '
             'against the flat datum used above</tspan></text>'
             % (ml, top_cu - 3.6, INK, MUTED, (stN - st0) / M_PER_FT))
    kcu = (h_cu - 3.5) / max(drop, 1e-12)
    s.append('<line x1="%.2f" y1="%.2f" x2="%.2f" y2="%.2f" stroke="%s" stroke-width=".5" '
             'stroke-dasharray="2 1.4"/>' % (xoff, top_cu, xoff + plot_w, top_cu, MUTED))
    pts = []
    for i in range(81):
        tt = i / 80.0
        xm = tt * (stN - st0)
        dy = ((xm - (stN - st0) / 2) ** 2 - ((stN - st0) / 2) ** 2) / (2 * R_EARTH)
        pts.append((xoff + tt * plot_w, top_cu - dy * kcu))
    s.append('<path d="M%s" fill="none" stroke="%s" stroke-width=".8"/>'
             % ('L'.join('%.2f %.2f' % p for p in pts), TEAL))
    s.append('<text x="%.2f" y="%.2f" font-size="2.25" fill="%s">flat chord — the datum every '
             'panel above uses</text>' % (xoff + 1.2, top_cu - 1.3, MUTED))
    s.append('<text x="%.2f" y="%.2f" font-size="2.25" fill="%s">true curved sea-level surface: '
             'it falls away by just <tspan font-weight="700">%.2f mm (%.4f ft)</tspan> at '
             'mid-section</text>' % (xoff + 1.2, top_cu + h_cu - .8, TEAL, drop * 1000,
                                     drop / M_PER_FT))
    s.append('<text x="%.2f" y="%.2f" font-size="2.15" fill="%s" text-anchor="end">this panel is '
             'exaggerated ×%s vertically just to make the curve visible</text>'
             % (xoff + plot_w, top_cu + h_cu + 3.4, FAINT,
                format(int(round(kcu / (M_PER_FT * k))), ',')))
    s.append('</svg>')

    meta = dict(ratio=ratio, vex=round(vex), plan_h=H, sec_h=SH,
                curv_mm=round(drop * 1000, 2), curv_ft=drop / M_PER_FT,
                lo=lo, hi=hi, span_ft=(stN - st0) / M_PER_FT)
    return plan, ''.join(s), meta
