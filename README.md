# Bar X Ranch — 5-Lot Feasibility Portfolio

Independent feasibility review of five vacant lots in Bar X Ranch, unincorporated Brazoria County,
Angleton, Texas 77515 — assessed for a five-bedroom build, and for what it is actually like to live
there.

**Current edition: v4.0, 13 September 2026, prepared for Mohsin Chowdhury.** 51 pages, paginated, five lots.

## Contents

| File | What it is |
|------|-----------|
| [`index.html`](index.html) | **The artifact (v4.0)** — 51 numbered A4 pages. Open in a browser; print to PDF at 100% for true-scale drawings. |
| [`Bar-X-Ranch-5-Lot-Feasibility-v4.0.pdf`](Bar-X-Ranch-5-Lot-Feasibility-v4.0.pdf) | **Rendered PDF of the current edition** — A4, 51 pages, true scale. |
| [`letters/`](letters) | **County correspondence** — a formal BFE request letter per parcel, a combined five-lot letter, and the same requests as plain-text e-mail drafts. See Appendix B. |
| [`data/parcels.geojson`](data/parcels.geojson) | The four parcels as recorded boundaries, from the county's BCAD parcel service |
| [`data/terrain.json`](data/terrain.json) | 1 ft LiDAR contours, A–B transects and 1 m DEM elevation profiles per lot |
| [`data/fill.json`](data/fill.json) | Pad geometry, fill volumes and costs per lot |
| [`data/pagination.json`](data/pagination.json) | Measured page numbers, written by `tools/paginate.py` |
| [`tools/build_artifact.py`](tools/build_artifact.py) | Builds `index.html`. All figures baked in as literals. |
| [`tools/terrain.py`](tools/terrain.py) | Rebuilds `data/terrain.json` from the county and USGS elevation services |
| [`tools/terrain_svg.py`](tools/terrain_svg.py) | Renders the true-scale plans and terrain sections |
| [`tools/aerials.py`](tools/aerials.py) | Builds the twelve lot aerials from USGS NAIP |
| [`tools/fill.py`](tools/fill.py) | Costs the flood-headroom pad on each lot from a DEM grid |
| [`tools/satmap.py`](tools/satmap.py) | Composes the full-page satellite plate — stitches Esri World Imagery tiles, draws boundaries, pins and name tags |
| [`tools/letters.py`](tools/letters.py) | Generates the `letters/` PDFs and e-mail drafts from the parcel and terrain data |
| [`tools/paginate.py`](tools/paginate.py) | Two-pass pagination — measures the real print, then fixes every page number and verifies it |
| [`docs/EVIDENCE.md`](docs/EVIDENCE.md) | Every v3 finding with the exact query that produced it |
| [`docs/AUDIT.md`](docs/AUDIT.md) | Claim-by-claim audit of the original generated portfolio |
| [`docs/SOURCES.md`](docs/SOURCES.md) | Source register, and an explicit list of what could not be verified |
| `assets/photos/` | Drop listing photographs here as `lot1-1.jpg` … `lot4-3.jpg` and the artifact picks them up |

## The four lots

| Lot | PID | Acres of record | Asking | County appraised | Soil | Fill to 30 ft | Pad cost (mid) |
|---|---|---|---|---|---|---|---|
| 1127 Saddle Horn Bend | 183667 | 1.95 | $82,500 | $65,030 | Asa silty clay loam | 4.2 ft | $48,600 |
| **336 Wagon Wheel Trail W** | 183367 | 1.00 | **$45,000** | $36,000 | Asa silty clay loam | **0.7 ft** | **$20,400** |
| Lot 29 Broken Arrow Trail | 186219 | 1.30 | $49,000 | $51,870 | Pledger clay | 3.0 ft | $37,500 |
| 750 Wagon Wheel Trail | 183332 | 1.00 | $58,000 | $50,000 | Pledger clay | 3.8–5.2 ft | $44,700–58,200 |
| 808 Wagon Wheel Trail | 183331 | 1.07 | **$100,000** | $53,280 | Pledger clay | 4.7 ft | $53,200 — **pad does not fit** |

Cost to reach build-ready (asking price + calculated pad at mid-case + the $20k vertisol foundation
upcharge on the clay lots): **Lot 2 ~$65k**, Lot 3 ~$107k, Lot 4 ~$123k, Lot 1 ~$131k,
**Lot 5 ~$173k**. Portfolio: $334,500 asking across 6.32 ac, +30.6% over the $256,180 appraised.

