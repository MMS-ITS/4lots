#!/usr/bin/env python3
"""Generate the Brazoria County floodplain correspondence.

Writes, into letters/:
  * one A4 request letter PDF per parcel, asking for a written BFE determination
  * a combined PDF carrying all four letters
  * EMAIL-DRAFTS.md — the same requests as plain-text e-mails, ready to paste

Every parcel figure is read from data/parcels.geojson and data/fill.json, so the
letters cannot drift from the report. Nothing is hard-coded per lot except the
lot-specific questions at the foot of each letter.

    python3 tools/letters.py
"""
import json
import os
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTDIR = os.path.join(ROOT, 'letters')
CHROME = '/usr/local/bin/chrome'

PREPARED_FOR = "Mohsin Chowdhury"
DATED = "13 September 2026"

# The sender block, as it prints on every letter and signs off every e-mail.
SENDER = {
    'name': PREPARED_FOR,
    'addr1': '3731 Bright Aquarius Lane',
    'addr2': 'Henderson, Nevada 89052',
    'tel': '(702) 582-5724',
    'email': 'mms221@gmail.com',
}

# The county office that issues both the floodplain determination and the building permit.
COUNTY = {
    'office': 'Floodplain &amp; 911 Administration',
    'body': 'Brazoria County',
    'addr1': '451 North Velasco, Suite 210',
    'addr2': 'Angleton, Texas 77515',
    'tel': '(979) 864-1295',
    'tel2': '(281) 756-1295',
}

# Standards the letters state as the applicant's understanding, for confirmation.
FREEBOARD_IN = 24
FFE_FT = 30.0          # BFE 28.0 + 24 in, per data/fill.json basis
PANEL = '48039C0420K'
PANEL_EFF = '30 December 2020'


def money(n):
    return '$%s' % format(int(round(n)), ',d')


# --------------------------------------------------------------- lot-specific questions
EXTRA = {
    1: [
        ("Governing watercourse",
         "Mill Bayou lies about 112 ft from this parcel and an unnamed water body about 38 ft from it, "
         "while the nearest published BFE line sits roughly 1,594 ft away — the greatest separation of "
         "the four parcels. Please confirm which flooding source governs here, and whether the BFE for "
         "this parcel is taken from the Mill Bayou profile or interpolated from a more distant section."),
        ("Water-body setback and fill limits",
         "Please confirm any county setback, fill restriction or easement applying to the portion of the "
         "parcel adjoining the water, and whether fill is permitted within it."),
    ],
    2: [
        ("Highest natural ground of the four",
         "County LiDAR puts natural ground here between about 24.9 and 29.4 ft NAVD88, averaging about "
         "28.1 ft — so the calculated lift to a compliant pad is only about 0.7 ft. Please confirm "
         "whether a pad of that order is acceptable, and what the county will require as evidence of "
         "existing grade."),
        ("Recorded drainage easements",
         "The restrictions of record for this section reference drainage easements at 1712/500. Please "
         "confirm whether any mapped drainage easement crosses this parcel and how it constrains the "
         "building envelope or the placement of fill."),
    ],
    3: [
        ("Address of record",
         "The situs of record for PID 186219 reads HIGHWAY 35, while the parcel is marketed as Lot 29 "
         "Broken Arrow Trail. As the same office administers 911 addressing, please confirm the correct "
         "address of record and what is required to assign or correct the situs address before a permit "
         "is issued."),
        ("Distance to the published BFE line",
         "The nearest published BFE line is roughly 2,477 ft from this parcel — the greatest separation "
         "of the four. Please confirm how the BFE is derived at this distance."),
    ],
    4: [
        ("Flag Lake Levee and Flag Pond",
         "Flag Pond lies about 11 ft from this parcel, and the Flag Lake Levee — a structure carried in "
         "the National Inventory of Dams — is recorded at about the same distance. Please confirm: the "
         "levee's accreditation status and whether the mapping for this parcel relies on it; its hazard "
         "classification and condition rating; whether the parcel lies within a dam-failure inundation "
         "area; and any easement, setback or construction restriction attaching to the levee."),
        ("Building envelope on a narrow parcel",
         "The parcel measures roughly 479 ft by 123 ft. Against the pad footprint the report assumes, "
         "the narrow dimension leaves only about 12 ft of spare width. Please confirm the applicable "
         "front, side and rear building lines of record so the envelope can be tested before purchase."),
        ("Recorded drainage easements",
         "The restrictions of record for this section reference drainage easements at 1712/500. Please "
         "confirm whether any mapped drainage easement crosses this parcel."),
    ],
}

