# Evidence register — v3.0

Everything established for the first time in v3.0, with the exact query that produced it, so a
reviewer can re-run it and disagree. Retrieved **11 September 2026**.

Source content is paraphrased and summarised rather than quoted at length, except for short
quotations from the recorded deed restrictions, where the exact wording is the finding.

---

## 1. The parcel record

Brazoria County publishes its GIS as an open ArcGIS service. Note that `brazoriacountytx.gov`
returns an Akamai `403` to automated requests, but `arcgis-web.brazoriacountytx.gov` does not.

```
POST https://arcgis-web.brazoriacountytx.gov/arcgis/rest/services/general/Parcels/MapServer/1/query
  where=situs_street LIKE '%SADDLE HORN%' AND situs_num='1127'
  outFields=PID,geo_id,SITUS,LEGALTYPE,legal_desc,legal_acreage,Land_Acreage,tract_or_lot,
            appraised_val,abs_subdv_desc,DOCUMENT,CITYCODE_NAME
  returnGeometry=true&outSR=4326&f=json
```

Queries must be sent by **POST**; a polygon geometry in a GET query string exceeds the IIS URL
limit and returns a bare `404`.

| Lot | Query used | PID | geo ID | Acres of record | Appraised | Deed |
|---|---|---|---|---|---|---|
| 1127 Saddle Horn Bend | `situs_street LIKE '%SADDLE HORN%' AND situs_num='1127'` | 183667 | 1534-0084-000 | 1.95 | $65,030 | 2008-031507 |
| 336 Wagon Wheel Trl W | `situs_street LIKE '%WAGON WHEEL%' AND situs_num='336'` | 183367 | 1533-0167-000 | 1.00 | $36,000 | V1523P212 |
| Lot 29 Broken Arrow Trl | `legal_desc LIKE 'BAR X RANCH SEC 16%' AND tract_or_lot LIKE '29%'` | 186219 | 1549-0029-000 | **1.30** | $51,870 | V268P248 |
| 750 Wagon Wheel Trl | `situs_street LIKE '%WAGON WHEEL%' AND situs_num='750'` | 183332 | 1533-0132-000 | **1.00** | $50,000 | V1729P804 |

Lot 29 could not be found by street name: no street number is assigned to it and its situs of
record is `HIGHWAY 35`. It was located by section and lot number instead. **Confirm the listing
refers to PID 186219** before relying on any of it.

Owner-of-record names are returned by the same query and are deliberately not reproduced in the
artifact or here.

Geometry for all four is committed as [`data/parcels.geojson`](../data/parcels.geojson).

## 2. Flood — panel, zone and published BFE

Service: `general/Floodplain/MapServer`, layers `9` (Floodplain 2020), `11` (FEMA BFE 2020),
`12` (FEMA FirmPanels 2020). Parcel polygon posted as the query geometry.

- **FIRM panel `48039C0420K`**, effective **30 December 2020**, for all four parcels. Both earlier
  editions cited `48039C0605K`; that is wrong.
- **Zone AE, `SFHA_TF = T`**, on all four, with **`STATIC_BFE = -9999`** — i.e. no static BFE is
  published for the polygon, so the BFE varies across it and must be read from the profile. This is
  precisely why a single assumed BFE was never safe.
- **Nearest published BFE line reads 28.0 ft NAVD88 at every one of the four lots** (1,010 ft away
  at Lot 2; 1,492 ft at Lot 4; 1,594 ft at Lot 1; 2,477 ft at Lot 3), with a 29.0 ft line further
  upstream. Not the 24 ft assumed by v1 and v2.

A published BFE line 1,000–2,500 ft away is strong evidence, **not** a determination. Only the
county floodplain administrator can issue one.

## 3. Natural ground elevation

Two independent datasets, which agree to about a foot:

- **County LiDAR**, `general/LiDAR/MapServer/0`, field `CONTOUR`, **1-foot interval**, queried by
  parcel envelope plus a 45 m halo.
- **USGS 3DEP 1 m DEM**, `getSamples` along the A–B transect, ~1 m spacing, metres converted at
  1 ft = 0.3048 m.

```
POST https://elevation.nationalmap.gov/arcgis/rest/services/3DEPElevation/ImageServer/getSamples
  geometry={"paths":[[[lon1,lat1],[lon2,lat2]]],"spatialReference":{"wkid":4326}}
  geometryType=esriGeometryPolyline&sampleCount=180
  returnFirstValueOnly=true&interpolation=RSP_BilinearInterpolation&f=json
```

