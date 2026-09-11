# Bar X Ranch — 4-Lot Feasibility Portfolio

Independent feasibility review of four vacant lots in Bar X Ranch, unincorporated Brazoria County,
Angleton, Texas 77515 — assessed for a five-bedroom build, and for what it is actually like to live
there.

**Current edition: v3.0, 11 September 2026, prepared for Mohsin Chowdhury.** 35 pages, paginated.

## Contents

| File | What it is |
|------|-----------|
| [`index.html`](index.html) | **The artifact (v3.0)** — 34 numbered A4 pages. Open in a browser; print to PDF at 100% for true-scale drawings. |
| [`data/parcels.geojson`](data/parcels.geojson) | The four parcels as recorded boundaries, from the county's BCAD parcel service |
| [`data/terrain.json`](data/terrain.json) | 1 ft LiDAR contours, A–B transects and 1 m DEM elevation profiles per lot |
| [`data/fill.json`](data/fill.json) | Pad geometry, fill volumes and costs per lot |
| [`data/pagination.json`](data/pagination.json) | Measured page numbers, written by `tools/paginate.py` |
| [`tools/build_artifact.py`](tools/build_artifact.py) | Builds `index.html`. All figures baked in as literals. |
| [`tools/terrain.py`](tools/terrain.py) | Rebuilds `data/terrain.json` from the county and USGS elevation services |
| [`tools/terrain_svg.py`](tools/terrain_svg.py) | Renders the true-scale plans and terrain sections |
| [`tools/aerials.py`](tools/aerials.py) | Builds the twelve lot aerials from USGS NAIP |
| [`tools/fill.py`](tools/fill.py) | Costs the flood-headroom pad on each lot from a DEM grid |
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

Cost to reach build-ready (land + pad + septic + foundation): **Lot 2 ~$65k**, Lot 3 ~$109k,
Lot 1 ~$131k, Lot 4 ~$139k.

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