# The ten questions every letter asks, in the order they matter for a purchase decision.
COMMON = [
    ("Written base flood elevation",
     "The base flood elevation the county applies to this parcel, in feet NAVD88, and the source used to "
     "derive it — the Flood Insurance Study profile and cross-section, or the published BFE line, with "
     "the method of interpolation if one is used."),
    ("Regulatory floodway",
     "Whether any part of the parcel lies within the regulatory floodway as opposed to the flood fringe."),
    ("Minimum finished-floor elevation",
     "Confirmation of the minimum finished-floor elevation the county will require. Our understanding is "
     "the base flood elevation plus 24 inches of freeboard, being a single requirement of 24 inches "
     "rather than 24 inches in addition to a further two feet. Please correct that if it is wrong, and "
     "state any additional local standard that applies."),
    ("Levee status relied upon",
     "The accreditation status of the Angleton Levee as relied upon in the current mapping, and whether "
     "any Letter of Map Revision, physical map revision or preliminary FIRM is pending that would change "
     "the zone or the base flood elevation for this parcel."),
    ("Fill, no-rise and drainage",
     "Whether raising a building pad on this parcel requires a no-rise certification, compensatory "
     "storage, or a drainage review, and confirmation that a Fill and Grading permit is required in "
     "addition to the development permit."),
    ("Map amendment on natural grade",
     "Whether the county considers this parcel a candidate for a Letter of Map Amendment on natural "
     "grade, and confirmation that placing fill under the structure would instead require a Letter of "
     "Map Revision based on fill."),
    ("Permit route and fees",
     "Confirmation that a single combined Development and Building Permit applies, the fee basis for a "
     "single-family residence in a flood zone, and that all contractors must hold county IRC "
     "registration before the permit issues."),
    ("Elevation certificate",
     "At what stage an elevation certificate is required, and the form the county accepts."),
    ("Jurisdiction",
     "Confirmation that this parcel is in unincorporated Brazoria County and not within the city limits "
     "or extraterritorial jurisdiction of Angleton, so that the county is the permitting authority."),
    ("Substantial-damage and repetitive-loss history",
     "Any record the county holds of flooding, substantial damage or repetitive loss affecting this "
     "parcel or its immediate street."),
]

CSS = """
@page{size:A4; margin:22mm 20mm 20mm;}
*{box-sizing:border-box;}
body{margin:0; font:10.5pt/1.5 Georgia,"Times New Roman",serif; color:#16262c;}
.letter{page-break-after:always;}
.letter:last-child{page-break-after:auto;}
.hd{display:flex; justify-content:space-between; align-items:flex-start;
    border-bottom:2px solid #16262c; padding-bottom:4mm; margin-bottom:6mm;}
.from{font-size:9pt; line-height:1.45;}
.from .nm{font-weight:700; font-size:11.5pt; font-family:-apple-system,"Segoe UI",Roboto,Helvetica,sans-serif;}
.ref{text-align:right; font-size:8.4pt; color:#54666d; font-family:-apple-system,"Segoe UI",Roboto,Helvetica,sans-serif;}
.ref b{color:#16262c;}
.to{font-size:10pt; line-height:1.45; margin-bottom:5mm;}
.to .of{font-weight:700;}
.subj{font-family:-apple-system,"Segoe UI",Roboto,Helvetica,sans-serif; font-size:10pt;
      font-weight:700; margin:5mm 0 4mm; padding:2.5mm 3mm; background:#eef2f2;
      border-left:3px solid #0f766e;}
p{margin:0 0 3.2mm;}
h2{font-family:-apple-system,"Segoe UI",Roboto,Helvetica,sans-serif; font-size:8.2pt;
   text-transform:uppercase; letter-spacing:.09em; color:#54666d; margin:6mm 0 2mm;}
table.rec{width:100%; border-collapse:collapse; font-size:9pt; margin:0 0 4mm;
          font-family:-apple-system,"Segoe UI",Roboto,Helvetica,sans-serif;}
table.rec th,table.rec td{border:1px solid #dde4e6; padding:1.6mm 2.4mm; text-align:left;
                          vertical-align:top;}
table.rec th{width:42mm; background:#f5f8f8; font-weight:600; color:#54666d;}
ol.q{margin:0 0 4mm; padding-left:7mm;}
ol.q li{margin:0 0 2.6mm;}
ol.q b{font-family:-apple-system,"Segoe UI",Roboto,Helvetica,sans-serif; font-size:9.4pt;}
.sig{margin-top:8mm;}
.sig .rule{border:0; border-top:1px solid #c3ced2; width:62mm; margin:12mm 0 1.5mm;}
.note{font-size:8.6pt; color:#54666d; background:#f5f8f8; border-left:3px solid #a8560a;
      padding:2.4mm 3mm; margin:5mm 0 0; font-family:-apple-system,"Segoe UI",Roboto,Helvetica,sans-serif;}
.foot{margin-top:6mm; padding-top:2.5mm; border-top:1px solid #dde4e6; font-size:7.8pt;
      color:#8d9a9f; font-family:-apple-system,"Segoe UI",Roboto,Helvetica,sans-serif;}
"""