| Lot | Contours crossing the parcel | Plateau (3DEP) | Transect min–max | Steepest bank |
|---|---|---|---|---|
| 1 | 24, 25, 26 ft | 24–26 ft | 21.25–26.03 ft | −8.36° (14.7%) over 7.7 m |
| 2 | 25, 26, 27, 28 ft | 27–29 ft | 21.16–29.12 ft | −8.80° (15.5%) over 7.2 m |
| 3 | 23, 24, 25, 26 ft | 26–27 ft | 21.20–26.91 ft | −11.57° (20.5%) over 6.1 m |
| 4 | 23–30 ft (all eight) | 23–24 ft | 23.14–30.70 ft | **+8.47%** rising to the levee crest |

The "28–30 ft natural ground" repeated by both earlier editions is not supported. Ground at the
parcels is **24–28 ft**, so the 30 ft finished-floor target sits **2–6 ft above existing grade**.

Lot 4's profile rises toward the water because the transect climbs the **Flag Lake Levee**. The
101-acre pond is impounded above the buildable part of that lot.

## 4. Waterfront status

Measured as the distance from every recorded parcel-boundary vertex to the nearest mapped water
body (OpenStreetMap `natural=water`, `waterway=*`), counting how many vertices fall within 60 ft.

| Lot | Water body | Vertices within 60 ft | Verdict |
|---|---|---|---|
| 1 | Mill Bayou + a 13.0 ac impounded widening | 19 of 40 | Waterfront, ~half the perimeter |
| 2 | unnamed 12.6 ac pond | 4 of 12 | Waterfront, short frontage |
| 3 | the **same** 12.6 ac pond | 7 of 13 | **Waterfront** — both earlier editions said interior |
| 4 | **Flag Pond, 101.5 ac** + Flag Lake Levee | 8 of 17, at 11 ft | Waterfront on the main lake |

All four are waterfront. OSM water geometry is not authoritative for a boundary; the plat is.

## 4b. Corroborating the waterfront finding against USGS hydrography

The OSM measurement in §4 was re-tested against the **USGS National Hydrography Dataset**
(`hydro.nationalmap.gov/arcgis/rest/services/nhd/MapServer`, layers 12 Waterbody, 9 Area,
6 Flowline), measured from every recorded parcel-boundary vertex.

| Lot | Nearest NHD **waterbody** | Nearest NHD **flowline** | Reading |
|---|---|---|---|
| 1 | **395 ft** | 66 ft (Mill Bayou, 107 ft named) | **A tree-lined stream corridor, not a pond.** NAIP imagery confirms a wooded channel. |
| 2 | **41 ft** | 72 ft | Genuine pond adjacency |
| 3 | **59 ft** | 89 ft | Genuine pond adjacency |
| 4 | **14 ft — named Flag Pond** | 167 ft (canal/ditch) | Confirmed on the main lake |

This refines rather than overturns §4: all four are water-adjacent, but **Lot 1's frontage is bayou
corridor rather than open water**, and on Lot 4 the *visible* shoreline in the imagery sits further
out than the mapped pool boundary — the mapped extent includes the levee-enclosed pool.

## 4c. Aerial imagery

`tools/aerials.py` builds three images per lot from the **USGS NAIPPlus ImageServer**
(`imagery.nationalmap.gov`, 30 cm, 4-band, public domain) via `exportImage`, and draws on the
recorded boundary and the A–B section line:

```
GET https://imagery.nationalmap.gov/arcgis/rest/services/USGSNAIPPlus/ImageServer/exportImage
    ?bbox=<xmin,ymin,xmax,ymax>&bboxSR=3857&imageSR=3857&size=1600,1200
    &format=jpg&interpolation=RSP_BilinearInterpolation&f=image
```

NAIP is US Department of Agriculture aerial photography and is in the public domain, so it can be
reproduced in this document. Listing photographs on Zillow, Redfin and Realtor.com cannot — they are
licensed to those platforms and to the listing brokerage, and are linked instead.

## 5. Dams

- **Flag Lake Levee**, National Inventory of Dams **TX06298**, 11 ft from the Lot 4 boundary.
  Published NID data carries **no hazard-potential classification and no condition assessment**.
