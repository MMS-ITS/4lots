#!/usr/bin/env python3
"""Build index.html — the Bar X Ranch 4-lot feasibility portfolio, v3.0.

Emits a paginated A4 artifact with running page numbers. All figures are baked in
as literals so the build is reproducible from the repository alone; the parcel
geometry is read from data/parcels.geojson (retrieved from Brazoria County's
public ArcGIS service — see docs/EVIDENCE.md for the queries).

    python3 tools/build_artifact.py

Written for: Mohsin Chowdhury.
"""
import json
import os
import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GEOJSON = os.path.join(ROOT, 'data', 'parcels.geojson')
OUT = os.path.join(ROOT, 'index.html')

PREPARED_FOR = "Mohsin Chowdhury"
PREPARED_ON = "11 September 2026"
VERSION = "3.0"

# --------------------------------------------------------------------------- data
gj = json.load(open(GEOJSON))
LOTS = {f['id']: f['properties'] for f in gj['features']}
RINGS = {f['id']: f['geometry']['coordinates'] for f in gj['features']}
ORDER = ['lot1', 'lot2', 'lot3', 'lot4']

# Per-lot narrative facts established by the desktop verification pass.
EXTRA = {
    'lot1': dict(
        short="1127 Saddle Horn Bend",
        badges=[('ae', 'Zone AE'), ('wf', 'Waterfront — Mill Bayou'), ('q', 'Largest — 1.95 ac')],
        water="Mill Bayou. 19 of the 40 recorded boundary vertices lie within 60 ft of a "
              "13.0-acre mapped water body; the Mill Bayou centreline is 112 ft off the boundary.",
        frontage="Roughly half the perimeter is water frontage — the most of the four.",
        ground="24–25 ft at the parcel; 18–30 ft across the surrounding 600 ft "
               "(the 18 ft readings are the bayou channel itself).",
        sh35="0.09 mi (about 480 ft) south of State Highway 35",
        noise="Closest of the four to SH 35 — expect audible highway traffic.",
        best="Setback geometry. The extra acre is the only thing on offer here that actually "
             "solves the 5BR + drainfield + 100% reserve + well-spacing puzzle comfortably.",
        watch="Longest water frontage means the largest share of the lot is in the low ground "
              "near the channel, and the TCEQ 75 ft absorption setback bites along all of it. "
              "It also sits downstream of Bar X Development Dam (NID TX01759) on a Mill Bayou "
              "tributary.",
        verdict="Buy this one if the plan is a large house and you will pay for the pad.",
    ),
    'lot2': dict(
        short="336 Wagon Wheel Trail W",
        badges=[('ae', 'Zone AE'), ('wf', 'Waterfront'), ('q', 'Lowest price'), ('etj', 'Baileys Prairie ETJ')],
        water="An unnamed 12.6-acre mapped water body. 4 of 12 boundary vertices lie within 60 ft "
              "of it — the shortest water frontage of the four.",
        frontage="A narrow slice of frontage on the short end of a long, thin lot.",
        ground="28 ft at the parcel; 21–29 ft across the surrounding 600 ft.",
        sh35="0.37 mi south of State Highway 35",
        noise="Far enough off SH 35 to be quiet; closest of the four to FM 521 (1.24 mi).",
        best="Lowest cash outlay, and the highest natural ground of the four at 28 ft — which is "
             "the single most valuable physical attribute in a Zone AE subdivision.",
        watch="The shape is the problem: 424 ft × 187 ft on 1.00 acre of record, and the county's "
              "own polygon computes to 0.872 acre. Fitting a 5BR footprint, a 2,250–4,500 sq ft "
              "spray field, a 100% reserve area and a well at 100 ft from the field on a 187 ft "
              "width is the tightest test in the portfolio. This is also the only lot inside the "
              "Baileys Prairie ETJ, so Baileys Prairie subdivision regulation reaches it.",
        verdict="Cheapest entry and the best ground, but prove the footprint fits before you bid.",
    ),
    'lot3': dict(
        short="Lot 29 Broken Arrow Trail",
        badges=[('ae', 'Zone AE'), ('wf', 'Waterfront — reclassified'), ('q', 'Best value'), ('q', '1.30 ac')],
        water="The same unnamed 12.6-acre water body as Lot 2. 7 of 13 boundary vertices lie "
              "within 60 ft of it.",
        frontage="Materially more frontage than Lot 2 on the same water body — and both earlier "
                 "versions of this study called this lot 'interior'.",
        ground="26 ft at the parcel (a 26 ft contour runs 3 ft from the centroid); 21–28 ft across "
               "the surrounding 600 ft.",
        sh35="0.10 mi (about 530 ft) south of State Highway 35",
        noise="Effectively tied with Lot 1 as the closest to the highway. Its situs of record is "
              "literally 'HIGHWAY 35'.",
        best="Value, on every measure that can be checked. It is the only lot priced below the "
             "county's own appraisal, the cheapest per acre by 11%, the second largest, and it is "
             "waterfront after all.",
        watch="Section 16 is governed by a different recorded restriction instrument (84-29/885, "
              "1984) from Sections 1 and 2, so the ACC rules are not necessarily the same ones "
              "quoted for the other lots. No street number has been assigned, so confirm the "
              "listing actually refers to PID 186219.",
        verdict="On the verified record this is the pick of the four. Confirm the identity first.",
    ),
    'lot4': dict(
        short="750 Wagon Wheel Trail",
        badges=[('ae', 'Zone AE'), ('wf', 'Waterfront — Flag Lake'), ('red', 'Abuts a dam'), ('q', 'Dearest / acre')],
        water="Flag Pond — a 101.5-acre lake, by far the largest water body in the study area. "
              "8 of 17 boundary vertices lie within 11 ft of both the pond and the Flag Lake "
              "Levee embankment (National Inventory of Dams ID TX06298).",
        frontage="Genuine big-lake frontage. This is the only one of the four on the main lake.",
        ground="24 ft at the parcel (a 24 ft contour passes within 1 ft of the centroid); "
               "23–30 ft across the surrounding 600 ft.",
        sh35="1.03 mi south of State Highway 35",
        noise="Quietest of the four by a wide margin — a mile off the highway.",
        best="The view and the water. If the point of the exercise is a lake house, this is the "
             "only lot that delivers a 101-acre lake rather than a 13-acre pond.",
        watch="Two things. It is 1.00 acre of record — <b>not</b> the 1.27 acres quoted from "
              "LoopNet — which makes it the most expensive land per acre in the portfolio by 28% "
              "over Lot 3. And the boundary is 11 ft from a levee embankment that impounds a "
              "101-acre lake; the National Inventory of Dams carries no hazard-potential "
              "classification and no condition rating for it.",
        verdict="Best lot to live on, worst lot to buy on price. The dam needs answering first.",
    ),
}
for k, v in EXTRA.items():
    LOTS[k].update(v)

# ------------------------------------------------------------------ climate (Celsius)
# ERA5 reanalysis at 29.139 N, 95.547 W, daily 1991-2020, aggregated to monthly means.
CLIMATE = [
    # month, high C, low C, rain mm, high F, low F
    ('Jan', 17.3, 9.3, 96, 63, 49), ('Feb', 19.1, 11.0, 79, 66, 52),
    ('Mar', 22.0, 14.1, 90, 72, 57), ('Apr', 25.2, 17.4, 96, 77, 63),
    ('May', 28.7, 21.5, 89, 84, 71), ('Jun', 31.2, 24.4, 107, 88, 76),
    ('Jul', 32.1, 25.2, 90, 90, 77), ('Aug', 32.5, 25.2, 98, 90, 77),
    ('Sep', 30.2, 23.1, 121, 86, 74), ('Oct', 26.7, 18.9, 109, 80, 66),
    ('Nov', 21.8, 14.0, 103, 71, 57), ('Dec', 18.3, 10.5, 99, 65, 51),
]
CLIM_ANN = dict(rain_mm=1177, rain_in=46.3, mean_c=21.7, hot_days=51,
                hot_min=14, hot_max=117, wettest_mm=2024, driest_mm=488)

# ------------------------------------------------------------------ FEMA National Risk Index
# Brazoria County (FIPS 48039), NRI version December 2025.
NRI = [
    # hazard, label, rating, annual frequency, county expected annual loss
    ('IFLD', 'Riverine flooding', 'Relatively High', '1.86 events/yr', '$78.2 m'),
    ('HRCN', 'Hurricane', 'Relatively High', '0.22 events/yr', '$43.6 m'),
    ('TRND', 'Tornado', 'Relatively High', '1.11 events/yr', '$20.9 m'),
    ('LTNG', 'Lightning', 'Relatively High', '70.0 events/yr', '$2.3 m'),
    ('ISTM', 'Ice storm', 'Relatively High', '—', '—'),
    ('CFLD', 'Coastal flooding', 'Relatively Moderate', '3.74 events/yr', '$2.0 m'),
    ('SWND', 'Strong wind', 'Relatively Moderate', '1.03 events/yr', '$0.8 m'),
    ('HWAV', 'Heat wave', 'Relatively Moderate', '14.9 events/yr', '$5.0 m'),
    ('CWAV', 'Cold wave', 'Relatively Moderate', '—', '—'),
    ('DRGT', 'Drought', 'Relatively Moderate', '28.5 months/yr affected', '$1.4 m'),
    ('HAIL', 'Hail', 'Relatively Low', '1.59 events/yr', '$0.4 m'),
    ('WFIR', 'Wildfire', 'Relatively Low', '0.004 events/yr', '$0.9 m'),
    ('WNTW', 'Winter weather', 'Very Low', '—', '—'),
    ('ERQK', 'Earthquake', 'Very Low', '—', '—'),
    ('LNDS', 'Landslide', 'Very Low', '—', '—'),
]

# ------------------------------------------------------------------ distances (OSRM road)
# from the portfolio centroid 29.13918 N, 95.54651 W
DIST = {
    'Daily essentials': [
        ('H-E-B supermarket, West Columbia', 6.7, 13, 'nearest full supermarket'),
        ('Valero fuel + convenience, Hwy 35', 4.2, 9, 'nearest fuel'),
        ('Walgreens pharmacy, West Columbia', 6.6, 13, 'nearest pharmacy'),
        ('Brazoria Community Library', 2.9, 11, 'nearest public building of any kind'),
        ('H-E-B supermarket, Angleton', 9.9, 18, ''),
        ('Kroger, Angleton', 10.1, 18, ''),
        ('Walmart Supercenter, Angleton', 10.2, 19, ''),
        ("Buc-ee's, Hwy 288", 7.4, 14, 'regional travel stop'),
        ('Angleton town centre / county courthouse', 9.0, 16, 'county seat'),
        ('Walmart Supercenter, Lake Jackson', 15.8, 26, ''),
    ],
    'Health care': [
        ('UTMB Health Urgent Care', 7.3, 14, 'nearest urgent care'),
        ('AngletonER (freestanding emergency)', 9.9, 18, '24 h emergency'),
        ('UTMB Health Angleton-Danbury Campus', 11.3, 20, 'nearest full hospital + ER'),
        ("Sweeny Community Hospital", 14.7, 27, ''),
        ("St Luke's Health Brazosport, Lake Jackson", 16.9, 27, 'larger acute hospital'),
        ('Memorial Hermann Sugar Land', 44.7, 66, ''),
        ('Texas Medical Center, Houston', 47.8, 63, 'tertiary / specialist care'),
    ],
    'Schools — Columbia-Brazoria ISD': [
        ('West Columbia Elementary', 7.0, 14, ''),
        ('Columbia High School', 7.1, 14, ''),
        ('Wild Peach Elementary', 12.3, 23, ''),
        ('West Brazos Junior High', 13.8, 24, ''),
        ('Brazosport College, Lake Jackson', 16.5, 27, 'nearest college (approx.)'),
    ],
    'Shopping, dining, going out': [
        ('Margarita Jones / Republic BBQ, West Columbia', 6.5, 12, 'nearest sit-down restaurants'),
        ("Elroy Floyd's / Damifino", 8.8, 16, 'nearest bars'),
        ('Cooter Browns Country Club, Brazoria', 8.9, 23, 'nearest live-music venue'),
        ('AMC Classic Brazos 14 cinema', 15.6, 26, 'nearest cinema'),
        ('Brazos Mall, Lake Jackson', 15.6, 26, 'nearest enclosed mall'),
        ('Wayside Pub, Lake Jackson', 16.4, 26, ''),
        ('Pearland Town Center', 36.3, 49, 'first large-format retail'),
        ('The Strand / downtown Galveston', 60.0, 92, 'nightlife district (approx.)'),
        ('Downtown Houston', 50.6, 67, 'full metropolitan nightlife'),
    ],
    'Coast, resorts and amusements': [
        ('The Wilderness Golf Course', 17.0, 28, 'nearest golf'),
        ('Sea Center Texas, Lake Jackson', 18.4, 29, 'aquarium + hatchery, free'),
        ('San Bernard National Wildlife Refuge', 19.1, 41, ''),
        ('Surfside Beach', 28.3, 42, 'nearest Gulf beach'),
        ('Brazos Bend State Park', 31.0, 51, ''),
        ('Space Center Houston', 44.9, 72, ''),
        ('Kemah Boardwalk', 51.0, 81, ''),
        ('Moody Gardens, Galveston', 59.4, 92, ''),
        ('San Luis Resort, Galveston', 59.0, 91, 'nearest full resort hotel'),
        ('Galveston Pleasure Pier / Schlitterbahn waterpark', 60.2, 91, 'Schlitterbahn is seasonal'),
        ('Galveston Island seawall', 61.2, 93, ''),
    ],
    'Indian community': [
        ("The Monk's Indian Bistro", 35.5, 48, 'nearest Indian restaurant'),
        ('Sri Meenakshi Temple, Pearland', 39.5, 58, 'largest South Indian temple in the region'),
        ('Gayatri Bhavan (South Indian)', 40.5, 58, ''),
        ('HMM Vitthal Rukmini Mandir, Rosenberg', 42.0, 58, ''),
        ('Desi Brothers Farmers Market, Sugar Land', 42.9, 62, 'nearest South Asian grocery'),
        ('BAPS Shri Swaminarayan Mandir, Stafford', 45.1, 67, ''),
        ('Mahatma Gandhi District (Hillcroft), Houston', 54.7, 73, 'main Indian commercial district'),
    ],
    'Airports': [
        ('Texas Gulf Coast Regional (LBX)', 11.8, 29, 'general aviation only — no scheduled service'),
        ('Houston Hobby (HOU)', 49.5, 71, 'nearest international airport'),
        ('Houston Bush Intercontinental (IAH)', 70.4, 95, 'long-haul hub'),
    ],
}

# ------------------------------------------------------------------ demographics (ACS 2024 5-yr)
DEMOG = [
    # metric, tract 6625, Brazoria County, Texas
    ('Population', '3,452', '391,255', '30,188,424'),
    ('Median age', '42.3', '36.7', '35.6'),
    ('Median household income', '$116,550', '$97,993', '$78,476'),
    ('Median owner-occupied home value', '$384,100', '$301,600', '$283,800'),
    ('Owner-occupied share of homes', '96.9%', '74.1%', '62.6%'),
    ('White alone', '76.4%', '47.7%', '48.5%'),
    ('Black or African American alone', '6.2%', '16.2%', '12.2%'),
    ('Asian alone', '0.2%', '7.4%', '5.6%'),
    ('Two or more races', '16.7%', '21.1%', '23.5%'),
    ('Hispanic or Latino (any race)', '29.6%', '31.6%', '39.7%'),
    ('Asian Indian (alone or in combination)', '0 of 3,452', '6,414 (1.6%)', '588,500 (1.9%)'),
]


DEMOG[-1] = ('Asian Indian (alone or in combination)', 'none reported',
             '6,414 (1.6%)', '588,500 (1.9%)')