def letter_html(p, f, single=True):
    lot = p['lot']
    extra = EXTRA.get(lot, [])
    questions = COMMON + extra
    qs = ''.join('<li><b>%s.</b> %s</li>' % (t, b) for t, b in questions)

    water = p.get('nearest_water') or []
    wbits = []
    for w in water[:2]:
        nm = w.get('name') or 'unnamed water body'
        wbits.append('%s, about %s ft' % (nm, format(int(w['ft']), ',d')))
    wtxt = '; '.join(wbits) if wbits else 'not established'

    return """
<div class="letter">
  <div class="hd">
    <div class="from">
      <div class="nm">%(who)s</div>
      %(addr1)s<br>%(addr2)s<br>%(tel)s<br>%(email)s
    </div>
    <div class="ref">
      <b>%(dated)s</b><br>
      Our ref: BFE/%(pid)s<br>
      Parcel %(lotn)d of 4
    </div>
  </div>

  <div class="to">
    <div class="of">The Floodplain Administrator</div>
    %(office)s<br>%(body)s<br>%(a1)s<br>%(a2)s<br>
    %(ctel)s &nbsp;/&nbsp; %(ctel2)s
  </div>

  <div class="subj">
    Request for a written Base Flood Elevation determination<br>
    %(name)s &mdash; PID %(pid)s &mdash; %(acres)s acres of record, %(sub)s
  </div>

  <p>Dear Floodplain Administrator,</p>

  <p>I am evaluating the vacant parcel identified below for the construction of a single-family
  residence, and I should be grateful for a written determination of the base flood elevation that
  applies to it, together with confirmation of the points listed overleaf. I am not yet under contract;
  the purpose of this request is to establish the regulatory position before committing to a purchase
  or to a design.</p>

  <h2>The parcel</h2>
  <table class="rec">
    <tr><th>Marketed as</th><td>%(name)s, Angleton, Texas 77515</td></tr>
    <tr><th>Situs of record</th><td>%(situs)s</td></tr>
    <tr><th>Account / PID</th><td>%(pid)s &nbsp;&middot;&nbsp; GEO ID %(geo)s</td></tr>
    <tr><th>Legal description</th><td>%(legal)s</td></tr>
    <tr><th>Acreage of record</th><td>%(acres)s acres</td></tr>
    <tr><th>Subdivision and plat</th><td>%(sub)s &nbsp;&middot;&nbsp; plat %(plat)s</td></tr>
    <tr><th>Deed reference</th><td>%(deed)s</td></tr>
    <tr><th>Approximate centroid</th><td>%(lat).6f, %(lon).6f</td></tr>
  </table>

  <h2>Our present understanding, for correction</h2>
  <table class="rec">
    <tr><th>FEMA zone</th><td>Zone %(zone)s, special flood hazard area</td></tr>
    <tr><th>FIRM panel</th><td>%(panel)s, effective %(peff)s</td></tr>
    <tr><th>Nearest published BFE</th><td>%(bfe).1f ft NAVD88, the line lying about %(bfeaway)s ft
      from the parcel</td></tr>
    <tr><th>Natural ground</th><td>about %(gmin).1f to %(gmax).1f ft NAVD88 across the parcel,
      averaging %(gmean).1f ft, from county LiDAR and the USGS 1 m elevation model</td></tr>
    <tr><th>Nearest water</th><td>%(wtxt)s</td></tr>
    <tr><th>Assumed finished floor</th><td>%(ffe).1f ft NAVD88, being the published BFE plus
      %(fb)d inches of freeboard</td></tr>
  </table>

  <p>On that basis the parcel appears to need an engineered pad lifting the building area by
  approximately %(lift).1f ft to reach a compliant finished floor. That figure is derived from remote
  sensing rather than survey, which is one reason I am asking the county to state the governing
  elevation in writing.</p>

  <h2>Points on which I request confirmation</h2>
  <ol class="q">%(qs)s</ol>

  <p>If any of the figures above is wrong, I would be glad to be corrected &mdash; establishing the
  right numbers now is the object of the exercise. If a fee or a formal application is required for a
  written determination, please tell me the amount and the form to use and I will submit it promptly.</p>

  <p>I am writing from out of state, so a reply by e-mail to <b>%(email)s</b> would be most helpful, and
  I am reachable on %(tel)s during Pacific business hours. I am glad to telephone the office if that is
  easier than writing.</p>

  <p>Thank you for your assistance.</p>

  <div class="sig">
    <p>Yours faithfully,</p>
    <hr class="rule">
    <div><b>%(who)s</b></div>
  </div>

  %(note)s

  <div class="foot">
    Parcel figures are drawn from the Brazoria County Appraisal District record, the county public GIS
    services and the USGS 3DEP elevation model, as compiled in the four-lot feasibility portfolio
    v3.5. They are stated for correction, not as assertions of fact.
  </div>
</div>""" % {
        'who': PREPARED_FOR,
        'addr1': SENDER['addr1'], 'addr2': SENDER['addr2'],
        'tel': SENDER['tel'], 'email': SENDER['email'],
        'dated': DATED,
        'lotn': lot,
        'office': COUNTY['office'], 'body': COUNTY['body'],
        'a1': COUNTY['addr1'], 'a2': COUNTY['addr2'],
        'ctel': COUNTY['tel'], 'ctel2': COUNTY['tel2'],
        'name': p['listing_name'], 'situs': p['situs_of_record'],
        'pid': p['pid'], 'geo': p['geo_id'], 'legal': p['legal_description'],
        'acres': p['acres_of_record'], 'sub': p['subdivision'], 'plat': p['plat'],
        'deed': p['deed_reference'],
        'lat': p['centroid'][0], 'lon': p['centroid'][1],
        'zone': p['fema_zone_2020'], 'panel': PANEL, 'peff': PANEL_EFF,
        'bfe': p['nearest_published_bfe_ft_navd88'],
        'bfeaway': format(int(p['nearest_bfe_line_ft_away']), ',d'),
        'gmin': f['ground_min_ft'], 'gmax': f['ground_max_ft'], 'gmean': f['ground_mean_ft'],
        'wtxt': wtxt, 'ffe': FFE_FT, 'fb': FREEBOARD_IN, 'lift': f['lift_ft'],
        'qs': qs,
        'note': ('<div class="note">This is one of four parcels I am evaluating in Bar X Ranch. '
                 'A combined request covering all four is available if the office would prefer to '
                 'answer them together.</div>') if single else '',
    }