- **Bar X Development Dam**, NID **TX01759**, on a Mill Bayou tributary upstream of Lot 1. NID rates
  it low hazard potential, moderate risk.

Confirm both with TCEQ Dam Safety.

## 6. Soil

USDA NRCS **SSURGO** via Soil Data Access, major component of the map unit at each parcel centroid.

```
POST https://sdmdataaccess.sc.egov.usda.gov/Tabular/post.rest
{"format":"JSON+COLUMNNAME","query":
 "SELECT c.compname,c.drainagecl,c.runoff,c.hydgrp,mu.farmlndcl,ch.hzname,ch.hzdept_r,ch.hzdepb_r,
         ch.sandtotal_r,ch.silttotal_r,ch.claytotal_r,ch.om_r,ch.ksat_r,ch.awc_r,ch.lep_r,ch.ph1to1h2o_r
  FROM mapunit mu JOIN component c ON c.mukey=mu.mukey JOIN chorizon ch ON ch.cokey=c.cokey
  WHERE mu.mukey IN (SELECT * FROM SDA_Get_Mukey_from_intersection_with_WktWgs84('point(LON LAT)'))
    AND c.majcompflag='Yes' ORDER BY ch.hzdept_r"}
```

| | Lots 1 & 2 — **Asa silty clay loam** | Lots 3 & 4 — **Pledger clay** |
|---|---|---|
| Taxonomy | Fluventic Hapludoll (mollisol) | Typic Hapludert (**vertisol**) |
| Clay / silt / sand, topsoil | 36.5 / 49.0 / 14.5 % | **69.5** / 28.9 / 1.6 % |
| Organic matter | 3.07 % | 6.5 % |
| pH (1:1 H₂O) | 6.8 | 7.0 |
| Drainage class | **Well drained** | Moderately well drained |
| Surface runoff | **Negligible** | **High** |
| Hydrologic group | **B** | **D** |
| Saturated conductivity `ksat_r` | **9.0 µm/s** | **0.21 µm/s** |
| Linear extensibility `lep_r` | **4.5** | **19** |
| Available water capacity | 0.18–0.20 | 0.14 |
| Farmland class | All areas prime farmland | All areas prime farmland |

Consequences drawn in §16 and §18 of the artifact: a 43× permeability difference drives the TCEQ
soil class and therefore the septic system type; a linear extensibility of 19 is a high-movement
vertisol and drives the foundation design.

SSURGO is mapped at about 1:24,000 and reports the *predominant* soil of a map unit (85% component
share here). It is not a site-specific soil evaluation and does not set the TCEQ class on the permit.

## 7. Jurisdiction, taxing districts and school district

Service: `general/Taxing_Entities/MapServer`, layers 0, 1, 4, 5, 6, 8, 9, 11; and
`general/Legal_and_Development/MapServer/3` for the recorded subdivision.

- **School district: Columbia-Brazoria ISD** for all four parcels — not Angleton ISD.
- **No hospital district** reaches any of the four. The county contains only the Angleton-Danbury and
  Sweeny hospital districts and the parcels fall in neither. The v2 tax model wrongly included
  Angleton-Danbury at 0.074685 per $100.
- **No junior-college district** (the county has Alvin and Brazosport; neither reaches these lots).
- **Drainage: county-wide only** (`NAME='Brazoria County', DISTRICT=0`), not the Angleton Drainage
  District, so v2's 0.052816 per $100 also comes out.
- **No MUD, no city limits** on any of the four.
- **Lot 2 alone sits inside the Baileys Prairie ETJ.** The other three answer only to the county.
- Emergency services: ESD1 and ESD2 returned for Lots 1, 3 and 4; **no ESD polygon was returned for
  Lot 2**, which is more likely a gap in the layer than a gap in coverage — confirm.

Recorded subdivision instruments, from the Subdivisions layer:

| Lot | Subdivision | Plat | Restrictions |
|---|---|---|---|
| 2, 4 | Bar-X Ranch #1 | 16/104, 9 Jun 1980 | 1515/679, plus drainage easements 1712/500 |
| 1 | Bar-X Ranch #2 | 16/119, 17 Sep 1980 | 1532/471 |
| 3 | Bar-X Ranch #16 | 17/219, 23 Jul 1984 | 84-29/885 |