# --------------------------------------------------------------------------- css
CSS = r"""
:root{
  --ink:#16262c; --muted:#54666d; --faint:#86959b; --line:#dde4e6; --line2:#c3ced2;
  --paper:#fff; --wash:#f5f8f8;
  --teal:#0f766e; --teal-w:#e7f2f0;
  --amber:#a8560a; --amber-w:#fdf2e3;
  --red:#a91f14; --red-w:#fdeae8;
  --green:#15602f; --green-w:#e7f2ea;
  --blue:#1c3ba8; --blue-w:#e9edf9;
  --violet:#5b21a6; --violet-w:#f0eafb;
}
*{box-sizing:border-box;}
html{-webkit-text-size-adjust:100%;}
body{
  margin:0; background:#e6ebec; color:var(--ink);
  font:9.7pt/1.42 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
  font-variant-numeric:tabular-nums;
}
a{color:var(--teal); text-decoration:none; border-bottom:.5pt solid rgba(15,118,110,.35);}

/* ---------------- the page ---------------- */
.sheet{
  width:210mm; min-height:297mm; margin:0 auto 8mm; padding:13mm 15mm 18mm;
  background:var(--paper); position:relative;
  box-shadow:0 1px 3px rgba(0,0,0,.10),0 8px 26px rgba(20,40,45,.13);
  break-before:page; page-break-before:always;
}
.sheet:first-of-type{break-before:auto; page-break-before:auto;}
.smark{display:block; font-size:1.5pt; line-height:1; color:#fff; height:1.5pt;
        overflow:hidden; user-select:none;}
.foot{
  position:absolute; left:15mm; right:15mm; bottom:8mm; height:11mm;
  border-top:.6pt solid var(--line2); padding-top:2mm;
  display:flex; justify-content:space-between; align-items:flex-start;
  font-size:7.4pt; letter-spacing:.02em; color:var(--faint);
}
.foot b{color:var(--muted); font-weight:600;}
.foot .pg{white-space:nowrap;}

/* ---------------- type ---------------- */
h1{font-size:24pt; line-height:1.08; letter-spacing:-.015em; margin:0 0 3mm;}
h2{font-size:13.5pt; line-height:1.13; margin:0 0 2.4mm; padding-top:2mm;
   border-top:2.2pt solid var(--ink);}
h2 .n{color:var(--teal);}
h3{font-size:8.2pt; text-transform:uppercase; letter-spacing:.1em; color:var(--muted);
   margin:3.6mm 0 1.2mm; font-weight:700;}
h4{font-size:11pt; margin:0 0 1mm;}
p{margin:0 0 2mm;}
.lead{font-size:10.4pt; color:var(--muted);}
small,.sm{font-size:8.4pt; color:var(--muted);}
.xs{font-size:7.6pt; color:var(--faint);}
ul.t,ol.t{margin:1.5mm 0 2.5mm; padding-left:5mm;}
ul.t li,ol.t li{margin:.8mm 0;}
ul.t.wide li{margin:1.2mm 0;}
hr.r{border:0; border-top:.6pt solid var(--line); margin:4mm 0;}

/* ---------------- cover ---------------- */
.kick{font-size:8pt; letter-spacing:.2em; text-transform:uppercase; color:var(--teal); font-weight:700;}
.cover-meta{display:grid; grid-template-columns:auto 1fr; gap:1.4mm 6mm; font-size:9pt; margin-top:4mm;}
.cover-meta dt{color:var(--faint); text-transform:uppercase; letter-spacing:.07em; font-size:7.6pt; padding-top:.5mm;}
.cover-meta dd{margin:0;}

/* ---------------- callouts ---------------- */
.note{border:.6pt solid var(--line); border-left-width:2.6pt; border-radius:1.4mm;
      padding:2.4mm 3mm; margin:2.4mm 0; background:var(--wash); font-size:8.9pt;
      line-height:1.48;}
.note .lbl{display:block; font-weight:700; text-transform:uppercase; letter-spacing:.07em;
           font-size:7.6pt; margin-bottom:1.2mm;}
.note.teal{border-left-color:var(--teal); background:var(--teal-w);} .note.teal .lbl{color:var(--teal);}
.note.amber{border-left-color:var(--amber); background:var(--amber-w);} .note.amber .lbl{color:var(--amber);}
.note.red{border-left-color:var(--red); background:var(--red-w);} .note.red .lbl{color:var(--red);}
.note.blue{border-left-color:var(--blue); background:var(--blue-w);} .note.blue .lbl{color:var(--blue);}
.note.green{border-left-color:var(--green); background:var(--green-w);} .note.green .lbl{color:var(--green);}
.note.violet{border-left-color:var(--violet); background:var(--violet-w);} .note.violet .lbl{color:var(--violet);}
.note p:last-child,.note ul:last-child,.note ol:last-child{margin-bottom:0;}

/* ---------------- confidence chips ---------------- */
.cf{display:inline-block; font-size:6.8pt; font-weight:700; letter-spacing:.05em;
    text-transform:uppercase; padding:.3mm 1.4mm; border-radius:1mm; vertical-align:.4mm;
    white-space:nowrap; border:.5pt solid transparent;}
.cf.v{background:var(--green-w); color:var(--green); border-color:rgba(21,96,47,.25);}
.cf.u{background:var(--amber-w); color:var(--amber); border-color:rgba(168,86,10,.25);}
.cf.e{background:var(--blue-w); color:var(--blue); border-color:rgba(28,59,168,.22);}
.cf.n{background:var(--violet-w); color:var(--violet); border-color:rgba(91,33,166,.22);}

/* ---------------- tables ---------------- */
table{width:100%; border-collapse:collapse; margin:2mm 0; font-size:8.2pt;}
caption{caption-side:top; text-align:left; font-size:8pt; color:var(--muted); margin-bottom:1.4mm;}
th,td{border:.5pt solid var(--line); padding:1.1mm 1.6mm; text-align:left; vertical-align:top;}
thead th{background:var(--ink); color:#fff; font-size:7.6pt; letter-spacing:.05em;
         text-transform:uppercase; font-weight:600; border-color:var(--ink);}
tbody tr:nth-child(even){background:var(--wash);}
td.n,th.n{text-align:right; white-space:nowrap;}
tr.tot td{font-weight:700; border-top:1.4pt solid var(--ink); background:#eaf0f0;}
tr.hi td{background:var(--green-w);}
.strike{color:var(--red); text-decoration:line-through;}
.bad{color:var(--red); font-weight:600;}
.fix{color:var(--green); font-weight:600;}
table.compact{font-size:7.7pt;} table.compact th,table.compact td{padding:.9mm 1.3mm;}
.rank{display:inline-block; width:4.4mm; height:4.4mm; line-height:4.4mm; text-align:center;
      border-radius:50%; background:var(--ink); color:#fff; font-size:7pt; font-weight:700;}
.rank.g{background:var(--green);} .rank.a{background:var(--amber);} .rank.r{background:var(--red);}

/* ---------------- KPI strip ---------------- */
.kpis{display:grid; grid-template-columns:repeat(4,1fr); gap:2.5mm; margin:3mm 0;}
.kpi{border:.6pt solid var(--line); border-top:2.2pt solid var(--ink); border-radius:1.2mm; padding:2.5mm 2.8mm;}
.kpi .k{font-size:7pt; letter-spacing:.08em; text-transform:uppercase; color:var(--faint); font-weight:700;}
.kpi .v{font-size:14pt; font-weight:700; margin:.8mm 0 .4mm; letter-spacing:-.015em; line-height:1.1;}
.kpi .d{font-size:7.6pt; color:var(--muted); line-height:1.35;}
.kpi.flag{border-top-color:var(--amber);} .kpi.good{border-top-color:var(--green);}
.kpi.bad{border-top-color:var(--red);}

/* ---------------- lot pages ---------------- */
.lothead{display:flex; justify-content:space-between; align-items:flex-start; gap:5mm;
         border-bottom:1.4pt solid var(--ink); padding-bottom:2.5mm; margin-bottom:3mm;}
.lothead .id{font-size:7.4pt; letter-spacing:.14em; text-transform:uppercase; color:var(--teal); font-weight:700;}
.lothead h2{border:0; padding:0; margin:.8mm 0 1mm; font-size:17pt;}
.lothead .addr{font-size:8.4pt; color:var(--muted);}
.lothead .price{text-align:right; white-space:nowrap;}
.lothead .price .p{font-size:17pt; font-weight:700; line-height:1.1;}
.lothead .price .pa{font-size:8pt; color:var(--muted);}
.badges{display:flex; gap:1.4mm; flex-wrap:wrap; margin:1.6mm 0 0;}
.badge{font-size:7pt; font-weight:700; letter-spacing:.04em; padding:.5mm 1.8mm;
       border-radius:1mm; text-transform:uppercase;}
.badge.ae{background:var(--amber-w); color:var(--amber);}
.badge.wf{background:var(--blue-w); color:var(--blue);}
.badge.q{background:#e9eeef; color:var(--muted);}
.badge.etj{background:var(--violet-w); color:var(--violet);}
.badge.red{background:var(--red-w); color:var(--red);}
.cols2{display:grid; grid-template-columns:1fr 1fr; gap:4mm;}
.cols2c{display:grid; grid-template-columns:1.15fr 1fr; gap:4mm;}
dl.facts{display:grid; grid-template-columns:30mm 1fr; gap:.6mm 2.6mm; margin:0; font-size:8.1pt;}
dl.facts dt{color:var(--faint); text-transform:uppercase; letter-spacing:.05em; font-size:7.2pt; padding-top:.5mm;}
dl.facts dd{margin:0;}

/* ---------------- maps & imagery ---------------- */
.map{position:relative; border:.6pt solid var(--line2); border-radius:1.4mm; overflow:hidden;
     background:#e9eeef; height:66mm;}
.map iframe{width:100%; height:100%; border:0; display:block;}
.map.tall{height:120mm;}
.map.short{height:58mm;}
.maplbl{position:absolute; top:0; left:0; background:rgba(22,38,44,.86); color:#fff;
        font-size:6.8pt; letter-spacing:.08em; text-transform:uppercase; font-weight:700;
        padding:.9mm 2mm; border-bottom-right-radius:1.2mm; z-index:2;}
.mapfall{display:none; padding:4mm; font-size:8.4pt; color:var(--muted);}
.mapfall b{color:var(--ink);}
.shots{display:grid; grid-template-columns:repeat(3,1fr); gap:2mm; margin:2.5mm 0;}
.shot{position:relative; aspect-ratio:4/3; border:.6pt solid var(--line2); border-radius:1.2mm;
      overflow:hidden; background:var(--wash);}
.shot img{width:100%; height:100%; object-fit:cover; display:block;}
.shot .ph{position:absolute; inset:0; display:flex; flex-direction:column; justify-content:center;
          align-items:center; text-align:center; padding:2mm; gap:1mm;
          background:repeating-linear-gradient(45deg,#f2f6f6,#f2f6f6 3mm,#eaf0f0 3mm,#eaf0f0 6mm);}
.shot .ph .t{font-size:7pt; font-weight:700; letter-spacing:.06em; text-transform:uppercase; color:var(--muted);}
.shot .ph .s{font-size:6.6pt; color:var(--faint); line-height:1.35;}
.linkrow{display:flex; flex-wrap:wrap; gap:1.5mm; margin:2mm 0;}
.lnk{font-size:7.6pt; font-weight:600; padding:1mm 2.2mm; border:.6pt solid var(--line2);
     border-radius:1mm; background:var(--wash); color:var(--teal); border-bottom-width:.6pt;}
.lnk.g{background:var(--teal); color:#fff; border-color:var(--teal);}
.tabs{display:flex; gap:1.2mm; margin:0 0 2mm; flex-wrap:wrap;}
.tab{font-size:7.6pt; font-weight:700; letter-spacing:.04em; padding:1.1mm 2.6mm; cursor:pointer;
     border:.6pt solid var(--line2); border-radius:1mm; background:#fff; color:var(--muted);}
.tab[aria-selected=true]{background:var(--ink); color:#fff; border-color:var(--ink);}
#leaf{height:118mm; border:.6pt solid var(--line2); border-radius:1.4mm; background:#e9eeef;}
.leg{display:flex; flex-wrap:wrap; gap:1mm 4mm; font-size:7.6pt; color:var(--muted); margin-top:1.5mm;}
.leg i{display:inline-block; width:3mm; height:3mm; border-radius:.6mm; vertical-align:-.3mm; margin-right:1mm;}

/* ---------------- misc ---------------- */
.toc{display:grid; grid-template-columns:1fr 1fr; gap:0 8mm;}
.toc ol{margin:0; padding-left:6mm; font-size:9.2pt;}
.toc li{margin:1.2mm 0;}
.toc .pgn{float:right; color:var(--faint); font-size:8pt;}
.legend{display:flex; gap:4mm; flex-wrap:wrap; font-size:8pt; color:var(--muted); margin:2.5mm 0;}
.bars{font-size:8.6pt;}
.bar{display:grid; grid-template-columns:38mm 1fr auto; gap:2.5mm; align-items:center; margin:1.3mm 0;}
.bar .t{color:var(--muted);}
.bar .track{height:3.4mm; background:#eaf0f0; border-radius:.8mm; overflow:hidden;}
.bar .fill{height:100%; background:var(--teal);}
.bar .fill.a{background:var(--amber);} .bar .fill.r{background:var(--red);}
.bar .fill.g{background:var(--green);} .bar .fill.b{background:var(--blue);}
.bar .v{font-weight:600; font-size:8.2pt; white-space:nowrap;}
.sig{border:.6pt solid var(--line2); border-top:2.2pt solid var(--ink); border-radius:1.4mm;
     padding:5mm 6mm; margin-top:5mm; background:var(--wash);}
.sig .for{font-size:7.6pt; letter-spacing:.14em; text-transform:uppercase; color:var(--faint); font-weight:700;}
.sig .who{font-size:16pt; font-weight:700; letter-spacing:-.01em; margin:1.2mm 0 .8mm;}
.sig .on{font-size:9.4pt; color:var(--muted);}

@media screen and (max-width:230mm){
  .sheet{width:100%; min-height:0; padding:8mm 6mm 22mm; margin-bottom:4mm;}
  .kpis{grid-template-columns:repeat(2,1fr);}
  .cols2,.cols2c{grid-template-columns:1fr;}
  .toc{grid-template-columns:1fr;}
  .shots{grid-template-columns:repeat(2,1fr);}
  dl.facts{grid-template-columns:1fr;}
  dl.facts dt{margin-top:1.5mm;}
  .foot{position:static; margin-top:6mm; left:auto; right:auto; bottom:auto; height:auto;}
}
@media print{
  @page{
    size:A4; margin:13mm 15mm 14mm;
    @bottom-left{
      content:"Bar X Ranch — Four-Lot Feasibility Portfolio v3.0 · prepared for Mohsin Chowdhury · 11 September 2026";
      font-family:-apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
      font-size:7.2pt; color:#86959b; vertical-align:top; padding-top:3mm;
    }
    @bottom-right{
      content:"Page " counter(page) " of " counter(pages);
      font-family:-apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
      font-size:7.4pt; font-weight:700; color:#54666d; vertical-align:top; padding-top:3mm;
    }
  }
  body{background:#fff;}
  .sheet{margin:0; box-shadow:none; width:auto; min-height:0; padding:0;}
  .foot{display:none !important;}
  .noprint{display:none !important;}
  .map{height:auto; border-style:dashed; background:#fff;}
  .map iframe{display:none;}
  .mapfall{display:block;}
  #leaf{display:none;}
  .tabs{display:none;}
  a{color:var(--ink); border-bottom:0;}
  .shot .ph{background:#f6f8f8;}
  h2,h3{break-after:avoid; page-break-after:avoid;}
  table,.note,.lot,.kpi,svg.dwg,.shots{break-inside:avoid; page-break-inside:avoid;}
  tr{break-inside:avoid;}
}
"""


# --------------------------------------------------------------------------- helpers
SHEETS = []   # (anchor, foot_label, html)


def add(html, foot, anchor=None):
    SHEETS.append((anchor, foot, html))


def gmap_lot(p, z=18):
    lat, lon = p['centroid']
    return ("https://maps.google.com/maps?q=%.6f,%.6f&z=%d&t=k&hl=en&output=embed"
            % (lat, lon, z))


def gmap_all(z=15):
    a = [LOTS[k]['centroid'] for k in ORDER]
    return ("https://maps.google.com/maps?f=d&saddr=%.6f,%.6f&daddr=%.6f,%.6f+to:%.6f,%.6f"
            "+to:%.6f,%.6f&t=k&hl=en&output=embed"
            % (a[0][0], a[0][1], a[1][0], a[1][1], a[2][0], a[2][1], a[3][0], a[3][1]))


GMAP_AREA = ("https://maps.google.com/maps?q=Bar+X+Ranch,+Angleton,+TX+77515"
             "&z=14&t=k&hl=en&output=embed")


def gmap_link(p):
    lat, lon = p['centroid']
    return "https://www.google.com/maps/search/?api=1&query=%.6f,%.6f" % (lat, lon)


def gsv_link(p):
    lat, lon = p['centroid']
    return ("https://www.google.com/maps/@?api=1&map_action=pano&viewpoint=%.6f,%.6f"
            % (lat, lon))


def zillow_link(addr):
    return "https://www.zillow.com/homes/%s,-Angleton,-TX-77515_rb/" % addr.replace(' ', '-')


def mapbox(label, src, fallback, cls="map"):
    return ('<div class="%s"><span class="maplbl noprint">%s</span>'
            '<iframe src="%s" loading="lazy" referrerpolicy="no-referrer-when-downgrade" '
            'title="%s"></iframe><div class="mapfall">%s</div></div>'
            % (cls, label, src, label, fallback))


def map_fallback(p):
    lat, lon = p['centroid']
    return ("<b>%s — live satellite map.</b> Interactive in the browser version; "
            "this is a printed copy.<br>Parcel centroid <b>%.6f, %.6f</b> · "
            "PID %s · %s<br><span class='xs'>Open: google.com/maps/search/?api=1&amp;query=%.6f,%.6f</span>"
            % (p['short'], lat, lon, p['pid'], p['legal_description'], lat, lon))


def shot(lot_n, i, title, sub):
    return ('<div class="shot"><img src="assets/photos/lot%d-%d.jpg" alt="%s" '
            'onload="this.parentNode.querySelector(\'.ph\').style.display=\'none\'">'
            '<div class="ph"><span class="t">%s</span><span class="s">%s</span></div></div>'
            % (lot_n, i, title, title, sub))


def bar(label, value, pct, cls=''):
    return ('<div class="bar"><span class="t">%s</span><span class="track">'
            '<span class="fill %s" style="width:%.1f%%"></span></span>'
            '<span class="v">%s</span></div>' % (label, cls, max(1.0, pct), value))


def table(head, rows, caption=None, cls='', foot=None):
    h = '<table class="%s">' % cls
    if caption:
        h += '<caption>%s</caption>' % caption
    h += '<thead><tr>' + ''.join(
        '<th%s>%s</th>' % (' class="n"' if c.startswith('~') else '', c.lstrip('~'))
        for c in head) + '</tr></thead><tbody>'
    for r in rows:
        cls_r = ''
        if isinstance(r, tuple) and len(r) == 2 and isinstance(r[1], str) and r[1] in ('tot', 'hi'):
            r, cls_r = r[0], r[1]
        h += '<tr%s>' % (' class="%s"' % cls_r if cls_r else '')
        for c, cell in zip(head, r):
            h += '<td%s>%s</td>' % (' class="n"' if c.startswith('~') else '', cell)
        h += '</tr>'
    h += '</tbody>'
    if foot:
        h += '<tfoot>%s</tfoot>' % foot
    return h + '</table>'


def lot_label(legal):
    """'... BLK 1 LOT 84 ACRES 1.95' -> 'Block 1, Lot 84'."""
    import re
    blk = re.search(r'BLK\s+(\S+)', legal)
    lot = re.search(r'\bLOT\s+([0-9A-Za-z-]+)', legal)
    parts = []
    if blk:
        parts.append('Block %s' % blk.group(1))
    if lot:
        parts.append('Lot %s' % lot.group(1))
    return ', '.join(parts) or '—'


CF = {'v': '<span class="cf v">verified</span>',
      'u': '<span class="cf u">unverified</span>',
      'e': '<span class="cf e">estimate</span>',
      'n': '<span class="cf n">new in v3</span>'}

# =========================================================================== 1. cover
add(f"""
<div class="kick">Independent feasibility review · third edition</div>
<h1>Bar X Ranch<br>Four-Lot Feasibility Portfolio</h1>
<p class="lead" style="margin-top:4mm;">Land acquisition and a five-bedroom build on four vacant
lots in Bar X Ranch, unincorporated Brazoria County, Angleton, Texas 77515 — assessed for
buildability, cost, flood and windstorm exposure, and what it is actually like to live there.</p>

<div class="note green" style="margin-top:6mm;">
  <span class="lbl">What is new in this edition</span>
  Every one of the four lots has now been <b>identified in the county record</b> — parcel ID, legal
  description, acreage of record, appraised value, deed reference — and checked against the county's
  own flood, LiDAR elevation, taxing-district and subdivision layers, the USDA soil survey, and the
  recorded deed restrictions. This edition adds <b>true-scale plans and terrain sections</b> for each
  lot (§11–15) and a chapter on <b>what living here is actually like</b> (§22–27). Nineteen open
  questions are closed, and <b>four conclusions change</b>: the FIRM panel, the governing base flood
  elevation, which lot is the best buy, and whether you can keep poultry.
</div>

<dl class="cover-meta">
  <dt>Prepared for</dt><dd><b>{PREPARED_FOR}</b></dd>
  <dt>Date</dt><dd>{PREPARED_ON}</dd>
  <dt>Version</dt><dd>{VERSION} — supersedes v2.0 (10 Sep 2026) and the original generated portfolio</dd>
  <dt>Subject</dt><dd>PID 183667 · 183367 · 186219 · 183332 — Bar X Ranch Sections 1, 2 and 16</dd>
  <dt>Asking price</dt><dd>$234,500 for 5.25 acres of record across four lots</dd>
  <dt>Basis</dt><dd>Primary regulation, Brazoria County public GIS, FEMA, TCEQ, TDI, TWIA,
      US Census ACS 2024, ERA5 climate reanalysis</dd>
  <dt>Status</dt><dd>Desktop study. No survey, no soil test, no written county flood determination.</dd>
</dl>

<div class="cols2" style="margin-top:6mm;">
  <div class="note amber" style="margin:0;">
    <span class="lbl">The number that changed the engineering</span>
    The nearest <b>published base flood elevation</b> on the effective FIRM is <b>28 ft NAVD88</b>,
    not the 24 ft assumed by both earlier editions. County LiDAR puts natural ground at these
    parcels at <b>24–28 ft</b>. Brazoria County requires a finished floor 24 in above BFE — so the
    target is <b>30 ft</b>, which is <b>2 to 6 ft above existing grade</b>. Building at grade is not
    an option on any of the four. See §10.
  </div>
  <div class="note red" style="margin:0;">
    <span class="lbl">The finding that changed the answer</span>
    Two of the four lots sit on <b>Pledger clay</b> — a 70% clay shrink-swell vertisol, hydrologic
    group D — and two on <b>Asa silty clay loam</b>, a well-drained prime-farmland loam. For a
    gardener who is also pouring a foundation and a septic field, that single difference outweighs
    every price gap in the portfolio. See §16.
  </div>
</div>
<div class="note violet" style="margin-top:3mm;">
  <span class="lbl">And the finding you need before you do anything else</span>
  The recorded restrictions allow one dwelling, one garage and <b>one horse barn</b> per lot, and bar
  <b>&ldquo;livestock of any kind other than house pets&rdquo;</b> apart from horses. <b>Chickens and ducks
  are very unlikely to be permitted.</b> See §1 and §17.
</div>

<p class="xs" style="margin-top:6mm;">This document is a desktop screening study prepared from
published regulation and public records. It is not a survey, an engineering opinion, a flood
determination, insurance advice, legal advice or an appraisal. Read the disclaimer on the final
page before relying on any figure in it.</p>
""", "Cover", "cover")