# ------------------------------------------------------------------------------ e-mails
def email_text(p, f):
    lot = p['lot']
    extra = EXTRA.get(lot, [])
    lines = []
    lines.append('Subject: BFE determination request — %s (PID %s), Bar X Ranch, Angleton'
                 % (p['listing_name'], p['pid']))
    lines.append('To: Brazoria County Floodplain & 911 Administration')
    lines.append('')
    lines.append('Dear Floodplain Administrator,')
    lines.append('')
    lines.append('I am evaluating the vacant parcel below for a single-family residence and would be')
    lines.append('grateful for a written determination of the base flood elevation that applies to it.')
    lines.append('I am not yet under contract; I am trying to establish the regulatory position before')
    lines.append('committing to a purchase or a design.')
    lines.append('')
    lines.append('  Marketed as       %s, Angleton, TX 77515' % p['listing_name'])
    lines.append('  Situs of record   %s' % p['situs_of_record'])
    lines.append('  Account / PID     %s  (GEO ID %s)' % (p['pid'], p['geo_id']))
    lines.append('  Legal             %s' % p['legal_description'])
    lines.append('  Acreage of record %s acres' % p['acres_of_record'])
    lines.append('  Subdivision       %s, plat %s' % (p['subdivision'], p['plat']))
    lines.append('  Centroid          %.6f, %.6f' % (p['centroid'][0], p['centroid'][1]))
    lines.append('')
    lines.append('My present understanding, which I would be glad to have corrected:')
    lines.append('')
    lines.append('  - Zone %s, FIRM panel %s effective %s' % (p['fema_zone_2020'], PANEL, PANEL_EFF))
    lines.append('  - Nearest published BFE %.1f ft NAVD88, about %s ft from the parcel'
                 % (p['nearest_published_bfe_ft_navd88'],
                    format(int(p['nearest_bfe_line_ft_away']), ',d')))
    lines.append('  - Natural ground about %.1f-%.1f ft NAVD88 (LiDAR / USGS 1 m DEM)'
                 % (f['ground_min_ft'], f['ground_max_ft']))
    lines.append('  - Assumed finished floor %.1f ft NAVD88 = BFE + %d in freeboard'
                 % (FFE_FT, FREEBOARD_IN))
    lines.append('  - Implied pad lift about %.1f ft' % f['lift_ft'])
    lines.append('')
    lines.append('Could you please confirm:')
    lines.append('')
    for i, (t, b) in enumerate(COMMON + extra, start=1):
        lines.append('  %2d. %s' % (i, t))
        for ln in wrap(b, 72):
            lines.append('      %s' % ln)
    lines.append('')
    lines.append('If a fee or a formal application is needed for a written determination, please tell me')
    lines.append('the amount and the form and I will submit it promptly.')
    lines.append('')
    lines.append('I am writing from out of state, so a reply to this address is most helpful; I am also')
    lines.append('reachable on %s during Pacific business hours.' % SENDER['tel'])
    lines.append('')
    lines.append('With thanks,')
    lines.append(SENDER['name'])
    lines.append('%s, %s' % (SENDER['addr1'], SENDER['addr2']))
    lines.append('%s · %s' % (SENDER['tel'], SENDER['email']))
    return '\n'.join(lines)