**Three different recorded instruments**, so the single "ACC Rev 2" cited by earlier editions as
governing all four lots cannot be correct.

## 8. Deed restrictions

Read from the recorded Bar X Ranch declaration of restrictions published by the POA
(`barxranch.org`), Deed Vol. **1679**, Pg. **695**, executed 1982.

- **§3.01** — only *one single-family dwelling, one garage and one horse barn* (max 30 × 25 ft) may
  stand on a lot; anything else needs prior written committee approval.
- **§3.15** — *"No livestock of any kind other than house pets of reasonable kind and number may be
  kept on any Lot."* Horses are the sole express exception: 1 per 32,670 sq ft, 2 per 42,000 sq ft,
  one more per additional 21,880 sq ft.
- **§3.03** — minimum dwelling **1,100 sq ft** of living area (1,400 sq ft above two storeys). The
  "1,800 sq ft minimum" repeated by earlier editions is **not** in this instrument.
- **§3.06** — no building on a lot under 21,880 sq ft; no resubdivision without approval.
- **§3.05** — the front of a lot is the boundary with the *shortest* dimension abutting a street.
- **§3.12** — a lot with a horse barn must be fenced; all fences need written approval.
- **§3.04** — roofing limited to wood shingle, built-up tar and gravel, or asphalt shingle ≥340 lb
  per square.
- **§3.07** — no noxious or offensive activity; exterior display or discharge of firearms forbidden.
- **§3.13** — owners must keep grass cut and fences painted, or the association does it and bills
  them. This is the origin of the $125 vacant-lot mowing charge.
- **§3.14 / §3.16** — no septic discharge to road ditches; drainage of streets, lots or ditches may
  not be impaired. Directly relevant to placing a 2–6 ft pad.
- **§4.05** — committee powers passed to the POA 15 years after the instrument.

> **This instrument is not one of the three that govern these lots.** It is a Bar X Ranch declaration
> of the same era and form. The provisions above are very likely substantially what applies, but the
> operative instrument for the specific lot (1515/679, 1532/471 or 84-29/885) must be pulled from the
> County Clerk, and the poultry question put to the POA in writing.

## 9. Windstorm zone

Texas Department of Insurance, Brazoria County designated-catastrophe-area page: community list and
the written description of the dividing line.

- **Inland II — 110 mph** 3-second gust: includes Bailey's Prairie, West Columbia, Holiday Lakes.
- **Inland I — 120 mph**: includes Angleton, Brazoria, Lake Jackson.
- **Seaward — 130 mph**: Quintana, Surfside Beach.
- The Inland I / Inland II dividing line runs **northeasterly along State Highway 35**, then north
  along FM 521, then northeasterly along FM 523.

Measured against the county street centrelines, **all four lots lie south (seaward) of SH 35** — at
0.09 mi (Lot 1), 0.10 mi (Lot 3), 0.37 mi (Lot 2) and 1.03 mi (Lot 4) — which places all four in
**Inland I, 120 mph**. Lots 1 and 3 are within 530 ft of the line, so confirm against TDI's own map.

The same measurement is the basis for the highway-noise comparison in the artifact.

## 10. Hazards

FEMA **National Risk Index**, December 2025 edition, Brazoria County (FIPS 48039), read from the
NRI counties feature service. The direct CSV download on `hazards.fema.gov` is Akamai-blocked.

Composite **Relatively Moderate** (score 93.64); expected annual loss $161.5 m; social vulnerability
Relatively Low; community resilience **Very High**.

Relatively High: riverine flooding (1.86/yr, $78.2 m), hurricane (0.22/yr, $43.6 m), tornado
(1.11/yr, $20.9 m), lightning (70/yr), ice storm.
Relatively Moderate: coastal flooding, strong wind, heat wave, cold wave, drought.
Relatively Low: hail, **wildfire (0.004/yr)**.
Very Low: earthquake, landslide, winter weather.

## 11. Climate

ERA5 reanalysis, daily 1991–2020, at 29.1392 N 95.4655 W, aggregated in metric.

Annual mean 21.7 °C · annual rainfall 1,177 mm · wettest year 2,024 mm, driest 488 mm ·
51 days/yr ≥32.2 °C, 8 ≥35 °C, 0.5 ≥38 °C · 30-year extremes −6.0 °C and 41.0 °C ·
air frost in 18 of 30 years, mean 1.9 frost days · mean last spring frost 2 Feb, first autumn frost
19 Dec, **frost-free season ~320 days**.