# =========================================================================== 2. contents
add("""
<h2><span class="n">Contents</span></h2>
@@TOC@@
<h3>How to read this document</h3>
<p>Every material figure carries a confidence chip. They are not decoration — the chips are the
point of the document, because the original portfolio presented estimates and errors in the same
typeface as facts.</p>
<div class="legend">
  <span>""" + CF['v'] + """ traced to a primary or official source and reproduced here</span>
  <span>""" + CF['u'] + """ from listing copy or a superseded edition; not confirmed</span>
  <span>""" + CF['e'] + """ a ranged planning figure, not a quote</span>
  <span>""" + CF['n'] + """ established for the first time in this edition</span>
</div>
<div class="note teal">
  <span class="lbl">Where the new evidence came from</span>
  Brazoria County publishes its GIS as an open ArcGIS service. This edition queries it directly for
  the parcel record, the FEMA flood layers, the LiDAR elevation contours, the taxing districts and
  the recorded subdivision instruments, then cross-checks the results against FEMA, TCEQ, TDI, TWIA,
  the US Census and OpenStreetMap. Every query is written down in
  <a href="docs/EVIDENCE.md">docs/EVIDENCE.md</a> so it can be re-run and disputed. The parcel
  polygons are committed to the repository as <a href="data/parcels.geojson">data/parcels.geojson</a>.
</div>
<div class="note amber">
  <span class="lbl">Three things this document still cannot tell you</span>
  <ul class="t" style="margin-bottom:0;">
    <li><b>The soil class.</b> It decides whether the septic system costs $8,000 or $25,000 — the
        single largest controllable cost swing in the project — and it can only be answered by a
        site and soil evaluation on the specific lot.</li>
    <li><b>The distance to three-phase power at each lot.</b> $0 or $25,000.</li>
    <li><b>The site-specific BFE in writing.</b> §10 narrows it hard, but only the Brazoria County
        Floodplain Administration can issue the determination a lender and an insurer will accept.</li>
  </ul>
</div>
""", "Contents", "toc")

# =========================================================================== 3. verdict
add("""
<h2><span class="n">1 ·</span> Verdict and recommendation</h2>
<p class="lead">You asked which one lot to buy and build on, weighted for gardening, hobby farming,
scenery, a good developed neighbourhood, quick access to amenities and safety from flood and storm.
Two findings in this edition decide it, and neither was in any earlier version.</p>

<div class="note red">
  <span class="lbl">Read this before anything else — poultry looks prohibited</span>
  <p>The recorded Bar X Ranch declaration of restrictions permits, on any lot, exactly
  <b>three structures</b>: one single-family dwelling, a garage, and <b>one horse barn</b> of no more
  than 30 × 25 ft (§3.01). And §3.15 provides that <b>&ldquo;no livestock of any kind other than house
  pets of reasonable kind and number may be kept on any Lot&rdquo;</b>, adding horses as the one express
  exception, on an acreage formula.</p>
  <p style="margin-bottom:0;"><b>Chickens and ducks are neither house pets nor horses.</b> On the face
  of the instrument, keeping them would need a written variance from the committee for the structure
  <em>and</em> a departure from the livestock clause. If poultry is non-negotiable for you, the honest
  answer is that <b>Bar X Ranch is the wrong subdivision</b> — buy unrestricted acreage in Brazoria
  County instead. Horses, unusually, are welcome: 1 per 32,670 sq ft, 2 per 42,000 sq ft.</p>
</div>

<div class="note green">
  <span class="lbl">If you buy here anyway, buy Lot 1 — 1127 Saddle Horn Bend</span>
  It is the only lot that delivers your three physical requirements together: <b>1.95 acres</b> of room
  (double the next largest), <b>Asa silty clay loam</b> — a well-drained prime-farmland loam that is
  genuinely good garden soil — and <b>roughly half its perimeter fronting Mill Bayou</b> for the
  scenery and wildlife. You pay for it: $82,500, a 26.9% premium over the county appraisal, and the
  deepest pad of the four.
</div>

<table class="compact">
  <caption>Scored against your brief. Soil from USDA SSURGO, ground from county LiDAR, both new in
  this edition.</caption>
  <thead><tr><th>Rank</th><th>Lot</th><th>Garden soil</th><th>Room</th><th>Scenery</th>
  <th>Flood headroom</th><th>Build risk</th><th class="n">Price</th></tr></thead>
  <tbody>
    <tr class="hi"><td><span class="rank g">1</span></td>
      <td><b>1127 Saddle Horn Bend</b><br><span class="xs">1.95 ac · PID 183667</span></td>
      <td><b>Asa loam</b> — well drained, prime</td><td><b>1.95 ac</b></td>
      <td><b>Mill Bayou, ~half the perimeter</b></td><td>24–25 ft — needs 5–6 ft of fill</td>
      <td>Low shrink-swell</td><td class="n">$82,500</td></tr>
    <tr><td><span class="rank">2</span></td>
      <td><b>336 Wagon Wheel Trl W</b><br><span class="xs">1.00 ac · PID 183367</span></td>
      <td><b>Asa loam</b> — well drained, prime</td><td>1.00 ac (0.87 by polygon)</td>
      <td>Short frontage on a 12.6 ac pond</td><td><b>28 ft — only ~2 ft of fill</b></td>
      <td>Low shrink-swell</td><td class="n"><b>$45,000</b></td></tr>
    <tr><td><span class="rank a">3</span></td>
      <td><b>Lot 29 Broken Arrow Trl</b><br><span class="xs">1.30 ac · PID 186219</span></td>
      <td class="bad">Pledger clay — 70% clay</td><td>1.30 ac</td>
      <td>Good frontage, 12.6 ac pond</td><td>26 ft — 4 ft of fill</td>
      <td><b>Vertisol — high movement</b></td><td class="n">$49,000</td></tr>
    <tr><td><span class="rank r">4</span></td>
      <td><b>750 Wagon Wheel Trl</b><br><span class="xs">1.00 ac · PID 183332</span></td>
      <td class="bad">Pledger clay — 73% clay</td><td>1.00 ac</td>
      <td><b>Flag Lake, 101 acres</b></td><td>24 ft — 6 ft of fill</td>
      <td><b>Vertisol + abuts a dam</b></td><td class="n">$58,000</td></tr>
  </tbody>
</table>

<div class="cols2">
  <div class="note amber" style="margin-top:0;">
    <span class="lbl">Why the cheapest land is not the answer for you</span>
    <p>On price alone Lot 29 wins outright — $37,692 an acre and the only lot asking <em>below</em> the
    county's appraisal. This edition would recommend it to an investor.</p>
    <p style="margin-bottom:0;">But it sits on <b>Pledger clay</b>: 70% clay, a permeability of
    0.21 µm/s, hydrologic group D, and a linear extensibility of <b>19</b> — a shrink-swell vertisol.
    That is the ground that cracks slabs, forces an aerobic septic system, ponds after rain and
    gardens only in a two-week moisture window. The $10,000 you save on land you give back on the
    septic and the foundation, and you garden on it for the next thirty years. See §13.</p>
  </div>
  <div class="note blue" style="margin-top:0;">
    <span class="lbl">The case for taking Lot 2 instead</span>
    <p>If the budget is the binding constraint, Lot 2 is the value play <em>within</em> the good soil:
    the same Asa loam, the <b>highest natural ground in the portfolio at 28 ft</b> — so ~2 ft of fill
    instead of 5–6 — and it costs $37,500 less than Lot 1.</p>
    <p style="margin-bottom:0;">What you give up is room and outlook: 1.00 acre of record that the
    county's own polygon computes at <b>0.872</b>, only 187 ft wide, and the shortest water frontage of
    the four. For a keen gardener that is the difference between a vegetable plot and an orchard.</p>
  </div>
</div>

<div class="note teal" style="margin-bottom:0;">
  <span class="lbl">And do not buy all four</span>
  Four vacant lots cost <b>$4,650–$5,520 a year</b> to hold and return nothing — $14,000–$16,500 over
  a three-year window, on a portfolio already asking 15.6% above the county's appraised value. The
  build needs one lot; the other three add carry, not capability.
</div>
""", "1 · Verdict", "verdict")


# =========================================================================== 4. snapshot
add("""
<h2><span class="n">2 ·</span> Portfolio snapshot</h2>
<div class="kpis">
  <div class="kpi"><div class="k">Land, all four lots</div><div class="v">$234,500</div>
    <div class="d">5.25 ac of record <span class="cf n">was &ldquo;~4.95&rdquo;</span></div></div>
  <div class="kpi bad"><div class="k">County appraised value</div><div class="v">$202,900</div>
    <div class="d">asking a <b>+15.6%</b> premium """ + CF['v'] + """</div></div>
  <div class="kpi flag"><div class="k">All-in, one lot built</div><div class="v">$505k–905k</div>
    <div class="d">land + site + 5BR house """ + CF['e'] + """</div></div>
  <div class="kpi flag"><div class="k">Annual carry, four vacant lots</div><div class="v">$4.7–5.5k</div>
    <div class="d">tax + POA + mowing <span class="cf n">rates corrected</span></div></div>
</div>

<div class="note teal">
  <span class="lbl">Site facts that now hold for all four lots — checked parcel by parcel</span>
  FEMA FIRM panel <b>48039C0420K</b>, effective <b>30 December 2020</b> <span class="cf n">corrected
  from 48039C0605K</span> · all four mapped <b>Zone AE</b>, SFHA = true, with <b>no static BFE</b> on
  the polygon (the BFE varies and must be read from the profile) """ + CF['v'] + """ ·
  nearest published BFE line <b>28 ft NAVD88</b> at every lot <span class="cf n">new</span> ·
  finished floor required at <b>≥ BFE + 24 in</b> """ + CF['v'] + """ ·
  school district <b>Columbia-Brazoria ISD</b> for all four """ + CF['v'] + """ ·
  <b>no</b> hospital district, <b>no</b> junior-college district, <b>no</b> MUD, <b>no</b> city limits
  <span class="cf n">new</span> · water and sewer are <b>private well plus on-site septic</b> ·
  no natural gas · TDI windstorm zone <b>Inland I, 120 mph</b> <span class="cf n">new</span>.
</div>

<h3>The shape of the money</h3>
<div class="bars">
""" + bar('Land, one lot', '$45k–82.5k', 12, 'b')
  + bar('Pre-construction / site works', '$26k–108k', 16, 'a')
  + bar('The house itself, 2,400–2,800 sq ft', '$420k–700k', 100, 'g')
  + bar('Insurance, first year once built', '$5k–9.5k', 2, 'r')
  + bar('Annual carry while vacant, ×4', '$4.7k–5.5k', 1, 'r') + """
</div>
<p class="sm">Land is <b>9–16%</b> of the all-in cost of putting a family into a house here. That is
the single most important proportion in this document: the lot choice matters far less to the budget
than the soil class, the pad and the distance to power — and all three of those are lot-specific
unknowns that a $600 soil test and three phone calls would resolve.</p>

<div class="cols2">
  <div class="note amber" style="margin-top:0;">
    <span class="lbl">Costs the original portfolio omitted entirely</span>
    <ul class="t" style="margin-bottom:0;">
      <li>The house — $420,000 to $700,000</li>
      <li>The septic system itself — $8,000 to $25,000</li>
      <li>Windstorm insurance — TWIA average $2,541/yr</li>
      <li>Property tax — the largest carry line</li>
      <li>Electric service extension — up to $25,000</li>
      <li>Engineered pad and fill — now <b>certain</b>, not optional (§10)</li>
      <li>Propane, water treatment, culvert, clearing</li>
    </ul>
  </div>
  <div class="note blue" style="margin-top:0;">
    <span class="lbl">Costs this edition removes</span>
    <ul class="t" style="margin-bottom:0;">
      <li><b>Angleton-Danbury Hospital District tax</b> — the lots are in no hospital district at
          all, so 0.074685 per $100 comes out of the model</li>
      <li><b>Angleton Drainage District tax</b> — the lots sit in county-wide drainage, not the
          Angleton district, so 0.052816 per $100 comes out too</li>
      <li><b>Brazosport / Alvin junior-college tax</b> — neither district reaches these parcels</li>
    </ul>
    <p class="xs" style="margin-bottom:0;">Together those three lines were overstating the annual
    tax by roughly $260–$300 on the portfolio.</p>
  </div>
</div>
""", "2 · Snapshot", "snapshot")

# =========================================================================== 5. parcel record
rows = []
for k in ORDER:
    p = LOTS[k]
    prem = 100 * (p['asking_price_usd'] / p['bcad_appraised_usd'] - 1)
    rows.append([
        '<b>%s</b>' % p['short'],
        '%s<br><span class="xs">%s</span>' % (p['pid'], p['geo_id']),
        p['legal_description'].replace('(A0038 J B BAILEY) ', '').replace('BAR X RANCH', 'Bar X Ranch'),
        '%.2f' % p['acres_of_record'],
        '%.3f' % p['gis_polygon_acres'],
        '%d × %d' % tuple(p['bbox_ft']),
        '$%s' % format(p['bcad_appraised_usd'], ','),
        p['deed_reference'],
    ])
add("""
<h2><span class="n">3 ·</span> The parcel record — established for the first time</h2>
<p>Neither earlier edition contained a single parcel identifier. Every lot is now tied to its
Brazoria County Appraisal District record. This is the table that resolves the acreage disputes,
the section numbers and the value question.</p>
""" + table(
    ['Listing name', 'PID / geo ID', 'Legal description of record', '~Acres of record',
     '~GIS polygon', '~Bounding box (ft)', '~BCAD appraised', 'Deed'],
    rows,
    caption='Brazoria County ArcGIS, general/Parcels/MapServer/1 (BCAD parcel data), '
            'retrieved 11 September 2026. ' + CF['n'],
    cls='compact') + """

<div class="note green">
  <span class="lbl">Thirteen open items closed</span>
  Parcel IDs and geo IDs for all four · legal descriptions · acreage of record for Lots 3 and 4 ·
  the section number for Lots 2 and 4 · the recorded plat and restriction instrument for each
  section · the FIRM panel · the flood zone per parcel · the taxing districts · the school district ·
  the jurisdiction · natural ground elevation · whether Lot 3 is waterfront · whether Lot 4 is
  1.0 or 1.27 acres.
</div>

<h3>Where the acreage claims landed</h3>
<table class="compact">
  <thead><tr><th>Lot</th><th>Earlier editions said</th><th>County record says</th><th>Effect</th></tr></thead>
  <tbody>
    <tr><td>1127 Saddle Horn Bend</td><td>1.95 ac</td><td class="fix">1.95 ac — confirmed</td><td>None. The one acreage that was right.</td></tr>
    <tr><td>336 Wagon Wheel Trl W</td><td>1.00 ac</td><td class="fix">1.00 ac of record, but the county polygon computes to <b>0.872 ac</b></td><td>Buildable area may be ~13% less than the deed implies. Survey it.</td></tr>
    <tr><td>Lot 29 Broken Arrow Trl</td><td class="strike">~1.0 ac "est."</td><td class="fix"><b>1.30 ac</b></td><td>$/acre falls from ~$49,000 to <b>$37,692</b>. Best value in the portfolio.</td></tr>
    <tr><td>750 Wagon Wheel Trl</td><td class="strike">1.0 ac or 1.27 ac — unresolved</td><td class="fix"><b>1.00 ac</b>. The 1.27 figure is wrong.</td><td>Confirms it as the dearest land per acre, by 28% over Lot 29.</td></tr>
  </tbody>
</table>

<div class="note amber">
  <span class="lbl">Two per-lot differences nobody had noticed</span>
  <ul class="t" style="margin-bottom:0;">
    <li><b>The four lots are not governed by one set of deed restrictions.</b> Lots 2 and 4 are in
        Bar-X Ranch Section 1 (plat 16/104, restrictions 1515/679, 1980, plus drainage easements
        1712/500); Lot 1 is Section 2 (plat 16/119, restrictions 1532/471, 1980); Lot 3 is Section 16
        (plat 17/219, restrictions 84-29/885, <b>1984</b>). Three different recorded instruments, so
        the "ACC Rev 2" quoted as a single controlling document across all four lots cannot be
        right. The minimum-square-footage and garage rules must be read per section.</li>
    <li><b>Lot 2 alone sits inside the Baileys Prairie extraterritorial jurisdiction.</b> Baileys
        Prairie subdivision regulation reaches it; the other three answer only to the county.</li>
  </ul>
</div>

<p class="xs">Owner-of-record names are in the BCAD record and are deliberately not reproduced here.
Search by PID at <a href="https://esearch.brazoriacad.org/">esearch.brazoriacad.org</a>.</p>
""", "3 · Parcel record", "parcels")

# =========================================================================== 6. value
vrows = []
for k in ORDER:
    p = LOTS[k]
    ppa = p['asking_price_usd'] / p['acres_of_record']
    prem = 100 * (p['asking_price_usd'] / p['bcad_appraised_usd'] - 1)
    cls = 'hi' if k == 'lot3' else ''
    vrows.append(([
        '<b>%s</b>' % p['short'],
        '$%s' % format(p['asking_price_usd'], ','),
        '%.2f ac' % p['acres_of_record'],
        '<b>$%s</b>' % format(round(ppa), ','),
        '$%s' % format(p['bcad_appraised_usd'], ','),
        ('<b>%+.1f%%</b>' if k == 'lot3' else '%+.1f%%') % prem,
        '$%s' % format(p['asking_price_usd'] - p['bcad_appraised_usd'], ','),
    ], cls) if cls else [
        '<b>%s</b>' % p['short'],
        '$%s' % format(p['asking_price_usd'], ','),
        '%.2f ac' % p['acres_of_record'],
        '<b>$%s</b>' % format(round(ppa), ','),
        '$%s' % format(p['bcad_appraised_usd'], ','),
        '%+.1f%%' % prem,
        '$%s' % format(p['asking_price_usd'] - p['bcad_appraised_usd'], ','),
    ])
vrows.append(([
    'Portfolio', '$234,500', '5.25 ac', '$44,667', '$202,900', '+15.6%', '$31,600'], 'tot'))