## What v4.0 changed

- **808 Wagon Wheel is asking $100,000** (MLS 84275418) — resolved from the listing. That is
  **$93,458 per acre**: 2.5× Lot 3, 61% above its own neighbour Lot 4, and **+87.7% over the county's
  appraisal**, the largest premium of the five by a factor of three. Combined with the pad that does not
  fit, the deepest lift and the worst soil, the verdict on Lot 5 is to **rule it out**. It scores
  4 green / 2 amber / 14 red — the weakest of the five.
- **The scorecard price, price-per-acre, premium and cost-to-build-ready rows, and the green/amber/red
  tally, are now computed at build time** rather than maintained by hand. Doing so exposed two more
  drifted figures: cost-to-build-ready for Lots 3 and 4 had been carrying $109k and $139k against
  actual $107k and $123k.

- **Water regime and stocking, per lot.** Mill Bayou is classified **intermittent** in the National
  Hydrography Dataset (FCode 46003), so it does not flow year-round: expect low or no flow **late May to
  September, worst in July and August**, derived from a Thornthwaite water balance on the artifact's own
  ERA5 normals (July runs −103 mm). **Only Lot 1 fronts that seasonal channel** — Lots 2–5 front
  *impounded* water that holds through the summer, and what is nearest Lots 4 and 5 is a **canal/ditch**,
  drainage infrastructure rather than an amenity. **Nothing here is state-stocked:** neither Mill Bayou
  nor Flag Pond appears in TPWD's stocked water-body list, and Bastrop Bayou itself reports no stockings
  this year. The fishery is the POA's own two lakes.
- **Every lot heading now links to Zillow** — Lot 5 to its resolved listing page, the other four to a
  Zillow address search built from the marketed address.

- **Plate 1 · Satellite view** — a full page (page 8) showing all five parcels on high-resolution
  satellite imagery with recorded boundaries, numbered stamp pins, name tags with PID and acreage, a
  scale bar and a north arrow. Built by `tools/satmap.py` from Esri World Imagery at 0.8 m/px,
  composed at 2,400 px for print.

- **808 Wagon Wheel Trail added as a fifth lot** (PID 183331, Lot 131, 1.07 ac of record), taken through
  the full pipeline: parcel record, flood zone and panel, nearest published BFE, 1 ft LiDAR contours and a
  USGS 3DEP terrain section, SSURGO soil, pad and fill cost, aerials, scorecard, carrying cost, and its
  own county BFE request letter and e-mail draft.
- **It is Lot 4's immediate neighbour** — Lot 131 beside Lot 132, about 85 ft apart on the same Flag Pond
  shoreline — which is why their terrain profiles and hazards read almost identically.
- **The building pad does not fit.** At 490 × 110 ft the parcel is the narrowest in the study and the pad
  plus its graded side slopes needs 116 ft against the 110 ft available. It is the only lot of the five
  where the geometry fails outright rather than merely running tight, and it also needs the deepest lift
  (4.69 ft) and the most fill (1,603 cu yd).
- **Asking price is outstanding.** The parcel is actively listed (Zillow zpid 305175997) but every listing
  portal blocks automated retrieval, so price-dependent cells are marked *pending* rather than estimated.
- **The scorecard tallies are now computed from the data** instead of being maintained by hand — which
  revealed the v3.5 totals had drifted and were wrong.
- Sections renumbered: lots are §6–§10, terrain §13–§17, and everything from Soil onward shifts by two.

## What v3.5 changed

- **Appendix A · Engagement brief** added as the closing pages (36–37) — a traceability record of the
  requirements that produced the document and the section that answers each. Structured as
  **A.1** the original brief as raised (subject properties, the three core questions, information
  requested, deliverables), **A.2** the later instruction to audit and rebuild the first attempt, and
  **A.3** delivery.
- **Appendix C · The four draft e-mails** — all four requests reproduced in full, one per page, so the
  document is complete on its own. Generated by importing `tools/letters.py`, so the appendix and the
  sendable `letters/EMAIL-DRAFTS.md` are produced by the same code and cannot fall out of step.