Monthly normals are tabulated in §22 of the artifact.

## 12. Demographics

US Census Bureau **ACS 2024 five-year estimates** (2020–2024) for **census tract 6625**, which
contains all four lots, retrieved via the Census Reporter API (`api.census.gov` requires a key).

Tract: population 3,452 · median age 42.3 · median household income **$116,550** · median owner-
occupied value $384,100 · **96.9% owner-occupied** · White alone 76.4%, Black 6.2%, **Asian alone
0.2% (7 people)**, two or more races 16.7%, Hispanic 29.6% · **no Asian Indian population reported**.

Brazoria County: population 391,255 · median household income $97,993 · **Asian Indian alone or in
combination 6,414 (1.6%)**.

## 13. Distances

Road distances and drive times from OSRM (`router.project-osrm.org`), origin the portfolio centroid
29.13918 N 95.54651 W. Destinations located by OpenStreetMap Overpass ("nearest X of type Y")
rather than by guessing street addresses, or by the county's own schools and airports layers.

Selected results, all in §24–27: nearest supermarket **H-E-B West Columbia 6.7 mi / 13 min** (closer
than Angleton) · nearest hospital + ER **UTMB Angleton-Danbury 11.3 mi / 20 min** · nearest Gulf
beach **Surfside 28.3 mi / 42 min** (not the 20 min claimed originally) · nearest Indian restaurant
35.5 mi / 48 min · **Sri Meenakshi Temple, Pearland 39.5 mi / 58 min** · nearest South Asian grocery
42.9 mi / 62 min · **nearest international airport Houston Hobby 49.5 mi / 71 min**; IAH 70.4 mi /
95 min.

## 14. Fill and the pad (§20)

Computed by `tools/fill.py`. Design basis: finished floor **30.0 ft** (28 ft BFE + 24 in county
freeboard), pad top **29.5 ft** for a 6-inch slab, topsoil stripped **0.5 ft**, pad **69 × 82 ft**
for a ~3,040 sq ft house and garage plus a 10 ft working margin, **3:1** side slopes.

Ground is sampled from the USGS 3DEP 1 m DEM on a 5 m grid inside each recorded boundary
(`getSamples`, multipoint, bilinear). The pad is placed to minimise fill subject to its slope toe
fitting inside the boundary and staying **30 m clear of mapped water** — without that constraint the
optimiser puts the Lot 4 pad on the crest of the Flag Lake levee, which is not a foundation.

Volume is the exact prismatoid for planar side slopes:

```
V = W·L·h + s·h²·(W + L) + (4/3)·s²·h³
```

Plan area × depth understates a deep pad materially: the slope wedge grows with h² and the corners
with h³. Rates: fill **$16–$30** per compacted cubic yard placed (haul is most of the spread),
stripping $1.60–$3.20/sy, slope finishing $1.10–$2.40/sy, geotechnical $2,500–$5,000, pad and
drainage design $1,500–$4,000, density testing $1,200–$3,000, erosion control $600–$1,500, drainage
works $1,000–$4,000, permit $0–$80. These are planning figures, not quotations.

A pier-and-beam or stem-wall alternative at $26–$44/sq ft of floor area (~$106,000 mid-case here)
only becomes competitive at about **9.3 ft** of lift, so a fill pad is correct on all four lots.

### Lot 1 — 1127 Saddle Horn Bend

Ground at the chosen pad **25.26 ft** · pad top 29.5 ft · lift **4.24 ft** · fill from stripped surface 4.74 ft · **1,416 cu yd** · toe 97 × 110 ft (lot narrow dimension 316 ft, needs 113 ft, +203 ft spare)

| Item | Low | High |
|---|---:|---:|
| Strip and stockpile topsoil under the pad | $1,912 | $3,825 |
| Imported select fill, placed and compacted in lifts | $22,661 | $42,490 |
| Topsoil and turf the side slopes | $623 | $1,360 |
| Geotechnical investigation and report | $2,500 | $5,000 |
| Engineered pad and drainage plan | $1,500 | $4,000 |
| Compaction density testing | $1,200 | $3,000 |
| Erosion and sediment control | $600 | $1,500 |
| Drainage works so runoff is not pushed onto the road or a neighbour | $1,000 | $4,000 |
| County fill and grading permit | $0 | $80 |
| **Total** | **$31,997** | **$65,255** |