add("""
<h2><span class="n">4 ·</span> Value — asking price against the county's own number</h2>
<p>Pricing land per acre only works once the acreage is right, which is why neither earlier edition
could do it. With the acreage of record established, two independent value tests are available: price
per acre, and price against the appraisal the county already publishes for each parcel.</p>
""" + table(
    ['Lot', '~Asking', '~Acres of record', '~$ per acre', '~BCAD appraised', '~Premium', '~Premium $'],
    vrows,
    caption='Asking prices from listing copy ' + CF['u'] +
            '; acreage and appraised value from the BCAD parcel record ' + CF['v']) + """

<div class="cols2">
  <div>
    <h3>Price per acre, re-ranked</h3>
    <div class="bars">
""" + bar('Lot 29 Broken Arrow', '$37,692', 65, 'g')
  + bar('1127 Saddle Horn Bend', '$42,308', 73, '')
  + bar('336 Wagon Wheel Trl W', '$45,000', 78, 'a')
  + bar('750 Wagon Wheel Trl', '$58,000', 100, 'r') + """
    </div>
    <p class="sm">The second edition ranked 1127 Saddle Horn Bend cheapest per acre. Correcting Lot
    29 from an estimated 1.0 acre to its recorded 1.30 acres moves it to the front by 11%.</p>
  </div>
  <div>
    <h3>Premium over county appraisal</h3>
    <div class="bars">
""" + bar('Lot 29 Broken Arrow', '−5.5%', 20, 'g')
  + bar('750 Wagon Wheel Trl', '+16.0%', 59, 'a')
  + bar('336 Wagon Wheel Trl W', '+25.0%', 93, 'r')
  + bar('1127 Saddle Horn Bend', '+26.9%', 100, 'r') + """
    </div>
    <p class="sm">An appraisal is not a market value, and Texas appraisals commonly lag a rising
    market. But a <b>27% premium</b> on one lot and a <b>discount</b> on another, inside the same
    subdivision and the same flood zone, is a negotiating fact.</p>
  </div>
</div>

<div class="note blue">
  <span class="lbl">How to use this at the negotiating table</span>
  The four appraised values total <b>$202,900</b> against a $234,500 ask. The county's appraisal is
  the number the seller pays tax on and the number that will be quoted back at them. On Lots 1, 2 and
  4 there is a documented $31,600 of daylight to argue about. On Lot 29 there is none — the seller is
  already under the county's number, which is a further reason to treat it as the pick rather than to
  push it.
</div>

<div class="note amber">
  <span class="lbl">A caution on the polygon acreages</span>
  The GIS polygon area computed from the county's own parcel geometry runs <b>3–13% below</b> the
  acreage of record on three of the four lots (Lot 1 is the exception, computing slightly above).
  Appraisal-district polygons are maintained for mapping, not for conveyancing, and the county says
  so. Do not treat either figure as survey-grade — but do notice that on Lot 2 the gap is large
  enough to matter to a septic layout on a 1-acre lot.
</div>
""", "4 · Value", "value")

# =========================================================================== 7. combined map
pins = []
for k in ORDER:
    p = LOTS[k]
    pins.append('<tr><td><span class="rank">%d</span></td><td><b>%s</b></td>'
                '<td class="n">%.6f</td><td class="n">%.6f</td><td class="n">%s</td>'
                '<td><a href="%s">Google&nbsp;Maps</a> · <a href="%s">Street&nbsp;View</a></td></tr>'
                % (p['lot'], p['short'], p['centroid'][0], p['centroid'][1], p['pid'],
                   gmap_link(p), gsv_link(p)))
add("""
<h2><span class="n">5 ·</span> All four lots on one interactive map</h2>
<p>The map below is live Google Maps satellite imagery with all four parcels pinned in order. Use the
buttons to switch between the four-lot route view, the whole subdivision, and each lot individually.
Below it, the same four parcels are drawn as their <b>actual county boundary polygons</b> — which is
what shows you where the water frontage really is.</p>

<div class="tabs noprint" role="tablist" id="tabs">
  <button class="tab" role="tab" aria-selected="true"  data-src="%%ALL%%">All four lots</button>
  <button class="tab" role="tab" aria-selected="false" data-src="%%AREA%%">Bar X Ranch — whole subdivision</button>
""" + ''.join('<button class="tab" role="tab" aria-selected="false" data-src="%s">Lot %d — %s</button>'
              % (gmap_lot(LOTS[k]), LOTS[k]['lot'], LOTS[k]['short'].split()[0]) for k in ORDER) + """
</div>
""" + mapbox('Live Google Maps — satellite', gmap_all(),
             "<b>Combined Google Maps satellite view of all four lots.</b> Interactive in the browser "
             "version. The four parcel centroids are tabulated below; each is a live link.",
             cls='map') + """
<h3>The same four parcels as recorded boundaries</h3>
<div id="leaf"></div>
<div class="noprint leg">
  <span><i style="background:#0f766e"></i>Lot 1 · 1127 Saddle Horn Bend</span>
  <span><i style="background:#1c3ba8"></i>Lot 2 · 336 Wagon Wheel Trl W</span>
  <span><i style="background:#15602f"></i>Lot 3 · Lot 29 Broken Arrow Trl</span>
  <span><i style="background:#a91f14"></i>Lot 4 · 750 Wagon Wheel Trl</span>
</div>
<p class="xs noprint">Boundaries from <a href="data/parcels.geojson">data/parcels.geojson</a>
(Brazoria County BCAD parcel service). Imagery Esri, Maxar, Earthstar Geographics. Click a parcel for
its record. Boundaries are for orientation only and are not a survey.</p>

<table class="compact">
  <caption>Parcel centroids, WGS 84</caption>
  <thead><tr><th>Lot</th><th>Listing name</th><th class="n">Latitude</th><th class="n">Longitude</th>
  <th class="n">PID</th><th>Open live</th></tr></thead>
  <tbody>""" + ''.join(pins) + """</tbody>
</table>
""", "5 · Combined map", "map")


# =========================================================================== 8-11. lot pages
LOT_SEC = {'lot1': 6, 'lot2': 7, 'lot3': 8, 'lot4': 9}
for k in ORDER:
    p = LOTS[k]
    ppa = p['asking_price_usd'] / p['acres_of_record']
    prem = 100 * (p['asking_price_usd'] / p['bcad_appraised_usd'] - 1)
    badges = ''.join('<span class="badge %s">%s</span>' % (c, t) for c, t in p['badges'])
    add("""
<div class="lothead">
  <div>
    <div class="id">Lot %d of 4 · PID %s · %s</div>
    <h2>%s</h2>
    <div class="addr">Angleton, TX 77515 · %s · %s</div>
    <div class="badges">%s</div>
  </div>
  <div class="price">
    <div class="p">$%s</div>
    <div class="pa">$%s per acre · %.2f ac of record</div>
    <div class="pa" style="color:%s;font-weight:600;">%+.1f%% vs county appraisal</div>
  </div>
</div>

<div class="cols2c">
  <div>
    %s
  </div>
  <div>
    <dl class="facts">
      <dt>Legal</dt><dd>%s</dd>
      <dt>Situs of record</dt><dd>%s</dd>
      <dt>Deed reference</dt><dd>%s</dd>
      <dt>Plat / restrictions</dt><dd>%s · restrictions %s</dd>
      <dt>Dimensions</dt><dd>Bounding box %d × %d ft; county polygon computes %.3f ac</dd>
      <dt>Flood</dt><dd>Zone %s, SFHA · FIRM panel %s eff. %s</dd>
      <dt>Nearest BFE line</dt><dd><b>%s ft NAVD88</b>, %s ft from the parcel</dd>
      <dt>Ground (LiDAR)</dt><dd>%s</dd>
      <dt>Water body</dt><dd>%s</dd>
      <dt>Highway</dt><dd>%s</dd>
      <dt>School district</dt><dd>Columbia-Brazoria ISD</dd>
      <dt>Jurisdiction</dt><dd>%s</dd>
      <dt>Windstorm</dt><dd>TDI Inland I — 120 mph 3-second gust</dd>
    </dl>
  </div>
</div>

<h3>Listing photography and street imagery</h3>
<div class="shots">
  %s
  %s
  %s
</div>
<div class="linkrow">
  <a class="lnk g" href="%s">Open in Google Maps</a>
  <a class="lnk" href="%s">Google Street View</a>
  <a class="lnk" href="%s">Zillow — search this address</a>
  <a class="lnk" href="https://esearch.brazoriacad.org/">BCAD record — PID %s</a>
  %s
</div>
<p class="xs">Listing photographs on Zillow, Redfin and Realtor.com are licensed to those
platforms and to the listing brokerage, so they are linked rather than reproduced. To place the
waterfront photographs inline, download them from the listing pages above and save them into
<code>assets/photos/</code> as <code>lot%d-1.jpg</code>, <code>lot%d-2.jpg</code> and
<code>lot%d-3.jpg</code> — the frames above will pick them up automatically on reload.</p>

<div class="cols2">
  <div class="note %s" style="margin-top:1mm;">
    <span class="lbl">Best for</span>%s
  </div>
  <div class="note amber" style="margin-top:1mm;">
    <span class="lbl">Watch</span>%s
  </div>
</div>
<div class="note %s" style="margin-bottom:0;">
  <span class="lbl">Verdict on this lot</span>%s
</div>
""" % (
        p['lot'], p['pid'], p['geo_id'],
        p['short'],
        p['subdivision'], lot_label(p['legal_description']),
        badges,
        format(p['asking_price_usd'], ','), format(round(ppa), ','), p['acres_of_record'],
        ('#15602f' if prem < 0 else '#a91f14'), prem,
        mapbox('Live Google Maps satellite — %s' % p['short'], gmap_lot(p),
               map_fallback(p), cls='map'),
        p['legal_description'],
        p['situs_of_record'] if p['situs_of_record'].strip() else '— none assigned —',
        p['deed_reference'],
        p['plat'], p['recorded_restrictions'],
        p['bbox_ft'][0], p['bbox_ft'][1], p['gis_polygon_acres'],
        p['fema_zone_2020'], p['firm_panel'], p['firm_effective'],
        p['nearest_published_bfe_ft_navd88'], format(p['nearest_bfe_line_ft_away'], ','),
        p['ground'],
        p['water'],
        p['sh35'] + ' — ' + p['noise'],
        ('Unincorporated county · <b>inside the Baileys Prairie ETJ</b>'
         if k == 'lot2' else 'Unincorporated county · no city limits, no ETJ'),
        shot(p['lot'], 1, 'Waterfront view', 'Save as assets/photos/lot%d-1.jpg' % p['lot']),
        shot(p['lot'], 2, 'Lot / frontage', 'Save as assets/photos/lot%d-2.jpg' % p['lot']),
        shot(p['lot'], 3, 'Street / access', 'Save as assets/photos/lot%d-3.jpg' % p['lot']),
        gmap_link(p), gsv_link(p), zillow_link(p['short']), p['pid'],
        ('<a class="lnk" href="https://www.realtor.com/realestateandhomes-detail/'
         '750-Wagon-Wheel-Trl_Angleton_TX_77515_M88761-47581">Realtor.com listing</a>'
         if k == 'lot4' else
         '<a class="lnk" href="https://www.loopnet.com/property/'
         '1127-saddle-horn-bnd-angleton-tx-77515/48039-15340084000/">LoopNet listing</a>'
         if k == 'lot1' else ''),
        p['lot'], p['lot'], p['lot'],
        ('green' if k in ('lot3',) else 'teal'), p['best'],
        p['watch'],
        ('green' if k == 'lot3' else 'blue'), p['verdict'],
    ), "%d · Lot %d — %s" % (LOT_SEC[k], p['lot'], p['short']), k)

# =========================================================================== 12. flood
add("""
<h2><span class="n">10 ·</span> Flood — the finding that changes the build</h2>
<p class="lead">All four lots are in a mapped Special Flood Hazard Area. That was never in doubt. What
both earlier editions got wrong is the elevation arithmetic, and it goes the wrong way.</p>

<div class="note red">
  <span class="lbl">The correction</span>
  <p>Both earlier editions assumed a base flood elevation of <b>24 ft</b> and concluded that natural
  ground of 28–30 ft cleared the county's requirement comfortably, so the house could be built at
  grade with no fill. Queried against the county's own copy of the effective FIRM:</p>
  <ul class="t" style="margin-bottom:0;">
    <li>The <b>nearest published BFE line to every one of the four lots reads 28 ft NAVD88</b>, with
        a 29 ft line further upstream. Not 24 ft.</li>
    <li>The Zone AE polygon carries <b>no static BFE</b> — meaning the BFE varies across it and must
        be read from the flood profile, which is precisely why a single assumed figure was never safe.</li>
    <li>County <b>LiDAR elevation contours</b> put natural ground at the parcels at <b>24–28 ft</b>,
        not 28–30 ft.</li>
  </ul>
</div>

<table class="compact">
  <caption>Per-lot elevation arithmetic. Requirement = 28 ft BFE + 24 in county freeboard = 30 ft.
  """ + CF['n'] + """</caption>
  <thead><tr><th>Lot</th><th class="n">Nearest published BFE</th><th class="n">Ground at parcel (LiDAR)</th>
  <th class="n">Required finished floor</th><th class="n">Fill / stem wall needed</th><th>Consequence</th></tr></thead>
  <tbody>
    <tr><td>1127 Saddle Horn Bend</td><td class="n">28 ft</td><td class="n">24–25 ft</td><td class="n">30 ft</td>
      <td class="n"><b>5–6 ft</b></td><td>Largest lift of the four. Engineered pad or piers, not a slab on grade.</td></tr>
    <tr><td>336 Wagon Wheel Trl W</td><td class="n">28 ft</td><td class="n">28 ft</td><td class="n">30 ft</td>
      <td class="n"><b>2 ft</b></td><td>Smallest lift. The best ground in the portfolio.</td></tr>
    <tr><td>Lot 29 Broken Arrow Trl</td><td class="n">28 ft</td><td class="n">26 ft</td><td class="n">30 ft</td>
      <td class="n"><b>4 ft</b></td><td>Middling. Budget a real pad.</td></tr>
    <tr><td>750 Wagon Wheel Trl</td><td class="n">28 ft</td><td class="n">24 ft</td><td class="n">30 ft</td>
      <td class="n"><b>6 ft</b></td><td>Largest lift, and it abuts a levee. See below.</td></tr>
  </tbody>
</table>

<div class="cols2">
  <div class="note amber" style="margin-top:0;">
    <span class="lbl">What this does to the cost model</span>
    <p>The second edition carried engineered pad and fill at <b>$0–$8,000</b>, treating it as
    optional. On these figures it is not optional on any lot, and a 4–6 ft lift under a
    2,400–2,800 sq ft house is a different item altogether. §14 carries it at
    <b>$12,000–$45,000</b>.</p>
    <p style="margin-bottom:0;">It also all but forecloses the LOMA. A Letter of Map Amendment
    requires naturally high ground; placing fill converts the application into a LOMR-F, which
    carries a FEMA review fee and a far heavier evidential burden.</p>
  </div>
  <div class="note red" style="margin-top:0;">
    <span class="lbl">750 Wagon Wheel Trail sits against a dam</span>
    <p>The parcel boundary runs <b>11 ft</b> from the <b>Flag Lake Levee</b> embankment, which
    impounds the 101.5-acre Flag Pond. The structure is in the National Inventory of Dams as
    <b>TX06298</b>. Published NID data carries <b>no hazard-potential classification and no condition
    assessment</b> for it.</p>
    <p style="margin-bottom:0;">Lot 1 has a lighter version of the same question: it lies downstream
    of <b>Bar X Development Dam (NID TX01759)</b> on a Mill Bayou tributary, which NID does rate —
    low hazard potential. Ask TCEQ Dam Safety about both before buying either.</p>
  </div>
</div>

<h3>What still has to be confirmed in writing, per lot</h3>
<ul class="t wide">
  <li><b>The site-specific BFE</b> from Brazoria County Floodplain &amp; 911 Administration. A
      published BFE line 1,000–2,500 ft away is strong evidence, not a determination. Ask which
      cross-section governs each lot — Mill Bayou governs Lot 1, and it is a different watercourse
      from the one governing Lots 2 and 3.</li>
  <li><b>Lowest adjacent grade at the proposed footprint</b>, from a topographic survey. The LiDAR
      contour band is a screening tool; the elevation certificate will be written from a survey.</li>
  <li><b>Pluvial ponding.</b> Flat coastal clay floods from rainfall alone, and a riverine BFE says
      nothing about it. The wettest year in the 1991–2020 record delivered <b>2,024 mm</b> of rain
      against a 1,177 mm average — four times the driest year.</li>
  <li><b>Levee status.</b> Whether the Angleton Levee is FEMA-accredited, and its trajectory, remains
      unconfirmed — as does the condition of Flag Lake Levee.</li>
</ul>

<p class="sm"><b>One correction carried forward:</b> the county's 24-inch freeboard was adopted by
Commissioners Court in <b>May 2005</b>, not raised after Hurricane Harvey in 2017. The original
portfolio's causal story was twelve years out.</p>
""", "10 · Flood", "flood")


# =========================================================================== terrain
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import terrain_svg                                                    # noqa: E402

TERRAIN = json.load(open(os.path.join(ROOT, 'data', 'terrain.json')))

TER_NOTE = {
    'lot1': ("The section runs 562 ft from the Saddle Horn Bend frontage out to the Mill Bayou "
             "edge. The lot is a wedge: narrow at the road, wide at the water. Ground sits at "
             "24–26 ft across the buildable middle, then drops <b>3.7 ft in the last 8 m</b> to the "
             "bayou at 21.2 ft — an <b>8.4° bank</b>. There is a second, sharper dip right at the "
             "road: 1.7 ft in 8 m at 3.9°, which is the roadside drainage ditch, not landform. "
             "Everything between is within a foot and a half of level.",
             "The pad problem is visible here. The highest natural point anywhere on the transect is "
             "26.0 ft, and the finished floor has to reach 30 ft. That is a <b>4 ft lift at the very "
             "best spot</b>, and 5–6 ft anywhere you would actually want to sit the house."),
    'lot2': ("The section runs 412 ft from Wagon Wheel Trail to the pond. This is the driest profile "
             "of the four: the ground rises off the road to <b>29.1 ft</b> — the highest natural "
             "elevation measured on any of the four lots — holds a broad, genuinely level plateau "
             "across the middle of the lot, then falls away at <b>8.8°</b> over the last few metres "
             "to the water at 21.2 ft.",
             "At 29.1 ft the plateau is <b>within a foot of the 30 ft requirement</b>. That is the "
             "single most valuable physical fact in this portfolio: a foot of fill instead of five or "
             "six, on a lot that also happens to be the cheapest."),
    'lot3': ("The section runs 453 ft from Broken Arrow Trail to the pond. The plateau is real and "
             "broad at 26–27 ft, with the high point at 26.9 ft. The lakeside bank is the "
             "<b>steepest of the four at 11.6°</b> — 4.1 ft of drop in 6 m — and there is another "
             "8.2° cut at the road, again the ditch.",
             "Good, level building ground at 26–27 ft, needing about 3–4 ft of fill. The steep bank "
             "at B matters for the TCEQ 75 ft absorption setback and for erosion, and the ground it "
             "is cut into is Pledger clay."),
    'lot4': ("The section runs 568 ft from Wagon Wheel Trail to Flag Pond, and it is the one profile "
             "that behaves backwards: the ground <b>rises</b> toward the water, from 23.1 ft near the "
             "road to <b>30.7 ft</b> at the far boundary, on a sustained <b>8.5°</b> climb.",
             "That rise is not a hill. It is the <b>Flag Lake Levee embankment</b>. The 101-acre pond "
             "is impounded <em>above</em> the level of the buildable part of the lot — the interior "
             "sits at 23–24 ft, the lowest of the four, while the crest beside it reaches 30.7 ft. "
             "You would be building in the shadow of a structure the National Inventory of Dams "
             "carries with no hazard classification and no condition rating."),
}

