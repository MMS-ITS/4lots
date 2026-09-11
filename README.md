# Bar X Ranch — 4-Lot Feasibility Portfolio

Independent feasibility review of four vacant lots in Bar X Ranch, unincorporated Brazoria County,
Angleton, Texas 77515 — assessed for a five-bedroom build, and for what it is actually like to live
there.

**Current edition: v3.0, 11 September 2026, prepared for Mohsin Chowdhury.** 34 pages, paginated.

## Contents

| File | What it is |
|------|-----------|
| [`index.html`](index.html) | **The artifact (v3.0)** — 34 numbered A4 pages. Open in a browser; print to PDF at 100% for true-scale drawings. |
| [`data/parcels.geojson`](data/parcels.geojson) | The four parcels as recorded boundaries, from the county's BCAD parcel service |
| [`data/terrain.json`](data/terrain.json) | 1 ft LiDAR contours, A–B transects and 1 m DEM elevation profiles per lot |
| [`data/pagination.json`](data/pagination.json) | Measured page numbers, written by `tools/paginate.py` |
| [`tools/build_artifact.py`](tools/build_artifact.py) | Builds `index.html`. All figures baked in as literals. |
| [`tools/terrain.py`](tools/terrain.py) | Rebuilds `data/terrain.json` from the county and USGS elevation services |
| [`tools/terrain_svg.py`](tools/terrain_svg.py) | Renders the true-scale plans and terrain sections |
| [`tools/paginate.py`](tools/paginate.py) | Two-pass pagination — measures the real print, then fixes every page number and verifies it |
| [`docs/EVIDENCE.md`](docs/EVIDENCE.md) | Every v3 finding with the exact query that produced it |
| [`docs/AUDIT.md`](docs/AUDIT.md) | Claim-by-claim audit of the original generated portfolio |
| [`docs/SOURCES.md`](docs/SOURCES.md) | Source register, and an explicit list of what could not be verified |
| `assets/photos/` | Drop listing photographs here as `lot1-1.jpg` … `lot4-3.jpg` and the artifact picks them up |

## The four lots

| Lot | PID | Acres of record | Asking | County appraised | Soil |
|---|---|---|---|---|---|
| 1127 Saddle Horn Bend | 183667 | 1.95 | $82,500 | $65,030 | Asa silty clay loam |
| 336 Wagon Wheel Trail W | 183367 | 1.00 | $45,000 | $36,000 | Asa silty clay loam |
| Lot 29 Broken Arrow Trail | 186219 | 1.30 | $49,000 | $51,870 | Pledger clay |
| 750 Wagon Wheel Trail | 183332 | 1.00 | $58,000 | $50,000 | Pledger clay |

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
- Added true-scale plans and terrain sections per lot, and a livability chapter covering climate in
  Celsius, hazards, services, schools, distances, demographics, the Indian community and airports.

## Rebuilding

```
python3 tools/build_artifact.py   # writes index.html
python3 tools/paginate.py         # measures the print and corrects every page number
python3 tools/terrain.py          # only needed to refresh the elevation data
```

`paginate.py` needs headless Chrome and `pypdf`. No API keys are required anywhere.

## Status

**Desktop screening study.** No lot has been visited, surveyed or soil-tested, and no BFE has been
confirmed in writing. Elevations come from remote-sensing models, not from an instrument survey. See
the due-diligence sequence in §31 of the artifact and the disclaimer on its final page before relying
on any figure.