### Lot 2 — 336 Wagon Wheel Trail W

Ground at the chosen pad **28.83 ft** · pad top 29.5 ft · lift **0.67 ft** · fill from stripped surface 1.17 ft · **268 cu yd** · toe 76 × 89 ft (lot narrow dimension 187 ft, needs 92 ft, +95 ft spare)

| Item | Low | High |
|---|---:|---:|
| Strip and stockpile topsoil under the pad | $1,202 | $2,405 |
| Imported select fill, placed and compacted in lifts | $4,283 | $8,031 |
| Topsoil and turf the side slopes | $135 | $295 |
| Geotechnical investigation and report | $2,500 | $5,000 |
| Engineered pad and drainage plan | $1,500 | $4,000 |
| Compaction density testing | $1,200 | $3,000 |
| Erosion and sediment control | $600 | $1,500 |
| Drainage works so runoff is not pushed onto the road or a neighbour | $1,000 | $4,000 |
| County fill and grading permit | $0 | $80 |
| **Total** | **$12,421** | **$28,311** |

### Lot 3 — Lot 29 Broken Arrow Trail

Ground at the chosen pad **26.49 ft** · pad top 29.5 ft · lift **3.01 ft** · fill from stripped surface 3.51 ft · **963 cu yd** · toe 90 × 103 ft (lot narrow dimension 354 ft, needs 106 ft, +248 ft spare)

| Item | Low | High |
|---|---:|---:|
| Strip and stockpile topsoil under the pad | $1,651 | $3,302 |
| Imported select fill, placed and compacted in lifts | $15,403 | $28,880 |
| Topsoil and turf the side slopes | $443 | $967 |
| Geotechnical investigation and report | $2,500 | $5,000 |
| Engineered pad and drainage plan | $1,500 | $4,000 |
| Compaction density testing | $1,200 | $3,000 |
| Erosion and sediment control | $600 | $1,500 |
| Drainage works so runoff is not pushed onto the road or a neighbour | $1,000 | $4,000 |
| County fill and grading permit | $0 | $80 |
| **Total** | **$24,297** | **$50,729** |

### Lot 4 — 750 Wagon Wheel Trail

Ground at the chosen pad **25.68 ft** · pad top 29.5 ft · lift **3.82 ft** · fill from stripped surface 4.32 ft · **1,255 cu yd** · toe 95 × 108 ft (lot narrow dimension 123 ft, needs 111 ft, +12 ft spare)

| Item | Low | High |
|---|---:|---:|
| Strip and stockpile topsoil under the pad | $1,822 | $3,643 |
| Imported select fill, placed and compacted in lifts | $20,082 | $37,654 |
| Topsoil and turf the side slopes | $561 | $1,224 |
| Geotechnical investigation and report | $2,500 | $5,000 |
| Engineered pad and drainage plan | $1,500 | $4,000 |
| Compaction density testing | $1,200 | $3,000 |
| Erosion and sediment control | $600 | $1,500 |
| Drainage works so runoff is not pushed onto the road or a neighbour | $1,000 | $4,000 |
| County fill and grading permit | $0 | $80 |
| **Total** | **$29,264** | **$60,101** |

**Taken fully clear of the levee embankment (60 m standoff):** ground 24.33 ft, lift 5.17 ft, 1,808 cu yd, **$38,630 – $77,762**, and the pad then needs 119 ft of width on a 123 ft lot.


---

## Reproducing all of it

```
python3 tools/terrain.py         # rebuilds data/terrain.json from the county and USGS services
python3 tools/fill.py            # rebuilds data/fill.json — the pad and fill costing
python3 tools/aerials.py         # rebuilds the twelve lot aerials from USGS NAIP
python3 tools/build_artifact.py  # rebuilds index.html
python3 tools/paginate.py        # measures the print, fixes page numbers, verifies them
```

`tools/terrain.py` needs network access to `arcgis-web.brazoriacountytx.gov`,
`elevation.nationalmap.gov` and an Overpass mirror. `tools/paginate.py` needs headless Chrome and
`pypdf`. Neither needs an API key.


---

## 13. The fifth lot — 808 Wagon Wheel Trail (added v4.0)

Retrieved **13 September 2026**, by the same queries and services as the original four.