add("""
<h2><span class="n">11 ·</span> Terrain, slope and how the drawings were made</h2>
<p class="lead">The next four pages give each lot a true-scale plan with the county's 1-foot LiDAR
contours, and a longitudinal section cut along the dotted A–B line from the roadside boundary to the
lakeside boundary.</p>

<div class="cols2">
  <div>
    <h3>How to read them</h3>
    <ul class="t wide">
      <li><b>The plan is rotated</b> so that A–B runs left to right. North is shown by the needle,
          which therefore points somewhere other than up.</li>
      <li><b>Plan and section share the same horizontal scale</b> and the same left-right position,
          so you can drop a finger down from any point on the plan to the same point on the section.</li>
      <li><b>A</b> is the boundary at the street, <b>B</b> the boundary at the water. The profile is
          continued a short way past both so the road ditch and the water are visible.</li>
      <li><b>The section is drawn three times.</b> Once vertically exaggerated so the shape can be
          seen, with the <b>true</b> slope angles printed on the notable breaks; once at a true
          <b>1:1</b>, which is what the ground really looks like; and once as an earth-curvature check.</li>
    </ul>
  </div>
  <div>
    <h3>Where the elevations come from</h3>
    <p class="sm">Contours are Brazoria County's published LiDAR product at a <b>1-foot interval</b>.
    The profile is sampled from the <b>USGS 3DEP 1-metre digital elevation model</b> at roughly 1 m
    spacing along the line, converted from metres to feet. The two are independent datasets and they
    agree to within about a foot across all four lots, which is the main reason to trust either.</p>
    <div class="note amber" style="margin:2mm 0 0;">
      <span class="lbl">Honest limitation</span>
      A DEM is a model of a bare-earth surface, not a survey. Slope angles quoted over a 6–8 m
      baseline are reliable to a fraction of a degree; spot elevations are good to roughly ±0.5 ft.
      An elevation certificate will be written from an instrument survey, not from this.
    </div>
  </div>
</div>

<h3>The four lots compared on terrain</h3>
""" + table(
    ['Lot', '~Section A–B', '~Ground on the buildable plateau', '~Highest', '~Lowest',
     '~Relief', '~Steepest bank', '~Fill to reach 30 ft'],
    [['1127 Saddle Horn Bend', '562 ft', '24–26 ft', '26.0 ft', '21.2 ft', '4.8 ft',
      '8.4° (15%)', '<b>4–6 ft</b>'],
     (['336 Wagon Wheel Trl W', '412 ft', '<b>27–29 ft</b>', '<b>29.1 ft</b>', '21.2 ft', '8.0 ft',
       '8.8° (16%)', '<b>~2 ft</b>'], 'hi'),
     ['Lot 29 Broken Arrow Trl', '453 ft', '26–27 ft', '26.9 ft', '21.2 ft', '5.7 ft',
      '<b>11.6° (20%)</b>', '3–4 ft'],
     ['750 Wagon Wheel Trl', '568 ft', '23–24 ft', '30.7 ft <span class="xs">(levee crest)</span>',
      '23.1 ft', '7.6 ft', '8.5° (15%)', '<b>6–7 ft</b>']],
    caption='Plateau figures are the range across the level central part of each transect — the part '
            'you would actually build on. ' + CF['n'], cls='compact') + """

<div class="note teal">
  <span class="lbl">The headline: this is flat land with a bank at the end</span>
  Across all four lots the buildable ground falls within about <b>1.5 ft over 300–400 ft</b> — a true
  gradient of roughly <b>0.2°</b>, which is why the 1:1 panels look like straight lines. That is
  <em>good</em> news for a garden and for a house pad, and <em>bad</em> news for drainage: water does
  not run off flat clay, it sits on it. Every angle worth reporting is concentrated in the last few
  metres before the water, where the bank drops 3–4 ft at 8–12°, and in the roadside ditch.
</div>

<div class="note blue" style="margin-bottom:0;">
  <span class="lbl">On earth curvature, since you asked</span>
  Each section carries a curvature panel. Over transects of 412–568 ft the sea-level surface departs
  from the flat drawing datum by <b>1.5 to 2.4 mm</b> — that is 0.005 to 0.008 <em>feet</em>, roughly
  one hundredth of the DEM's own vertical uncertainty and about one two-hundredth of a single contour
  interval. It is drawn, exaggerated by a factor of tens of thousands, purely so you can see that it
  has been checked. It is correctly ignored everywhere else in this document.
</div>
""", "11 · Terrain method", "terrain")

TER_SEC = {'lot1': 12, 'lot2': 13, 'lot3': 14, 'lot4': 15}
for k in ORDER:
    p = LOTS[k]
    t = TERRAIN['lots'][k]
    plan, sec, meta = terrain_svg.terrain_figs(t, avail_w_mm=176.0, plan_h_mm=88.0)
    read, mean = TER_NOTE[k]
    add("""
<h2><span class="n">%d ·</span> Terrain — Lot %d, %s</h2>
<p class="sm" style="margin-bottom:2mm;">Plan and section at a true horizontal scale of
<b>1:%d</b>. Contours are the county's 1 ft LiDAR product; the profile is USGS 3DEP 1 m DEM.
Section A–B runs from the %s frontage (A) to the water boundary (B), a distance of
<b>%.0f ft</b> across the parcel.</p>
%s
%s
<div class="cols2" style="margin-top:2mm;">
  <div class="note teal" style="margin:0;"><span class="lbl">What the ground does</span>%s</div>
  <div class="note %s" style="margin:0;"><span class="lbl">What it means for building</span>%s</div>
</div>
""" % (TER_SEC[k], p['lot'], p['short'], meta['ratio'],
        (t['street']['name'] or 'street').title(), t['transect_len_ft'],
        plan, sec, read, ('green' if k == 'lot2' else 'red' if k == 'lot4' else 'amber'), mean),
        "%d · Terrain — Lot %d" % (TER_SEC[k], p['lot']), 'terrain%d' % p['lot'])


# =========================================================================== 16. soil
add("""
<h2><span class="n">16 ·</span> Soil — the one thing that decides all three of your problems</h2>
<p class="lead">Soil settles your garden, your septic system and your foundation at the same time, and
the four lots do not share it. The USDA soil survey splits them cleanly down the middle.</p>
""" + table(
    ['Property', 'Lots 1 &amp; 2 — <b>Asa silty clay loam</b>',
     'Lots 3 &amp; 4 — <b>Pledger clay</b>', 'Why it matters to you'],
    [['Taxonomy', 'Fluventic Hapludoll — an alluvial <b>mollisol</b>',
      'Typic Hapludert — a <b>vertisol</b>', 'Mollisols are the world&rsquo;s good farming soils. '
      'Vertisols are fertile but physically hostile.'],
     ['Clay content, topsoil', '36.5%', '<b>69.5%</b>', 'Workability, drainage, everything.'],
     ['Organic matter, topsoil', '3.1%', '6.5%', 'Both genuinely fertile; Pledger more so.'],
     ['pH (1:1 water)', '6.8 — near neutral', '7.0 — neutral',
      'Both excellent. Neither needs correcting for most vegetables.'],
     ['Drainage class', '<b>Well drained</b>', 'Moderately well drained',
      'Wet feet kill more garden plants here than cold does.'],
     ['Surface runoff', '<b>Negligible</b>', '<b>High</b>',
      'High runoff on flat ground means standing water after rain.'],
     ['Hydrologic group', '<b>B</b>', '<b>D</b>',
      'D is the worst class — least infiltration, most runoff. A pluvial flood risk the FEMA '
      'map does not describe.'],
     (['Saturated conductivity', '<b>9.0 µm/s</b>', '<b>0.21 µm/s</b>',
       'Pledger is <b>43× less permeable</b>. This is what drives the septic system type.'], 'hi'),
     (['Linear extensibility (shrink-swell)', '<b>4.5</b> — low to moderate',
       '<b>19</b> — very high', 'Above about 9 is &ldquo;high&rdquo;. This is the number that cracks '
       'slabs, drives, and pipework.'], 'hi'),
     ['Available water capacity', '0.18–0.20', '0.14',
      'Asa holds more plant-available water despite being lighter.'],
     ['Farmland classification', 'All areas prime farmland', 'All areas prime farmland',
      'Both are officially prime. &ldquo;Prime&rdquo; is about fertility, not about being easy.'],
     ['Flooding frequency', 'Rarely flooded', 'Rarely flooded', 'Same on both.']],
    caption='USDA NRCS SSURGO, Brazoria County soil survey, major component of the map unit at each '
            'parcel centroid. ' + CF['n'], cls='compact') + """

<div class="cols2">
  <div class="note green" style="margin-top:0;">
    <span class="lbl">Asa silty clay loam — Lots 1 and 2</span>
    <p><b>For gardening: this is the good stuff.</b> A silty clay loam at pH 6.8 with 3% organic
    matter, well drained, negligible runoff. It works over a wide moisture range, takes a spade in
    most weather, holds water without waterlogging, and needs no pH correction. You could plant
    directly into it.</p>
    <p style="margin-bottom:0;"><b>For septic:</b> at 9 µm/s it is likely TCEQ <b>Class III</b>, which
    means roughly 2,250 sq ft of absorptive area and a realistic chance of avoiding a full aerobic
    spray system. <b>For foundations:</b> a linear extensibility of 4.5 is ordinary engineering.</p>
  </div>
  <div class="note red" style="margin-top:0;">
    <span class="lbl">Pledger clay — Lots 3 and 4</span>
    <p><b>For gardening: hard work, permanently.</b> Nearly 70% clay with slickensides in the subsoil.
    It is sticky and unworkable when wet, sets like fired brick when dry, and opens cracks you can put
    a hand into in August. Very fertile — but most people here end up gardening in <b>raised beds with
    imported soil</b>, which is a real annual cost and effort.</p>
    <p style="margin-bottom:0;"><b>For septic:</b> 0.21 µm/s is effectively impermeable — TCEQ
    <b>Class IV</b>, a conventional drainfield is not allowed, and an <b>aerobic unit with a spray or
    drip field is mandatory</b>: $15,000–$25,000 plus a maintenance contract for life.
    <b>For foundations:</b> extensibility 19 demands a post-tensioned or pier-and-beam design plus
    lifelong moisture management around the perimeter.</p>
  </div>
</div>

<div class="note amber">
  <span class="lbl">What this is worth, in money</span>
  On the septic alone the soil difference is plausibly <b>$7,000–$15,000</b> in favour of Lots 1 and 2,
  plus $300–$600 a year forever for the aerobic maintenance contract that Lots 3 and 4 will require.
  On the foundation, a post-tensioned slab engineered for a high-PI vertisol typically runs
  <b>$8,000–$20,000</b> above a conventional engineered slab on a 2,400–2,800 sq ft house. Lot 29's
  $10,000 land saving does not survive either comparison, let alone both.
</div>

<div class="note blue" style="margin-bottom:0;">
  <span class="lbl">The limit of this finding — and it is a real limit</span>
  SSURGO is mapped at about 1:24,000. It tells you the soil that <em>predominates</em> in a map unit,
  and the major component here is given an 85% share. It is strong evidence and it is free; it is
  <b>not</b> a site-specific soil evaluation, and the TCEQ soil class that actually governs your permit
  can only be set by a licensed site evaluator digging on your lot. Order that evaluation on the
  shortlisted lot before you close. It costs $350–$600 and it is the highest-value money in this
  entire project.
</div>
""", "16 · Soil", "soil")

# =========================================================================== 17. restrictions
add("""
<h2><span class="n">17 ·</span> Deed restrictions and buildability</h2>
<p>The recorded Bar X Ranch declaration of restrictions has now been read rather than paraphrased.
Several figures repeated by the earlier editions are not in it, and several provisions that matter a
great deal to your plans are.</p>
""" + table(
    ['Provision', 'What the recorded instrument actually says', 'Effect on your plan'],
    [(['<b>§3.15 Pets and livestock</b>',
       'No livestock of any kind other than house pets of reasonable kind and number. Horses are the '
       'single express exception: 1 per 32,670 sq ft, 2 per 42,000 sq ft, one more per additional '
       '21,880 sq ft.',
       '<b>Chickens and ducks are not house pets and are not horses.</b> Your hobby-farming plan is '
       'very likely barred.'], 'hi'),
     (['<b>§3.01 Structures permitted</b>',
       'One single-family dwelling, one attached or detached garage, and <b>one horse barn</b> no '
       'larger than 30 ft × 25 ft. Anything else needs written committee approval before construction.',
       'No coop, no run, no shed, no greenhouse without a written variance. A <b>greenhouse</b> is as '
       'much of an issue as a coop.'], 'hi'),
     ['<b>§3.03 Dwelling size</b>',
      'Minimum <b>1,100 sq ft</b> of living area, excluding open porches and garages; 1,400 sq ft if '
      'more than two storeys.',
      'The <b>&ldquo;1,800 sq ft minimum&rdquo;</b> quoted by earlier editions is <b>not</b> in this '
      'instrument. Your 2,400–2,800 sq ft house clears it easily either way.'],
     ['<b>§3.06 Minimum lot area</b>', 'No building on a lot under 21,880 sq ft; no resubdivision '
      'without written committee approval.', 'All four lots clear this. Lot 2 at 0.872 ac by the '
      'county polygon is still 38,000 sq ft.'],
     ['<b>§3.05 Orientation</b>', 'The front of the lot is the property line with the <b>shortest</b> '
      'dimension abutting a street; the dwelling must face it; a detached garage may sit no nearer the '
      'front line than the house.',
      'Fixes your house orientation. On the long, narrow lots this constrains where the septic field '
      'and garden can go.'],
     ['<b>§3.12 Fences</b>', 'Any lot with a horse barn must be fenced. All fences and their locations '
      'need written approval. No home-made fences.',
      'A garden fence — against deer, rabbits and your own dogs — is a committee submission.'],
     ['<b>§3.04 Roofing</b>', 'Wood shingle, built-up tar and gravel, or asphalt shingle of not less '
      'than 340 lb per square.', 'Rules out standing-seam metal without a variance; metal is otherwise '
      'the sensible coastal choice.'],
     ['<b>§3.07 Nuisance</b>', 'No noxious or offensive activity, nor anything that may become an '
      'annoyance to the neighbourhood. Exterior display or discharge of firearms expressly forbidden.',
      'A cockerel is the textbook &ldquo;annoyance&rdquo; complaint even where hens are tolerated.'],
     ['<b>§3.13 Lot maintenance</b>', 'Owners must keep grass and weeds cut and fences painted; the '
      'association may enter, do the work, and bill the owner.',
      'This is the origin of the <b>$125 vacant-lot mowing charge</b> in the carrying-cost model.'],
     ['<b>§3.14 / §3.16 Septic and drainage</b>',
      'No septic tank may drain into road ditches. Drainage of streets, lots or roadway ditches may '
      'not be impaired.',
      '<b>Directly relevant to the 2–6 ft pad</b> that §10 shows you need: you may not solve your '
      'flood problem by pushing water onto the road or a neighbour.'],
     ['<b>§4.05 Committee</b>',
      "The architectural control committee's powers ceased 15 years after the instrument and passed "
      "to the property owners' association.",
      'Submissions go to the POA today, not to a developer committee.']],
    caption='Bar X Ranch declaration of restrictions as recorded (Deed Vol. 1679, Pg. 695). '
            + CF['n'], cls='compact') + """

<div class="note red">
  <span class="lbl">The caveat that you must close before relying on any of this</span>
  The instrument read above is <b>one</b> Bar X Ranch declaration. Your four lots are governed by
  <b>three different recorded instruments</b> — Section 1 by 1515/679 (1980), Section 2 by 1532/471
  (1980), Section 16 by 84-29/885 (1984) — and none of them is the document quoted here. Subdivision
  declarations of this era were near-identical in form across sections, so the provisions above are
  very likely to be substantially what governs your lot. <b>Very likely is not good enough for the
  decision you are making.</b> Pull the recorded instrument for the specific lot from the Brazoria
  County Clerk, and ask the POA in writing, before you close, one question: <i>may I keep a small
  number of chickens and ducks, and may I build a coop and a greenhouse?</i> Get the answer on
  letterhead.
</div>

<div class="note green" style="margin-bottom:0;">
  <span class="lbl">If poultry is the point, here is the alternative</span>
  Unincorporated Brazoria County has <b>no zoning</b>, so outside a deed-restricted subdivision there
  is generally nothing stopping you keeping poultry on your own land. The trade is everything Bar X
  Ranch gives you — the two lakes, two pools, clubhouses, tennis and basketball courts, playgrounds,
  concrete streets, the 97% owner-occupied neighbourhood and the maintained frontages. Unrestricted
  acreage a few miles further out will let you keep ducks and will not give you any of that. That is
  the real choice in front of you, and it is not a choice this document can make for you.
</div>
""", "17 · Restrictions", "restrictions")


# =========================================================================== 18. septic
add("""
<h2><span class="n">18 ·</span> Septic (OSSF) — sized against the regulation, per soil</h2>
<p>Every house here is on a private well and an on-site sewage facility. This is where the original
portfolio was most wrong, and where §16's soil finding now produces two different answers.</p>
""" + table(['Basis', '~Flow Q (gpd)', 'Septic tank required'],
            [['5 bedrooms, dwelling under 4,500 sq ft, no water-saving devices', '450',
              'Both flows fall in the 351–500 gpd band &rarr; <b>1,250 gal</b> minimum ' + CF['v']],
             ['Same, with water-saving devices', '360', '']],
            caption='30 TAC §285.91 Table III and §285.91(2)') + table(
    ['TCEQ soil class', '~Loading rate R<sub>a</sub>', '~Absorptive area at Q = 450',
     'Which lots', 'System that results'],
    [(['<b>Class III</b> — clay loam', '0.20 gal/sf/day', '<b>~2,250 sq ft</b>',
       '<b>Lots 1 &amp; 2</b> — Asa, 9 µm/s',
       'Conventional drainfield may be permissible; low-pressure dosed or aerobic if not. '
       '<b>$8,000–$15,000</b>'], 'hi'),
     (['<b>Class IV</b> — clay', '0.10 gal/sf/day', '<b>~4,500 sq ft</b>',
       '<b>Lots 3 &amp; 4</b> — Pledger, 0.21 µm/s',
       'Conventional drainfield <b>not permitted</b>. Aerobic treatment unit (600 gal min) plus '
       'spray or drip field, and a mandatory maintenance contract. <b>$15,000–$25,000</b>'], 'hi'),
     ['Class Ib–II — sandy/loamy', '0.25–0.38', '~1,184–1,800 sq ft', 'Neither, on the survey',
      'Conventional. Cheapest outcome, not available here.']],
    caption='Absorptive area = Q ÷ R<sub>a</sub>. The original portfolio used 0.6 gal/sf/day, which '
            'exceeds every class in the TCEQ table. ' + CF['v'], cls='compact') + """

<div class="note red">
  <span class="lbl">The number the original document simply did not contain</span>
  Whichever class applies, TCEQ requires a <b>100% reserve area</b> in addition to the field. On Lots 3
  and 4 that means committing roughly <b>9,000 sq ft — a fifth of a one-acre lot</b> — to sewage
  disposal, before the house, the driveway, the garage, the well and your garden. On Lots 1 and 2 the
  same commitment is about 4,500 sq ft. The original budgeted the permit and the soil test and left the
  system itself out altogether.
</div>
""" + table(['From', 'To', '~Minimum separation'],
            [['Private well or cistern', 'Soil absorption or spray field', '100 ft'],
             ['Private well or cistern', 'Septic tank', '50 ft'],
             ['Lake or pond, at normal pool', 'Soil absorption / unlined evapotranspiration bed', '75 ft'],
             ['Lake or pond, at normal pool', 'Surface (spray) application', '50 ft'],
             ['Property line', 'Spray field', '10 ft (and no spray across a line)']],
            caption='30 TAC §285.91 Table X — these are what make a narrow waterfront lot hard '
                    + CF['v'], cls='compact') + """
<div class="note amber" style="margin-bottom:0;">
  <span class="lbl">Test this on paper before you bid</span>
  Take the lot plan in §12–15, and lay onto it: a 2,400–2,800 sq ft house at 30 ft finished floor, a
  garage, the field, the equal reserve, a well 100 ft from both, the 75 ft water setback, and your
  garden. On <b>Lot 2 at 187 ft wide</b> and on <b>Lot 4 at 123 ft wide</b> this is the test that
  decides whether the lot works at all. Lot 1 at 1.95 acres is the only one where it is not close.
</div>
""", "18 · Septic", "septic")