def wrap(s, w):
    out, cur = [], ''
    for word in s.split():
        if len(cur) + len(word) + 1 > w:
            out.append(cur)
            cur = word
        else:
            cur = (cur + ' ' + word).strip()
    if cur:
        out.append(cur)
    return out


def page(inner, title):
    return ('<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><title>%s</title>'
            '<style>%s</style></head><body>%s</body></html>' % (title, CSS, inner))


def to_pdf(html, path, tag):
    tmp = path + '.html'
    open(tmp, 'w').write(html)
    subprocess.run([CHROME, '--headless', '--disable-gpu', '--no-sandbox',
                    '--virtual-time-budget=6000', '--no-pdf-header-footer',
                    '--print-to-pdf=' + path, 'file://' + tmp],
                   capture_output=True, timeout=180)
    os.remove(tmp)
    try:
        from pypdf import PdfReader
        n = len(PdfReader(path).pages)
    except Exception:
        n = 0
    print('  %-52s %2d pp  %6.0f kB' % (tag, n, os.path.getsize(path) / 1024))
    return n


def slug(s):
    return (s.replace(' ', '-').replace('/', '-')
             .replace('--', '-'))


def main():
    os.makedirs(OUTDIR, exist_ok=True)
    gj = json.load(open(os.path.join(ROOT, 'data', 'parcels.geojson')))
    fill = json.load(open(os.path.join(ROOT, 'data', 'fill.json')))['lots']

    parcels = []
    for feat in gj['features']:
        p = feat['properties']
        parcels.append((p, fill['lot%d' % p['lot']]))
    parcels.sort(key=lambda t: t[0]['lot'])

    print('individual letters')
    singles, emails = [], []
    for p, f in parcels:
        name = 'BFE-Request-%s.pdf' % slug(p['listing_name'])
        to_pdf(page(letter_html(p, f, single=True), p['listing_name']),
               os.path.join(OUTDIR, name), name)
        singles.append(letter_html(p, f, single=False))
        emails.append(email_text(p, f))

    print('combined')
    comb = 'BFE-Request-All-Four-Lots.pdf'
    cover = """
<div class="letter">
  <div class="hd">
    <div class="from"><div class="nm">%s</div>%s<br>%s<br>%s<br>%s</div>
    <div class="ref"><b>%s</b><br>Our ref: BFE/BARX-4<br>Four parcels</div>
  </div>
  <div class="to"><div class="of">The Floodplain Administrator</div>
    %s<br>%s<br>%s<br>%s<br>%s &nbsp;/&nbsp; %s</div>
  <div class="subj">Request for written Base Flood Elevation determinations &mdash;
    four parcels in Bar X Ranch, Angleton</div>
  <p>Dear Floodplain Administrator,</p>
  <p>I am evaluating four vacant parcels in Bar X Ranch for the construction of a single-family
  residence, and expect to purchase one of them. I should be grateful for a written determination of
  the base flood elevation applying to each, together with confirmation of the points set out in the
  individual letters that follow.</p>
  <p>The four parcels are:</p>
  <table class="rec">
    <tr><th>Parcel</th><td><b>PID</b> &middot; legal description &middot; acreage of record</td></tr>
    %s
  </table>
  <p>Each parcel is covered by its own letter overleaf, because the questions differ between them &mdash;
  one adjoins Mill Bayou, one sits beside Flag Pond and the Flag Lake Levee, one has an apparent
  discrepancy in its address of record, and one stands appreciably higher than the rest. The ten
  questions common to all four are repeated in each letter so that any one of them can be answered on
  its own.</p>
  <p>If it is easier for the office to answer all four together in a single reply, that would suit me
  well. If a fee or a formal application is required, please tell me the amount and the form and I will
  submit it promptly.</p>
  <p>Thank you for your assistance.</p>
  <div class="sig"><p>Yours faithfully,</p><hr class="rule"><div><b>%s</b></div></div>
  <div class="foot">Compiled from the Brazoria County Appraisal District record, the county public GIS
  services and the USGS 3DEP elevation model &mdash; four-lot feasibility portfolio v3.5. Figures are
  stated for correction, not as assertions of fact.</div>
</div>""" % (
        PREPARED_FOR, SENDER['addr1'], SENDER['addr2'], SENDER['tel'], SENDER['email'],
        DATED,
        COUNTY['office'], COUNTY['body'], COUNTY['addr1'], COUNTY['addr2'],
        COUNTY['tel'], COUNTY['tel2'],
        ''.join('<tr><th>%s</th><td><b>%s</b> &middot; %s &middot; %s ac</td></tr>'
                % (p['listing_name'], p['pid'], p['legal_description'], p['acres_of_record'])
                for p, _ in parcels),
        PREPARED_FOR)
    to_pdf(page(cover + ''.join(singles), 'BFE requests — four parcels'),
           os.path.join(OUTDIR, comb), comb)

    md = ['# Draft e-mails — Brazoria County Floodplain & 911 Administration',
          '',
          'Four requests for a written base flood elevation determination, one per parcel. Plain text,',
          'ready to send as they stand.',
          '',
          '- **To:** Brazoria County %s, %s, %s' % (COUNTY['office'].replace('&amp;', '&'),
                                                    COUNTY['addr1'], COUNTY['addr2']),
          '- **Telephone:** %s or %s' % (COUNTY['tel'], COUNTY['tel2']),
          '- The same requests as formal letters, ready to print, are the PDFs in this folder.',
          '',
          'Every figure quoted is drawn from `data/parcels.geojson` and `data/fill.json`, so these',
          'drafts stay in step with the report. Regenerate them with `python3 tools/letters.py`.',
          '']
    for (p, _), body in zip(parcels, emails):
        md += ['---', '', '## Lot %d — %s' % (p['lot'], p['listing_name']),
               '', '```text', body, '```', '']
    open(os.path.join(OUTDIR, 'EMAIL-DRAFTS.md'), 'w').write('\n'.join(md) + '\n')
    print('  %-52s %6.0f kB' % ('EMAIL-DRAFTS.md',
                                os.path.getsize(os.path.join(OUTDIR, 'EMAIL-DRAFTS.md')) / 1024))


if __name__ == '__main__':
    main()