### Parcel record

```
POST https://arcgis-web.brazoriacountytx.gov/arcgis/rest/services/general/Parcels/MapServer/1/query
  where=situs_street LIKE '%WAGON WHEEL%' AND situs_num='808'
```

| Field | Value |
|---|---|
| PID | **183331** |
| geo ID | 1533-0131-000 |
| Situs of record | 808 WAGON WHEEL TRAIL |
| Legal description | BAR X RANCH (A0038 J B BAILEY) **LOT 131** ACRES 1.07 |
| Acreage of record | **1.07** |
| County GIS polygon | **0.964** ac — 11% below the acreage of record |
| Bounding box | **490 × 110 ft** — the narrowest of the five |
| BCAD appraised | **$53,280** |
| Deed | 2007-000505 |
| CITYCODE_NAME | *null* — unincorporated, no city or ETJ |

**It is Lot 4's immediate neighbour.** 750 Wagon Wheel is Lot 132, PID 183332; this is Lot 131,
PID 183331. Their centroids are about **85 ft apart** on the same Flag Pond shoreline, which is why
the terrain, soil and hazard readings are nearly identical.

### Flood

Same services and layers as §2. Zone polygon, panel and BFE line all queried with the parcel polygon.

- **Zone AE**, `SFHA_TF = T`, `STATIC_BFE = -9999` — no static BFE published, as on the other four.
- **FIRM panel 48039C0420K**, `EFF_DATE` 1609286400000 ms = **30 December 2020**.
- **Nearest published BFE line 28.0 ft NAVD88, 1,336 ft** from the boundary — between Lot 2 (1,010 ft)
  and Lot 4 (1,492 ft).

### Water

| Dataset | Nearest | Reading |
|---|---|---|
| NHD Waterbody | **18.8 ft — named Flag Pond, 101.8 ac** | Confirmed on the main lake |
| NHD Flowline | 94.1 ft, unnamed | — |
| OSM | Flag Pond and **Flag Lake Levee** both at 21 ft | Levee adjacency confirmed |

**6 of the 11 recorded boundary vertices** fall within 60 ft of the mapped pool.

### Terrain and pad

`tools/terrain.py` and `tools/fill.py`, unchanged, re-run across all five parcels.

- Transect **477.5 ft**, road to water. Relief **6.76 ft**, from **23.33 ft to 30.08 ft**.
- Contours crossing the parcel: 23, 24, 25, 26, 27, 28, 29 ft.
- Steepest run **4.46 ft in 8.1 m — 9.57°, 16.9%**, the steepest measured anywhere in this study, and
  it is the levee embankment rather than buildable ground.
- DEM grid ground **23.55–30.09 ft**, mean **24.6 ft**. Best pad ground clear of the levee **24.81 ft**.
- Lift to a 29.5 ft pad top: **4.69 ft** — the deepest of the five. Fill **1,603 cu yd**,
  **$35,148 – $71,198**.
- **Pad geometry fails: needs 116 ft of width on a 110 ft lot, short by 6 ft.** The only lot of the
  five where the pad does not fit.

### Soil

USDA SSURGO via Soil Data Access, same query as §6, at the parcel centroid.

**Pledger** — moderately well drained, runoff **High**, hydrologic group **D**, all areas prime
farmland. Topsoil 0–44 in: **69.5% clay**, 28.9% silt, 1.6% sand, 6.5% organic matter, ksat
0.21 µm/s, pH 7.0. Subsoil 44–133 in: **73.1% clay**. Identical to Lots 3 and 4.

### Jurisdiction and taxing districts

`general/Taxing_Entities/MapServer`, point query at the centroid: **Brazoria County**,
**Emergency Services District 1 and 2**, **Columbia-Brazoria ISD**. No city, no ETJ, no hospital
district, no drainage district, no MUD — the same position as Lots 1, 3 and 4, and unlike Lot 2,
which sits inside the Baileys Prairie ETJ.

### Asking price — outstanding

The parcel is **actively listed** (Zillow zpid 305175997), confirmed by the client. The asking price
**could not be retrieved**: Zillow, Redfin, Homes.com and HAR all return bot-protection responses to
automated requests, including through a real headless browser. Every price-dependent figure for this
lot is therefore marked *pending* in the artifact rather than estimated. The county appraisal of
$53,280 is the only value anchor held for it.