# =========================================================================== 19. cost
add("""
<h2><span class="n">19 ·</span> Cost to build — rebuilt with the pad and the soil in it</h2>
<p>The second edition carried fill at $0–$8,000 and treated it as optional. §10 and §11 show it is
mandatory on every lot, at 2–6 ft. That single line, plus the vertisol foundation upcharge on Lots 3
and 4, is most of the change here.</p>
""" + table(
    ['Item', '~Low', '~High', 'Note'],
    [['County development / building permit ($75 + $0.04/sf, flood zone)', '$165', '$200',
      'One combined permit ' + CF['v']],
     ['Fill &amp; grading permit', '$0', '$80', ''],
     ['Contractor IRC registration', '$0', '$0', 'Required before the permit issues'],
     ['OSSF site and soil evaluation', '$350', '$600', '<b>Buy this first</b>'],
     ['OSSF permit to construct', '$300', '$500', ''],
     (['<b>OSSF system installed</b>', '$8,000', '$25,000',
       '<b>Class III on Lots 1–2, Class IV aerobic on Lots 3–4</b>'], 'hi'),
     ['Water well, pump and pressure tank', '$10,000', '$20,000', ''],
     ['Water treatment for coastal groundwater', '$0', '$8,000', 'Test before you assume $0'],
     ['Boundary and topographic survey', '$1,500', '$3,500', ''],
     ['Elevation certificate', '$500', '$900', ''],
     ['LOMR-F preparation', '$500', '$1,200', 'Fill forecloses the fee-free LOMA route'],
     ['Driveway culvert and county road access', '$1,500', '$5,000', ''],
     ['Electric service extension', '$0', '$25,000', '<b>Get this quoted per lot</b>'],
     ['Propane tank and set', '$1,000', '$3,000', 'No natural gas here'],
     ['Clearing and grubbing', '$1,500', '$6,000', ''],
     (['<b>Engineered pad / imported fill, 2–6 ft</b>', '$12,000', '$45,000',
       '<b>Was $0–$8,000. Lot 2 at the low end, Lots 1 and 4 at the high end.</b>'], 'hi'),
     (['<b>Vertisol foundation upcharge</b>', '$0', '$20,000',
       '<b>Lots 3 and 4 only</b> — post-tensioned or piered for LEP 19'], 'hi'),
     ["POA architectural review, transfer and resale certificate", '$500', '$750', ''],
     (['Pre-construction subtotal', '<b>~$38,000</b>', '<b>~$165,000</b>',
       '<span class="strike">v1: $11–17k</span> &rarr; <span class="fix">v2: $26–108k</span>'], 'tot')],
    caption='One lot, a 2,400–2,800 sq ft five-bedroom house. ' + CF['e'], cls='compact') + """
<p class="sm">Central planning case <b>$60,000–$95,000</b>. The three variables that decide where you
land are, in order: <b>soil class</b>, <b>depth of fill</b>, and <b>distance to power</b>. All three
are lot-specific, and all three can be resolved for under $1,000 and three phone calls.</p>
""" + table(['Component', '~Low', '~High'],
            [['Land, one lot', '$45,000', '$82,500'],
             ['Pre-construction, above', '$38,000', '$165,000'],
             ['House, 2,400–2,800 sq ft at $175–$250/sq ft ' + CF['e'], '$420,000', '$700,000'],
             (['<b>All-in, one lot built</b>', '<b>~$505,000</b>', '<b>~$950,000</b>'], 'tot')],
            caption='All-in cost of putting a family into a house on one of these lots') + """
<div class="note blue" style="margin-bottom:0;">
  <span class="lbl">Put the lot price in proportion</span>
  The whole spread between the cheapest and dearest lot is <b>$37,500</b>. The spread on the septic
  system alone is <b>$17,000</b>, on the pad <b>$33,000</b>, on the foundation <b>$20,000</b> and on
  the electric extension <b>$25,000</b>. Choosing the lot on its asking price, rather than on its soil
  and its elevation, is optimising the smallest of the five numbers.
</div>
""", "19 · Cost", "cost")

# =========================================================================== 20. carry
add("""
<h2><span class="n">20 ·</span> Annual carrying cost — with the tax model corrected</h2>
<p>The second edition's tax model included an Angleton-Danbury hospital district levy and an Angleton
drainage district levy. Checked parcel by parcel against the county's taxing-district layers,
<b>these lots are in neither</b> — nor in any junior-college district or MUD.</p>
""" + table(
    ['Taxing entity', '~Rate per $100 (TY2025)', 'Applies to these lots?'],
    [['Brazoria County', '0.304758', '<b>Yes</b> ' + CF['v']],
     ['Columbia-Brazoria ISD', '0.953000', '<b>Yes</b> — all four lots ' + CF['v']],
     ['Emergency Services District 1 and 2', 'up to 0.100000 each', 'Yes — rate not confirmed; '
      'statutory cap used ' + CF['e']],
     ['Angleton-Danbury Hospital District', '<span class="strike">0.074685</span>',
      '<b>No</b> — no hospital district reaches these parcels <span class="cf n">corrected</span>'],
     ['Angleton Drainage District', '<span class="strike">0.052816</span>',
      '<b>No</b> — county-wide drainage only <span class="cf n">corrected</span>'],
     ['Brazosport / Alvin Junior College District', '—',
      '<b>No</b> — neither district reaches these parcels <span class="cf n">new</span>'],
     (['<b>Effective combined rate</b>', '<b>1.2578% – 1.4578%</b>', ''], 'tot')],
    cls='compact', caption='Brazoria County Truth-in-Taxation five-year summary, cross-checked '
                           'against the county taxing-district GIS layers') + table(
    ['Item', 'Basis', '~All four lots', '~One lot (1127 Saddle Horn Bend)'],
    [['Property tax, on the current appraised value',
      '1.26–1.46% of $202,900 / $65,030', '$2,552–$2,958', '$818–$948'],
     ['Property tax, once reappraised to what you pay',
      '1.26–1.46% of $234,500 / $82,500', '$2,950–$3,418', '$1,038–$1,203'],
     ['POA dues', '$400 per lot per year ' + CF['u'], '$1,600', '$400'],
     ['Vacant-lot mowing charge', '$125 per lot per year ' + CF['u'], '$500', '$125'],
     (['<b>Total annual carry while vacant</b>', '', '<b>$4,650–$5,520</b>',
       '<b>$1,350–$1,730</b>'], 'tot')],
    caption='Texas reappraises on sale, so plan on the higher tax line from year two') + """
<div class="cols2">
  <div class="note amber" style="margin-top:0;">
    <span class="lbl">The drag on four lots</span>
    <p style="margin-bottom:0;">$4,650–$5,520 a year is <b>2.0–2.4% of the $234,500 land basis</b>,
    every year, on land that produces nothing. Over three years, $14,000–$16,500. Add the 15.6%
    premium over appraised value and the four-lot investment case needs Bar X Ranch land to
    appreciate roughly <b>4–5% a year just to break even</b>.</p>
  </div>
  <div class="note green" style="margin-top:0;">
    <span class="lbl">The drag on one lot</span>
    <p style="margin-bottom:0;">$1,350–$1,730 a year, and it stops being dead money the day you
    build. Once the house is standing you also become eligible for the Texas <b>homestead
    exemption</b>, which the vacant-land case cannot claim — a material saving the earlier editions
    never mentioned.</p>
  </div>
</div>
<p class="xs" style="margin-bottom:0;">POA dues and the mowing charge come from listing copy for other
Bar X Ranch lots, not from the association. Confirm both, and the transfer fee, on a POA resale
certificate. §17 shows the mowing charge is grounded in §3.13 of the recorded restrictions.</p>
""", "20 · Carrying cost", "carry")

# =========================================================================== 21. wind
add("""
<h2><span class="n">21 ·</span> Wind, storm and insurance</h2>
<p class="lead">You asked about safety from storms. On the coast this is two separate questions —
what the building code makes you build, and what the insurance costs — and the answers are better
than you might fear for an address 28 miles from the Gulf.</p>

<div class="note teal">
  <span class="lbl">Wind zone — established for the first time in this edition</span>
  The Texas Department of Insurance divides Brazoria County into three windstorm zones, and
  <b>the dividing line between Inland I and Inland II runs along State Highway 35</b> — the highway
  this subdivision fronts. All four lots lie on the <b>seaward side</b> of SH 35 (between 0.09 and
  1.03 miles south of it), which places all four in <b>Inland I: a 120 mph three-second-gust design
  wind speed</b> under the 2006 IBC/IRC with Texas revisions. For comparison, Surfside Beach and
  Quintana on the shore are Seaward at 130 mph, and Bailey's Prairie and West Columbia inland are
  Inland II at 110 mph.
</div>
""" + table(
    ['Requirement', 'What it means here'],
    [['Design wind speed', '<b>120 mph</b> 3-second gust, TDI Inland I ' + CF['n']],
     ['Certificate of compliance', 'A <b>WPI-8</b> is required, and the application must be made '
      '<b>before construction begins</b>. Brazoria is a designated catastrophe area. ' + CF['v']],
     ['Who signs it', 'A TDI-appointed engineer for new construction in a first-tier county'],
     ['Why you want it anyway', 'Without a WPI-8 the property is not insurable through TWIA, which '
      'is the residual market most coastal Texas homes depend on'],
     ['Storm surge', 'Not the governing threat at this distance inland — the nearest Gulf shoreline '
      'is 28 mi by road. <b>Wind and rainfall are.</b>'],
     ['Rainfall', 'The wettest year in the 1991–2020 record delivered <b>2,024 mm</b> against a '
      '1,177 mm average. This, not surge, is what floods Bar X Ranch.']],
    cls='compact') + table(
    ['Coverage', 'Note', '~Estimated annual'],
    [['Flood — NFIP or private', 'Risk Rating 2.0 prices on first-floor height and <b>distance to '
      'water</b>, so waterfront costs more and the 30 ft pad helps. NFIP building cover caps at '
      '$250,000; excess flood needed above that.', '$1,500–$4,000'],
     ['Windstorm — TWIA', 'State average residential premium <b>$2,541</b> as at 30 June 2026; the '
      '2027 filing directs no rate increase, with a ~3% automatic dwelling-coverage uplift on '
      'renewals from 1 Sept 2026. ' + CF['v'], '$2,500–$4,000'],
     ['Homeowners, excluding wind and flood', 'Fire, liability, contents', '$1,000–$1,500'],
     (['<b>Total once built</b> ' + CF['e'], '', '<b>$5,000–$9,500</b>'], 'tot')]) + """
<div class="note amber" style="margin-bottom:0;">
  <span class="lbl">Two things to understand about the flood line</span>
  A LOMA, if you ever obtained one, would lift the <em>federal mandatory-purchase</em> requirement —
  it would not remove the exposure, and your lender may still insist on cover. But §10 shows you will
  be placing fill, and <b>fill forecloses the LOMA route</b> and pushes you into a LOMR-F, which
  carries a FEMA fee and a heavier burden of proof. Plan on carrying flood insurance permanently.
  Windstorm cover is unaffected by any of this.
</div>
""", "21 · Wind &amp; insurance", "wind")


# =========================================================================== 22. climate
crows = []
for mo, hc, lc, rain, hf, lf in CLIMATE:
    peak = 'hi' if mo in ('Jul', 'Aug') else ''
    row = [('<b>%s</b>' % mo), '<b>%.1f</b>' % hc, '<b>%.1f</b>' % lc,
           '%.1f' % ((hc + lc) / 2), '%d' % rain, '%d / %d' % (hf, lf)]
    crows.append((row, peak) if peak else row)
crows.append((['<b>Year</b>', '<b>25.4</b>', '<b>17.9</b>', '<b>21.7</b>',
               '<b>1,177</b>', '<b>78 / 64</b>'], 'tot'))
add("""
<h2><span class="n">22 ·</span> Living here — the weather, in degrees Celsius</h2>
<p class="lead">A humid subtropical Gulf coast climate: long, hot, wet summers, short mild winters,
almost no frost, and a 320-day growing season that is the single best thing about gardening here.</p>
""" + table(
    ['Month', '~Mean daily max °C', '~Mean daily min °C', '~Mean °C', '~Rainfall mm', '~°F max / min'],
    crows,
    caption='ERA5 reanalysis at the parcels, daily 1991–2020, aggregated to monthly means. '
            'Fahrenheit shown only for cross-reference with local sources. ' + CF['n'],
    cls='compact') + """
<div class="cols2">
  <div>
    <h3>What the numbers feel like</h3>
    <ul class="t wide">
      <li><b>Summer is the constraint.</b> July and August average <b>32.5 °C by day and 25 °C at
          night</b> — it is the humidity and the warm nights, not the peak, that wear people down.
          About <b>51 days a year reach 32 °C</b>, 8 reach 35 °C, and 38 °C is rare (0.5 days a year).
          The 30-year maximum was <b>41 °C</b>.</li>
      <li><b>Winter barely exists.</b> January averages 17.3 °C by day and 9.3 °C at night. Air frost
          occurred in only <b>18 of 30 years</b>, averaging <b>1.9 frost days</b>. The 30-year minimum
          was <b>−6 °C</b>.</li>
      <li><b>Rain is even, and then it isn't.</b> 1,177 mm a year spread remarkably evenly, 79–121 mm
          every month, with a September peak. But the wettest single year delivered <b>2,024 mm</b> and
          the driest <b>488 mm</b> — a fourfold swing. Design the garden and the drainage for both.</li>
    </ul>
  </div>
  <div>
    <h3>The gardening calendar</h3>
    <table class="compact">
      <tbody>
        <tr><td>Mean last spring frost</td><td class="n"><b>2 February</b></td></tr>
        <tr><td>Mean first autumn frost</td><td class="n"><b>19 December</b></td></tr>
        <tr><td>Frost-free growing season</td><td class="n"><b>~320 days</b></td></tr>
        <tr><td>Earliest / latest last spring frost</td><td class="n">5 Jan / 5 Mar</td></tr>
        <tr><td>USDA hardiness zone</td><td class="n">9a–9b</td></tr>
        <tr><td>Annual mean temperature</td><td class="n">21.7 °C</td></tr>
      </tbody>
    </table>
    <div class="note green" style="margin:2mm 0 0;">
      <span class="lbl">For a gardener this is close to a gift</span>
      <b>Two full growing seasons a year</b>, and a winter mild enough for brassicas, alliums, greens,
      carrots and peas from September through March. Citrus, figs, pomegranates, loquats and olives
      are all viable. What defeats people is <b>July and August</b>, when most vegetables stop setting
      — the local practice is to grow hard from February to June, rest or cover-crop through high
      summer, then plant a second crop in September.
    </div>
  </div>
</div>
<div class="note amber" style="margin-bottom:0;">
  <span class="lbl">Three climate realities the brochures leave out</span>
  <b>Humidity</b> drives fungal disease — choose disease-resistant varieties and space for airflow.
  <b>Mosquitoes</b> are a genuine quality-of-life factor beside a bayou or a pond in a subtropical
  climate; Brazoria County runs a mosquito-control programme, and you will use it.
  <b>Hurricane season</b> runs June to November, and the practical consequence for a gardener is that
  anything tall or trellised needs to come down or be strapped when a storm is named.
""" + '</div>', "22 · Climate", "climate")

# =========================================================================== 23. hazards
hrows = []
COL = {'Relatively High': 'r', 'Relatively Moderate': 'a', 'Relatively Low': 'g', 'Very Low': 'g'}
for code, label, rating, freq, eal in NRI:
    dot = COL.get(rating, '')
    badge = ('<span class="badge %s">%s</span>'
             % ({'r': 'red', 'a': 'ae', 'g': 'q'}.get(dot, 'q'), rating))
    hrows.append(([label, badge, freq, eal], 'hi' if code in ('IFLD', 'HRCN', 'WFIR') else ''))
hrows = [(r[0], r[1]) if r[1] else r[0] for r in hrows]
add("""
<h2><span class="n">23 ·</span> Living here — natural hazards, ranked by the federal index</h2>
<p>You asked specifically about flood, storm and fire. FEMA's National Risk Index scores every US
county on eighteen hazards. This is Brazoria County, December 2025 edition.</p>
""" + table(['Hazard', 'County risk rating', '~Annualised frequency', '~County expected annual loss'],
            hrows, cls='compact',
            caption='FEMA National Risk Index, Brazoria County (FIPS 48039). County composite: '
                    '<b>Relatively Moderate</b>. Social vulnerability: Relatively Low. Community '
                    'resilience: <b>Very High</b>. ' + CF['n']) + """
<div class="cols2">
  <div class="note green" style="margin-top:0;">
    <span class="lbl">Wildfire — your best answer</span>
    <p style="margin-bottom:0;"><b>Relatively Low</b>, at an annualised frequency of <b>0.004</b>.
    This is coastal prairie and cropland on heavy, moist clay, criss-crossed by bayous, with no
    forest canopy and no slope. Wildfire is close to a non-issue here, and it is one of the few
    hazards where this location is genuinely better than most of Texas. Grass fires in a drought
    year are the realistic version of the risk, not a crown fire.</p>
  </div>
  <div class="note red" style="margin-top:0;">
    <span class="lbl">Flood — your worst answer</span>
    <p style="margin-bottom:0;"><b>Relatively High</b> for riverine flooding, at 1.86 events a year
    and $78 m of expected annual loss county-wide — the largest single hazard loss in the county. All
    four lots are in mapped <b>Zone AE</b>. Coastal flooding, by contrast, is only Relatively
    Moderate at this distance inland. <b>Rain, not surge, is the threat.</b></p>
  </div>
</div>
<h3>How the hazards actually rank for you, on this site</h3>
<ul class="t wide">
  <li><b>1. Rainfall flooding — high and permanent.</b> Zone AE, a 28 ft BFE, a 30 ft floor
      requirement, and on Lots 3 and 4 a hydrologic group D soil that sheds almost all the rain that
      lands on it. This is the hazard that shapes the build, the insurance and the resale.</li>
  <li><b>2. Hurricane — high, and manageable by design.</b> 0.22 events a year. Twenty-eight miles
      inland puts you outside the surge zone; a 120 mph Inland I structure with an engineer-certified
      WPI-8 is a genuinely robust house. Expect to lose power, not the roof.</li>
  <li><b>3. Tornado — high frequency, low individual probability.</b> 1.11 events a year across a
      1,494 sq mi county. Worth a safe interior room; not worth losing sleep over.</li>
  <li><b>4. Lightning — high, at 70 events a year.</b> The one hazard most people under-rate. Surge
      protection on the well pump, the aerobic septic controller and the HVAC is cheap insurance.</li>
  <li><b>5. Heat — moderate and rising.</b> 14.9 heat-wave events a year. Relevant to the garden, to
      poultry if you ever get permission, and to your cooling bill.</li>
  <li><b>6. Hail, ice storm, cold wave — low to moderate.</b> The February 2021 freeze is the local
      memory; plan for a few days without power and lag the wellhead.</li>
  <li><b>7. Earthquake, landslide, winter weather — very low.</b> Ignore.</li>
</ul>
<div class="note blue" style="margin-bottom:0;">
  <span class="lbl">And one site-specific hazard the index cannot see</span>
  <b>Lot 4 abuts the Flag Lake Levee</b> (National Inventory of Dams TX06298), and §15 shows the
  101-acre pond is impounded <em>above</em> the buildable part of that lot. NID publishes no hazard
  classification and no condition rating for the structure. Lot 1 lies downstream of Bar X Development
  Dam (TX01759), which NID does rate, as low hazard potential. A county-level index will never tell you
  this; ask TCEQ Dam Safety.
</div>
""", "23 · Hazards", "hazards")