- **Appendix B · County correspondence** added, and with it the `letters/` folder — the last of the
  requested deliverables. Four formal BFE request letters, one per parcel, plus a combined four-lot
  document and four plain-text e-mail drafts. Generated by `tools/letters.py` from the parcel record and
  the terrain model, so the correspondence cannot drift out of step with the report. Each letter asks ten
  common questions and two or three specific to its parcel — the Flag Lake Levee beside 750 Wagon Wheel,
  the HIGHWAY 35 situs discrepancy on Lot 29, the governing watercourse at 1127 Saddle Horn.
- **Appendix A records what is still open, rather than implying completeness.** The BFE diagram is
  marked *superseded* because its three premise figures no longer hold; the FIRM panel extraction is
  *partly delivered* against the corrected panel 48039C0420K (no panel image embedded); and *compare the
  documents* stays partly open because no second document was ever supplied. Everything else asked for
  has now been produced.
- **A note on where the original premise moved** — the FIRM panel, the published BFE, "zoning 0140" and
  the freeboard arithmetic were all framed on figures the county record has since contradicted. The
  brief is recorded as asked, with the corrections stated alongside so the change is visible.
- Version now flows from a single constant into the title, every footer and the print
  running-header, instead of being hard-coded in the stylesheet.

## What v3.0 changed

- **All four lots identified in the county record** for the first time — PID, legal description,
  acreage of record, appraised value, deed reference. Nineteen previously open questions closed.
- **FIRM panel is 48039C0420K**, not 48039C0605K.
- **The nearest published BFE is 28 ft NAVD88**, not the 24 ft both earlier editions assumed, and
  county LiDAR puts natural ground at 24–28 ft — so a 2–6 ft pad is mandatory on every lot, and
  building at grade is not an option.
- **The soils differ between the lots.** Lots 1 and 2 are a well-drained prime-farmland loam; Lots 3
  and 4 are a 70% clay shrink-swell vertisol that forces an aerobic septic system and an engineered
  foundation. This, not price, decides the recommendation.
- **The recorded restrictions bar livestock other than house pets and horses**, and permit only a
  dwelling, a garage and one horse barn per lot — so keeping chickens and ducks is very unlikely to
  be permitted.
- **Lot 29 is 1.30 acres and is waterfront**, not ~1.0 acres and interior. **750 Wagon Wheel is 1.00
  acre**, not 1.27.
- **Lot 4 abuts the Flag Lake Levee** (NID TX06298), which impounds a 101-acre lake above the
  buildable part of that lot and carries no published hazard classification.
- **Tax model corrected** — these parcels are in no hospital, drainage or junior-college district.
- **The pad is now calculated, not estimated** (§20). Fill to reach the 30 ft floor ranges from
  **0.7 ft / 268 cu yd / ~$20,400 on Lot 2** to **5.2 ft / 1,808 cu yd / ~$58,200 on Lot 4**. That
  $38,000 spread, plus the soil difference, is what decides the recommendation — and it moved the
  answer from Lot 1 to **Lot 2**.
- Added true-scale plans and terrain sections per lot, and a livability chapter covering climate in
  Celsius, hazards, services, schools, distances, demographics, the Indian community and airports.

## Rebuilding

```
pip install Pillow pypdf

python3 tools/aerials.py          # writes the twelve lot aerials
python3 tools/fill.py             # costs the pad on each lot
python3 tools/build_artifact.py   # writes index.html
python3 tools/paginate.py         # measures the print and corrects every page number
python3 tools/terrain.py          # only needed to refresh the elevation data
```

`paginate.py` needs headless Chrome. No API keys are required anywhere.

### A note on image resolution

USGS NAIP is **30 cm** ground sample distance, and nothing sharper is published for this area —
Esri World Imagery tops out near 26 cm here and serves empty tiles above zoom 19. The aerials are
therefore sampled at a fixed **0.15 m/px**, a 2× oversample of the source, which is the honest
ceiling: asking the server for 0.06 m/px, as a first attempt did, only interpolated the same 30 cm
data five times over and looked soft. Each image states its own m/px in the corner.

## Status

**Desktop screening study.** No lot has been visited, surveyed or soil-tested, and no BFE has been
confirmed in writing. Elevations come from remote-sensing models, not from an instrument survey. See
the due-diligence sequence in §31 of the artifact and the disclaimer on its final page before relying
on any figure.