# =========================================================================== 24. services
def dist_table(groups):
    out = ''
    for g in groups:
        rows = []
        for name, mi, mins, note in DIST[g]:
            rows.append([name, '%.1f' % mi, '%d' % mins, note or ''])
        out += table([g, '~Miles', '~Drive min', 'Note'], rows, cls='compact')
    return out


add("""
<h2><span class="n">24 ·</span> Living here — services, shopping, school and hospital</h2>
<p class="lead">Bar X Ranch is rural but not remote. The honest summary: <b>nothing is far, and nothing
is close.</b> Almost every daily errand is a 12–20 minute drive, there is no walkable anything, and a
second car is not optional.</p>
""" + dist_table(['Daily essentials', 'Health care']) + """
<div class="note teal" style="margin-bottom:0;">
  <span class="lbl">The one surprise in this table</span>
  Your nearest supermarket is <b>not</b> in Angleton. The H-E-B in <b>West Columbia is 6.7 miles and
  13 minutes</b>, against 9.9 miles and 18 minutes to the Angleton H-E-B. The mailing address says
  Angleton; the shopping trip goes west. Same for the nearest pharmacy, police station and library —
  the Brazoria Community Library is <b>2.9 miles</b> away, easily the closest public building of any
  kind.
</div>
""", "24 · Services", "services")

add("""
<h2><span class="n">25 ·</span> Living here — schools, shopping and going out</h2>
""" + dist_table(['Schools — Columbia-Brazoria ISD', 'Shopping, dining, going out']) + """
<div class="cols2">
  <div class="note amber" style="margin-top:0;">
    <span class="lbl">Schools — read this carefully</span>
    <p style="margin-bottom:0;">All four lots are in <b>Columbia-Brazoria ISD</b>, confirmed parcel by
    parcel against the county's school-district layer — <b>not</b> Angleton ISD, despite the Angleton
    postal address. The campuses are in Brazoria and West Columbia, 7–14 miles west and south. Confirm
    the actual attendance zone for your lot directly with CBISD before you buy: district boundaries and
    campus assignments are different things, and this document deliberately does not reproduce school
    performance ratings, because the only dataset available to it is a decade out of date.</p>
  </div>
  <div class="note blue" style="margin-top:0;">
    <span class="lbl">Nightlife — set your expectations</span>
    <p style="margin-bottom:0;">Locally it is a handful of bars 16 minutes away and one country
    music venue in Brazoria at 23 minutes. A cinema and an enclosed mall are 26 minutes, in Lake
    Jackson. Anything you would recognise as a night out — restaurants with a wine list, live music
    with a choice of venue, theatre, clubs — is <b>Houston at 67 minutes</b> or <b>Galveston at 90</b>.
    That is a designated-driver drive, not a taxi ride. If frequent nightlife matters, this is the
    weakest column in the whole assessment.</p>
  </div>
</div>
""", "25 · Schools &amp; going out", "services2")

add("""
<h2><span class="n">26 ·</span> Living here — coast, resorts, amusements and the outdoors</h2>
""" + dist_table(['Coast, resorts and amusements']) + """
<div class="cols2">
  <div>
    <h3>What a weekend looks like</h3>
    <ul class="t wide">
      <li><b>Within 30 minutes:</b> your own two community lakes with boat ramps and a fishing pier;
          Sea Center Texas at Lake Jackson (a free state aquarium and fish hatchery, genuinely good
          with children); a golf course; and <b>Surfside Beach at 42 minutes</b> — a real Gulf beach
          you can drive onto.</li>
      <li><b>Within an hour:</b> Brazos Bend State Park, one of the best birding and alligator-watching
          parks in Texas; the San Bernard National Wildlife Refuge at 41 minutes; Space Center Houston
          at 72.</li>
      <li><b>90 minutes:</b> Galveston Island — the Pleasure Pier, Moody Gardens, Schlitterbahn
          waterpark (seasonal, roughly May to September), the Strand, and the San Luis Resort. This is
          the family holiday destination, and it is a comfortable day trip rather than a stay.</li>
      <li><b>Kemah Boardwalk</b> at 81 minutes covers the amusement-park itch without going to Houston.</li>
    </ul>
  </div>
  <div class="note green" style="margin-top:0;">
    <span class="lbl">Scenery and nature — the real draw</span>
    <p>This is the column where the location genuinely delivers, and it is why people move here. Bar X
    Ranch is 3,200 acres of large wooded lots, century live oaks, two lakes and bayou frontage in the
    Bastrop Bayou watershed. Bar X listings describe deer, hogs, raccoons, squirrels, bald eagles and
    a wide range of birds; the Central Flyway runs directly overhead, which makes spring and autumn
    migration exceptional from your own garden.</p>
    <p style="margin-bottom:0;"><b>The lot choice decides how much of this you get.</b> Lot 4 fronts a
    101-acre lake. Lot 1 fronts Mill Bayou along roughly half its perimeter, with mature trees. Lot 3
    has good frontage on a 12.6-acre pond. Lot 2 has the least — a short frontage on the same pond.</p>
  </div>
</div>
<div class="note amber" style="margin-bottom:0;">
  <span class="lbl">The nature you may not want</span>
  Coastal Brazoria County bayous and ponds hold <b>alligators</b>, and water moccasins are common. With
  children, dogs, or waterfowl, a waterfront lot in this county needs a fence and a rule about the
  water's edge. Feral hogs will find a vegetable garden, and raptors, raccoons and coyotes are exactly
  why the poultry question in §17 would have needed a well-built run anyway.
</div>
""", "26 · Coast &amp; outdoors", "leisure")


# =========================================================================== 27. community
add("""
<h2><span class="n">27 ·</span> Living here — the neighbourhood, and the Indian community</h2>
<p class="lead">You asked for a good, developed neighbourhood. On the census evidence this is a
markedly affluent, stable, almost entirely owner-occupied rural neighbourhood — and one with
essentially no Indian community in it.</p>
""" + table(
    ['Measure', 'Census Tract 6625 <span class="xs">(contains all four lots)</span>',
     'Brazoria County', 'Texas'],
    [([m[0], '<b>%s</b>' % m[1], m[2], m[3]], 'hi') if m[0] in
     ('Median household income', 'Owner-occupied share of homes',
      'Asian Indian (alone or in combination)') else [m[0], m[1], m[2], m[3]]
     for m in DEMOG],
    caption='US Census Bureau, American Community Survey 2024 five-year estimates (2020–2024). '
            + CF['n'], cls='compact') + """
<div class="cols2">
  <div class="note green" style="margin-top:0;">
    <span class="lbl">The neighbourhood is genuinely strong</span>
    <p style="margin-bottom:0;">Median household income of <b>$116,550</b> is 19% above the county and
    49% above Texas. <b>96.9% of homes are owner-occupied</b> — against 74% county-wide — which is an
    unusually low-churn, invested neighbourhood. Median home value is $384,100, comfortably above the
    county's $301,600, and the median age of 42.3 points to established families rather than a
    transient population. Bar X Ranch has been developed since 1980, has concrete streets, and is
    governed by a working POA that maintains frontages and amenities.</p>
  </div>
  <div class="note red" style="margin-top:0;">
    <span class="lbl">There is no Indian community here</span>
    <p style="margin-bottom:0;">The tract records <b>7 Asian residents out of 3,452</b> — 0.2% — and
    <b>no Asian Indian population at all</b> in the ACS estimate. Brazoria County as a whole has
    <b>6,414</b> people of Asian Indian origin, 1.6% of the county, but they are concentrated 30–40
    miles north around Pearland, not here. If cultural community, temple attendance, Indian grocery
    shopping and a peer group for children matter to you day to day, this address does not supply
    them locally — it supplies them at 55 to 75 minutes each way.</p>
  </div>
</div>
""" + dist_table(['Indian community']) + """
<div class="note blue">
  <span class="lbl">One genuinely encouraging fact</span>
  <b>Sri Meenakshi Temple — the largest South Indian temple complex in the region and the third Hindu
  temple built in the United States — is itself in unincorporated Brazoria County</b>, with a Pearland
  postal address. It is the same county as your lots, 39.5 miles and about 58 minutes north. The
  Houston metropolitan area has one of the largest Indian populations in the United States, and the
  Mahatma Gandhi District on Hillcroft is 73 minutes away. The community exists and it is substantial;
  it is simply at the other end of the county.
</div>
""" + dist_table(['Airports']) + """
<div class="note teal" style="margin-bottom:0;">
  <span class="lbl">Nearest international airport</span>
  <b>Houston Hobby (HOU) — 49.5 miles, 71 minutes</b> — is the nearest airport with international
  service, and the practical choice for domestic flying. <b>Bush Intercontinental (IAH) — 70.4 miles,
  95 minutes</b> — is the long-haul hub and the one that matters for direct flights to India. Texas Gulf
  Coast Regional is only 11.8 miles away but is a general-aviation field with no scheduled service.
  Budget <b>two hours to IAH</b> in practice; the 95-minute figure is free-flowing traffic, and the
  route crosses Houston's southern suburbs.
</div>
""", "27 · Neighbourhood", "community")

# =========================================================================== 28. amenities
add("""
<h2><span class="n">28 ·</span> Community amenities, the lakes and fishing</h2>
<p>The POA amenity base is the main thing your $400 a year buys, and it is better than the original
portfolio described.</p>
<div class="cols2">
  <div>
    <h3>What the POA maintains</h3>
    <ul class="t">
      <li><b>Two stocked lakes</b> with boat ramps and a fishing pier</li>
      <li><b>Two swimming pools</b></li>
      <li><b>Two clubhouses</b> — a lake house and a clubhouse, available to owners</li>
      <li>Tennis courts and basketball courts</li>
      <li>Two playgrounds, pavilions and picnic areas</li>
      <li>Campgrounds</li>
      <li>Concrete streets throughout the 3,200-acre subdivision</li>
      <li>Frontage mowing on vacant lots — charged to the owner under §3.13</li>
    </ul>
    <p class="sm">POA office: 1169 Bar X Trail, Angleton TX 77515 ·
    <a href="https://www.barxranch.org/">barxranch.org</a></p>
  </div>
  <div class="note amber" style="margin-top:0;">
    <span class="lbl">Correcting the fishing claims</span>
    <ul class="t" style="margin-bottom:0;">
      <li>Texas requires <b>no fishing licence</b> on water wholly enclosed within private property —
          and where that exemption applies, <b>no state bag or size limits apply either</b>. So the
          &ldquo;10 catfish per day&rdquo; in the original document cannot be state law. It can only be a
          <b>POA house rule</b>. """ + CF['v'] + """</li>
      <li><b>The private-water status is itself questionable.</b> The exemption requires the water not
          be subject to overflow from public water — and these lots sit in a mapped 1%-annual-chance
          floodplain in the Bastrop Bayou watershed, beside an impounded 101-acre pond. The flood
          finding undercuts the fishing premise.</li>
      <li>Statewide baselines, if the water is public: blue and channel catfish 25 per day combined,
          flathead 5 with an 18 in minimum, largemouth bass 5. <b>Black drum</b>, named in the original
          as an on-site species, is a brackish and saltwater fish — a bad data pull.</li>
      <li>The beach is <b>42 minutes</b>, not the &ldquo;20 minutes&rdquo; the original claimed.</li>
    </ul>
  </div>
</div>
<div class="note teal" style="margin-bottom:0;">
  <span class="lbl">What the water on your lot is, precisely</span>
  This matters, because &ldquo;waterfront&rdquo; has meant four different things in this portfolio.
  <b>Lot 1</b> fronts <b>Mill Bayou</b> and an impounded 13.0-acre widening of it, along roughly half
  its perimeter. <b>Lots 2 and 3</b> front opposite parts of the <b>same unnamed 12.6-acre pond</b> —
  Lot 3 with roughly twice the frontage of Lot 2. <b>Lot 4</b> fronts <b>Flag Pond, 101.5 acres</b>,
  and the levee that impounds it. Only Lot 4 is on what most people would call a lake.
</div>
""", "28 · Amenities &amp; fishing", "amenities")

# =========================================================================== 29. scorecard
def score_row(label, vals, weightnote=''):
    cells = []
    for v, cls in vals:
        cells.append('<td class="n" style="background:%s;font-weight:600;">%s</td>'
                     % ({'g': '#e7f2ea', 'a': '#fdf2e3', 'r': '#fdeae8', '': '#fff'}[cls], v))
    return '<tr><td>%s<br><span class="xs">%s</span></td>%s</tr>' % (label, weightnote,
                                                                     ''.join(cells))


SCORE = [
    ('Garden soil', 'Asa loam vs Pledger clay — §16',
     [('Excellent', 'g'), ('Excellent', 'g'), ('Poor', 'r'), ('Poor', 'r')]),
    ('Room to garden', 'acres of record',
     [('1.95 ac', 'g'), ('1.00 ac', 'r'), ('1.30 ac', 'a'), ('1.00 ac', 'r')]),
    ('Hobby farming — poultry', 'restrictions bar livestock on all four — §17',
     [('Barred', 'r'), ('Barred', 'r'), ('Barred', 'r'), ('Barred', 'r')]),
    ('Hobby farming — horses', '§3.15 formula on lot area',
     [('3 horses', 'g'), ('2 horses', 'a'), ('2 horses', 'a'), ('2 horses', 'a')]),
    ('Flood headroom', 'natural ground vs the 30 ft floor — §11',
     [('4–6 ft fill', 'a'), ('~2 ft fill', 'g'), ('3–4 ft fill', 'a'), ('6–7 ft fill', 'r')]),
    ('Rain ponding on the lot', 'hydrologic group',
     [('Group B', 'g'), ('Group B', 'g'), ('Group D', 'r'), ('Group D', 'r')]),
    ('Storm exposure', 'all four TDI Inland I, 120 mph',
     [('Equal', ''), ('Equal', ''), ('Equal', ''), ('Dam adjacent', 'r')]),
    ('Wildfire', 'county Relatively Low throughout',
     [('Negligible', 'g'), ('Negligible', 'g'), ('Negligible', 'g'), ('Negligible', 'g')]),
    ('Foundation risk', 'linear extensibility',
     [('LEP 4.5', 'g'), ('LEP 4.5', 'g'), ('LEP 19', 'r'), ('LEP 19', 'r')]),
    ('Septic cost', 'TCEQ class implied by permeability',
     [('$8–15k', 'g'), ('$8–15k', 'g'), ('$15–25k', 'r'), ('$15–25k', 'r')]),
    ('Septic layout fits?', 'field + 100% reserve + well + setbacks',
     [('Comfortable', 'g'), ('Tight — 187 ft wide', 'a'), ('Workable', 'a'),
      ('Tightest — 123 ft wide', 'r')]),
    ('Scenic beauty', 'water body and frontage',
     [('Mill Bayou, ½ perimeter', 'g'), ('Short pond frontage', 'r'),
      ('Good pond frontage', 'a'), ('101-acre lake', 'g')]),
    ('Quiet', 'distance to State Highway 35',
     [('0.09 mi — noisiest', 'r'), ('0.37 mi', 'a'), ('0.10 mi — noisy', 'r'),
      ('1.03 mi — quietest', 'g')]),
    ('Access to amenities', 'all four within 1.5 mi of each other',
     [('Equal', ''), ('Equal', ''), ('Equal', ''), ('+2–3 min', 'a')]),
    ('Neighbourhood', 'same tract, same POA, same ISD',
     [('Equal', ''), ('Equal', ''), ('Equal', ''), ('Equal', '')]),
    ('Jurisdiction', 'county only, or also a city ETJ',
     [('County only', 'g'), ('Baileys Prairie ETJ', 'a'), ('County only', 'g'),
      ('County only', 'g')]),
    ('Price', 'asking',
     [('$82,500', 'r'), ('$45,000', 'g'), ('$49,000', 'g'), ('$58,000', 'a')]),
    ('Value against county appraisal', 'premium or discount',
     [('+26.9%', 'r'), ('+25.0%', 'r'), ('−5.5%', 'g'), ('+16.0%', 'a')]),
]
add("""
<h2><span class="n">29 ·</span> Scorecard against your brief</h2>
<p>Eighteen tests, weighted to what you said matters: gardening, hobby farming, quick access to
amenities, a good and developed neighbourhood, scenery and nature, and safety from flood and storm.
Green is good, amber is a compromise, red is a problem.</p>
<table class="compact">
  <thead><tr><th style="width:44mm;">Test</th>
    <th class="n">Lot 1<br><span class="xs" style="font-weight:400;">1127 Saddle Horn</span></th>
    <th class="n">Lot 2<br><span class="xs" style="font-weight:400;">336 Wagon Wheel W</span></th>
    <th class="n">Lot 3<br><span class="xs" style="font-weight:400;">29 Broken Arrow</span></th>
    <th class="n">Lot 4<br><span class="xs" style="font-weight:400;">750 Wagon Wheel</span></th></tr></thead>
  <tbody>
""" + ''.join(score_row(l, v, n) for l, n, v in SCORE) + """
    <tr class="tot"><td>Green / amber / red</td>
      <td class="n">9 / 3 / 3</td><td class="n">8 / 5 / 3</td>
      <td class="n">3 / 5 / 7</td><td class="n">3 / 3 / 9</td></tr>
  </tbody>
</table>
<div class="note green" style="margin-bottom:0;">
  <span class="lbl">Conclusion — buy Lot 1, 1127 Saddle Horn Bend, at a negotiated price</span>
  <p>It carries the most greens and, more importantly, the right ones. It is the only lot that combines
  <b>good garden soil</b> with <b>room to use it</b> and <b>real scenery</b> — and soil and space are
  the two things you cannot buy later. Its weaknesses are all things money or design can fix: a 4–6 ft
  pad, and highway noise that a treed 1.95-acre lot and a house set back from the frontage will
  substantially absorb.</p>
  <p style="margin-bottom:0;"><b>Open at $65,000 — the county's appraised value — and be willing to go
  to about $72,000.</b> At $82,500 you are paying a 26.9% premium to the county's own number on a lot
  that also needs the second-deepest pad in the portfolio. If the seller will not move below roughly
  $75,000, take <b>Lot 2 at $45,000</b> instead: the same excellent soil and three feet more flood
  headroom, and accept the smaller garden. <b>Do not buy Lots 3 or 4</b> — the Pledger clay costs you
  more in septic and foundation than you save on land, and Lot 4's dam is an unquantified risk.</p>
</div>
""", "29 · Scorecard", "scorecard")


# =========================================================================== 30. corrections
add("""
<h2><span class="n">30 ·</span> What changed, edition by edition</h2>
<p>The original generated portfolio, the v2 rebuild, and this edition. Only the items where the answer
actually moved are listed.</p>
""" + table(
    ['#', 'Original portfolio said', 'v2 corrected it to', '<b>v3 establishes</b>'],
    [['1', '<span class="strike">No parcel identifiers at all</span>', 'Same — none available',
      '<b>PID, geo ID, legal description, deed reference for all four</b>'],
     ['2', '<span class="strike">Lot 29 ~1.0 ac "est."</span>', 'Unresolved',
      '<b>1.30 ac of record</b> — $/acre falls to $37,692'],
     ['3', '<span class="strike">750 Wagon Wheel 1.0 or 1.27 ac</span>', 'Unresolved',
      '<b>1.00 ac of record</b>; the 1.27 figure is wrong'],
     ['4', '<span class="strike">Lot 29 is interior</span>', 'Repeated as interior',
      '<b>Waterfront</b> — 7 of 13 boundary vertices within 60 ft of a 12.6 ac pond'],
     ['5', '<span class="strike">Panel 48039C0605K</span>', 'Repeated as verified',
      '<b>Panel 48039C0420K</b>, eff. 30 Dec 2020'],
     ['6', '<span class="strike">BFE ~24 ft; build at grade</span>',
      'Flagged the range, kept 24 ft as plausible',
      '<b>Nearest published BFE line is 28 ft NAVD88</b> at every lot'],
     ['7', '<span class="strike">Natural ground 28–30 ft</span>', 'Repeated, flagged unverified',
      '<b>24–28 ft</b> from county LiDAR — so 2–6 ft of fill is mandatory'],
     ['8', '<span class="strike">Fill "minimal"</span>', '$0–$8,000, optional',
      '<b>$12,000–$45,000, and not optional</b>'],
     ['9', '<span class="strike">Soil class unknown</span>', 'Unknown; assumed Class III–IV',
      '<b>Asa loam on Lots 1–2, Pledger vertisol on Lots 3–4</b> — a 43× permeability difference'],
     ['10', '<span class="strike">No foundation risk noted</span>', 'Not noted',
      '<b>LEP 19 on Lots 3–4</b> — post-tensioned or piered design'],
     ['11', '<span class="strike">Minimum dwelling 1,800 sq ft</span>', 'Repeated, flagged unverified',
      '<b>1,100 sq ft</b> in the recorded instrument'],
     ['12', '<span class="strike">"ACC Rev 2" governs all four</span>', 'Flagged as doubtful',
      '<b>Three different recorded instruments</b> — 1515/679, 1532/471, 84-29/885'],
     ['13', '<span class="strike">Silent on animals</span>', 'Silent',
      '<b>Livestock barred except horses; one horse barn only</b> — poultry very likely prohibited'],
     ['14', '<span class="strike">No tax at all</span>',
      'County + CBISD + hospital + drainage districts',
      '<b>County + CBISD + ESD only</b> — no hospital, drainage or college district'],
     ['15', '<span class="strike">Carry not modelled</span>', '$5,050–$5,750/yr on four lots',
      '<b>$4,650–$5,520/yr</b>, and $1,350–$1,730 on one'],
     ['16', '<span class="strike">Windstorm omitted</span>', 'TWIA average $2,541; WPI-8 required',
      '<b>TDI Inland I, 120 mph</b> — the zone boundary follows SH 35'],
     ['17', '<span class="strike">Jurisdiction unstated</span>', 'Unincorporated county',
      '<b>Lot 2 is inside the Baileys Prairie ETJ</b>; the other three are not'],
     ['18', '<span class="strike">Surfside 20 min</span>', '~30 min', '<b>42 min</b> by road'],
     ['19', '<span class="strike">10 catfish/day as state law</span>',
      'Shown to be impossible as state law', 'Confirmed a POA house rule at most'],
     ['20', '<span class="strike">No dam or levee noted</span>', 'Not noted',
      '<b>Lot 4 abuts Flag Lake Levee (NID TX06298)</b>, unrated; Lot 1 downstream of TX01759'],
     ['21', '<span class="strike">Cheapest waterfront framing</span>',
      'Ranked 1127 Saddle Horn cheapest per acre',
      '<b>All four are waterfront</b>; Lot 29 is cheapest per acre'],
     (['22', '<span class="strike">Total 9 pages, no drawings</span>', '12 sections, no drawings',
       '<b>True-scale plans and terrain sections for all four lots</b>'], 'tot')],
    cls='compact') + """
<p class="xs" style="margin-bottom:0;">The full claim-by-claim audit of the original document remains
in <a href="docs/AUDIT.md">docs/AUDIT.md</a>. The evidence trail for everything new in this edition,
including the exact service queries, is in <a href="docs/EVIDENCE.md">docs/EVIDENCE.md</a>.</p>
""", "30 · Corrections", "corrections")

# =========================================================================== 31. due diligence
add("""
<h2><span class="n">31 ·</span> What to do next, in this order</h2>
<p class="lead">Nine of these cost almost nothing and between them they resolve every remaining
material unknown. Do them before you make an offer, not after.</p>
<ol class="steps" style="font-size:9.6pt;">
  <li><b>Ask the POA the poultry question in writing.</b> &ldquo;May I keep a small number of chickens
      and ducks, and may I build a coop and a greenhouse?&rdquo; If the answer is no and that is
      unacceptable, stop here and look at unrestricted acreage instead — everything below becomes
      moot. <span class="xs">Free. One email to office@barxranch.org.</span></li>
  <li><b>Pull the recorded restrictions for the specific lot</b> from the Brazoria County Clerk —
      1515/679 for Sections 1 lots, 1532/471 for Section 2, 84-29/885 for Section 16 — plus a POA
      resale certificate showing dues, transfer fees and any assessments.
      <span class="xs">Under $100.</span></li>
  <li><b>Confirm Lot 29's identity.</b> Its situs of record is &ldquo;HIGHWAY 35&rdquo; with no street
      number. Verify the listing refers to <b>PID 186219</b> and not another Section 16 lot.
      <span class="xs">Free — BCAD and the listing agent.</span></li>
  <li><b>Order an OSSF site and soil evaluation</b> on the shortlisted lot. This is the highest-value
      money in the project: it converts §16's survey-scale inference into the permit-governing soil
      class, and it swings the septic budget by up to $17,000.
      <span class="xs">$350–$600.</span></li>
  <li><b>Request a written BFE determination per lot</b> from Brazoria County Floodplain &amp; 911
      Administration, 451 N Velasco Ste 210, Angleton TX 77515 · 979-864-1295. Ask which cross-section
      governs the lot — Mill Bayou governs Lot 1 and it is a different watercourse from the one
      governing Lots 2 and 3. <span class="xs">Free.</span></li>
  <li><b>Get three quotes for the electric service extension</b>, per lot. This is a $0–$25,000 line
      and the utility will tell you over the phone. <span class="xs">Free.</span></li>
  <li><b>Ask TCEQ Dam Safety about Flag Lake Levee (NID TX06298)</b> — hazard classification, condition
      and inspection history — if Lot 4 is still under consideration. And about Bar X Development Dam
      (TX01759) for Lot 1. <span class="xs">Free.</span></li>
  <li><b>Confirm the school attendance zone</b> for the specific lot with Columbia-Brazoria ISD, and
      confirm broadband availability at the address with the providers. Neither can be settled from a
      desk, and both shape daily life. <span class="xs">Free.</span></li>
  <li><b>Confirm the TDI windstorm zone</b> for the parcel against TDI's own Brazoria County map. §21
      places all four in Inland I, but the dividing line follows SH 35 and Lots 1 and 3 are within 530
      ft of it. <span class="xs">Free.</span></li>
  <li><b>Order a boundary and topographic survey</b> on the lot you intend to buy, then test a real
      2,400–2,800 sq ft footprint at 30 ft finished floor against the septic field, the 100% reserve,
      the well at 100 ft, the 75 ft water setback and your garden. <span class="xs">$1,500–$3,500.</span></li>
  <li><b>Get TWIA windstorm and Risk Rating 2.0 flood quotes</b> on the actual proposed structure, and
      price excess flood cover above the $250,000 NFIP building cap.</li>
  <li><b>Then make the offer</b>, anchored on the county appraised value, and only then commission
      design.</li>
</ol>
<div class="note teal" style="margin-bottom:0;">
  <span class="lbl">Total cost of resolving every remaining unknown</span>
  Roughly <b>$2,400–$4,800</b> and a fortnight, against a build of $505,000–$950,000. Steps 1 to 9 cost
  under $700 between them and would change the recommendation in this document if any of them came back
  differently.
</div>
""", "31 · Next steps", "next")

# =========================================================================== 32. sources & sign-off
add(f"""
<h2><span class="n">Sources, limitations and sign-off</span></h2>
<h3>Primary sources used in this edition</h3>
<table class="compact">
  <thead><tr><th>Source</th><th>Used for</th></tr></thead>
  <tbody>
    <tr><td><b>Brazoria County public ArcGIS</b> — general/Parcels, general/Floodplain, general/LiDAR,
      general/Taxing_Entities, general/Legal_and_Development, general/Roads, general/Community_Features</td>
      <td>Parcel record, FEMA zone and FIRM panel per parcel, published BFE lines, 1 ft elevation
      contours, taxing districts, recorded plats and restriction references, street centrelines,
      school locations</td></tr>
    <tr><td><b>USGS 3DEP</b> 1 m digital elevation model</td><td>The A–B terrain profiles in §12–15</td></tr>
    <tr><td><b>USDA NRCS SSURGO</b>, Brazoria County soil survey</td>
      <td>Soil series, texture, permeability, shrink-swell, drainage class, hydrologic group (§16)</td></tr>
    <tr><td><b>Bar X Ranch declaration of restrictions</b> as recorded (Deed Vol. 1679, Pg. 695)</td>
      <td>Permitted structures, livestock, dwelling size, fences, setbacks, lot maintenance (§17)</td></tr>
    <tr><td><b>30 TAC §285.91</b> (TCEQ OSSF)</td><td>Wastewater flow, tank sizing, loading rates,
      separation distances (§18)</td></tr>
    <tr><td><b>Brazoria County</b> building permit fee schedule, permit application, floodplain
      administration</td><td>Permit cost, the 24-inch freeboard standard, contact route</td></tr>
    <tr><td><b>FEMA</b> — National Risk Index (Dec 2025), LOMA/LOMR-F guidance, FIS 48039CV001A</td>
      <td>Hazard ratings (§23), map-amendment routes, study effective date</td></tr>
    <tr><td><b>Texas Department of Insurance</b> — windstorm zone map and community list for Brazoria
      County</td><td>Inland I 120 mph determination, WPI-8 obligation (§21)</td></tr>
    <tr><td><b>TWIA</b> — published rates and liability report</td><td>Windstorm premium (§21)</td></tr>
    <tr><td><b>TPWD</b> — private-water fishing exemption, freshwater bag and length limits</td>
      <td>Correcting the fishing claims (§28)</td></tr>
    <tr><td><b>US Census Bureau</b> — ACS 2024 five-year estimates, tract 6625</td>
      <td>Demographics, income, tenure, Indian population (§27)</td></tr>
    <tr><td><b>ERA5 reanalysis</b>, daily 1991–2020 at the parcels</td>
      <td>Climate normals in Celsius, frost dates, growing season (§22)</td></tr>
    <tr><td><b>OpenStreetMap</b> and <b>OSRM</b>; <b>National Inventory of Dams</b></td>
      <td>Water-body geometry and frontage measurement, road distances and drive times, dam records</td></tr>
  </tbody>
</table>
<p class="sm">Source content has been paraphrased and summarised rather than quoted at length, except
for short quotations from the recorded deed restrictions in §17, where the exact wording is the point.
The full register, including everything that could <b>not</b> be verified, is in
<a href="docs/SOURCES.md">docs/SOURCES.md</a>; the machine-retrieved evidence and the exact queries
are in <a href="docs/EVIDENCE.md">docs/EVIDENCE.md</a>.</p>

<h3>What remains unverified</h3>
<p class="sm">Site-specific BFE in writing for any lot · the TCEQ soil class from a site evaluation ·
distance to three-phase power at each lot · the recorded restriction instrument for each specific
section · POA dues, mowing and transfer fees from a resale certificate · ESD 1 and 2 tax rates ·
Angleton Levee accreditation status · Flag Lake Levee hazard class and condition · Brazoria County CRS
class · whether the POA permits poultry in practice · broadband availability at the addresses ·
current school attendance zones and campus performance.</p>

<div class="note red">
  <span class="lbl">Disclaimer</span>
  This is an independent desktop screening study prepared from published regulation, public records and
  open government data. It is <b>not</b> a survey, an engineering or geotechnical opinion, a flood
  determination, an elevation certificate, insurance advice, legal advice, tax advice or an appraisal,
  and it is not a substitute for the licensed professionals and the written county determinations named
  in §31. No lot has been visited, surveyed or soil-tested. Elevations derive from remote-sensing models
  and are indicative only. Figures marked <span class="cf e">estimate</span> are planning ranges;
  figures marked <span class="cf u">unverified</span> derive from third-party listing copy or a
  superseded edition. Prices, tax rates, insurance premiums and listing status change without notice.
  Do not rely on any figure in this document for a purchase, financing or construction decision without
  independent confirmation.
</div>

<div class="sig">
  <div class="for">Prepared as required for</div>
  <div class="who">{PREPARED_FOR}</div>
  <div class="on">on <b>{PREPARED_ON}</b></div>
  <hr class="r" style="margin:4mm 0;">
  <div class="sm">Bar X Ranch — Four-Lot Feasibility Portfolio · version {VERSION} ·
  @@N@@ pages · supersedes v2.0 of 10 September 2026 and the original generated portfolio.<br>
  Subject parcels: PID 183667, 183367, 186219, 183332 — Bar X Ranch Sections 1, 2 and 16,
  unincorporated Brazoria County, Angleton, Texas 77515.</div>
</div>
""", "Sources &amp; sign-off", "sources")

# =========================================================================== render
# Real printed page numbers come from data/pagination.json, written by tools/paginate.py
# after measuring the rendered sheets. Until that file exists we fall back to sheet order.
PAGES = {}
TOTAL_PAGES = len(SHEETS)
pgfile = os.path.join(ROOT, 'data', 'pagination.json')
if os.path.exists(pgfile):
    _pg = json.load(open(pgfile))
    PAGES = _pg.get('sheets', {})
    TOTAL_PAGES = _pg.get('total_pages', len(SHEETS))


def page_span(anchor, i):
    """(first, last) printed page for a sheet."""
    if anchor and anchor in PAGES:
        return PAGES[anchor]['start'], PAGES[anchor]['end']
    return i, i


toc_items = []
for i, (anchor, foot, _) in enumerate(SHEETS, start=1):
    if anchor in (None, 'cover', 'toc'):
        continue
    a, b = page_span(anchor, i)
    toc_items.append('<li><a href="#%s">%s</a><span class="pgn">%s</span></li>'
                     % (anchor, foot, a if a == b else '%d–%d' % (a, b)))
half = (len(toc_items) + 1) // 2
TOC = ('<div class="toc"><ol style="list-style:none;padding-left:0;">%s</ol>'
       '<ol style="list-style:none;padding-left:0;">%s</ol></div>'
       % (''.join(toc_items[:half]), ''.join(toc_items[half:])))

out = ['<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">',
       '<meta name="viewport" content="width=device-width, initial-scale=1">',
       '<title>Bar X Ranch — 4-Lot Feasibility Portfolio v%s — prepared for %s</title>'
       % (VERSION, PREPARED_FOR),
       '<meta name="description" content="Four-lot land feasibility study, Bar X Ranch, Angleton, '
       'Brazoria County, Texas — parcel record, flood and terrain analysis, soil, cost, livability.">',
       '<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">',
       '<style>%s</style></head><body>' % CSS]

for i, (anchor, foot, html) in enumerate(SHEETS, start=1):
    html = html.replace('@@TOC@@', TOC)
    a, b = page_span(anchor, i)
    pg = ('<b>Page %d of %d</b>' % (a, TOTAL_PAGES) if a == b
          else '<b>Pages %d–%d of %d</b>' % (a, b, TOTAL_PAGES))
    out.append('<section class="sheet"%s>' % (' id="%s"' % anchor if anchor else ''))
    out.append('<span class="smark" aria-hidden="true">[[S:%s]]</span>' % (anchor or i))
    out.append(html)
    out.append('<div class="foot"><span><b>Bar X Ranch — Four-Lot Feasibility Portfolio</b> '
               'v%s · prepared for %s · %s</span>'
               '<span class="pg">%s &nbsp;·&nbsp; %s</span></div>'
               % (VERSION, PREPARED_FOR, PREPARED_ON, foot, pg))
    out.append('</section>')

out.append("""
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script>
(function(){
  var tabs=document.getElementById('tabs');
  if(tabs){
    var frame=tabs.parentNode.querySelector('.map iframe');
    tabs.addEventListener('click',function(e){
      var b=e.target.closest('.tab'); if(!b||!frame) return;
      tabs.querySelectorAll('.tab').forEach(function(t){t.setAttribute('aria-selected','false');});
      b.setAttribute('aria-selected','true');
      frame.src=b.getAttribute('data-src');
    });
  }
  var el=document.getElementById('leaf');
  if(el&&window.L){
    fetch('data/parcels.geojson').then(function(r){return r.json();}).then(function(gj){
      var map=L.map('leaf',{scrollWheelZoom:false});
      L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        {maxZoom:19,attribution:'Imagery &copy; Esri, Maxar, Earthstar Geographics'}).addTo(map);
      var cols={lot1:'#0f766e',lot2:'#1c3ba8',lot3:'#15602f',lot4:'#a91f14'};
      var layer=L.geoJSON(gj,{
        style:function(f){return {color:cols[f.id]||'#fff',weight:3,fillOpacity:.14,fillColor:cols[f.id]};},
        onEachFeature:function(f,l){
          var p=f.properties;
          l.bindPopup('<b>Lot '+p.lot+' &middot; '+p.listing_name+'</b><br>'+
            'PID '+p.pid+' &middot; '+p.acres_of_record+' ac of record<br>'+
            p.legal_description+'<br>Asking $'+p.asking_price_usd.toLocaleString()+
            ' &middot; appraised $'+p.bcad_appraised_usd.toLocaleString()+
            '<br>Zone '+p.fema_zone_2020+' &middot; panel '+p.firm_panel);
          l.bindTooltip('Lot '+p.lot,{permanent:true,direction:'center',className:'lotlbl'});
        }}).addTo(map);
      map.fitBounds(layer.getBounds().pad(0.25));
    }).catch(function(){
      el.innerHTML='<div style="padding:8mm;font-size:9pt;color:#54666d">'+
        'The recorded-boundary map needs the page served over http with internet access. '+
        'Open data/parcels.geojson directly, or use the Google map above.</div>';
    });
  }
})();
</script>
<style>.lotlbl{background:rgba(22,38,44,.82);border:0;color:#fff;font-weight:700;font-size:9px;
  box-shadow:none;padding:1px 4px;}.lotlbl:before{display:none;}</style>
</body></html>""")

doc = ''.join(out)
doc = doc.replace('%%ALL%%', gmap_all()).replace('%%AREA%%', GMAP_AREA)
doc = doc.replace('@@N@@', str(TOTAL_PAGES))
with open(OUT, 'w') as fh:
    fh.write(doc)
print("wrote %s — %d sheets, %d printed pages, %.0f kB"
      % (OUT, len(SHEETS), TOTAL_PAGES, len(doc) / 1024))
