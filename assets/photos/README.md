# Lot imagery

The twelve JPEGs here are generated, not hand-collected. Rebuild them with:

```
python3 tools/aerials.py
```

Three per lot, which the artifact places on each lot page:

| File | What it shows |
|---|---|
| `lotN-1.jpg` | the parcel at close range, with its recorded boundary and the A–B section line |
| `lotN-2.jpg` | the water frontage, centred on point B |
| `lotN-3.jpg` | neighbourhood context, with the parcel outlined |

## Source and licensing

Imagery is **USGS NAIP** aerial photography at 30 cm, pulled from the USGS NAIPPlus ImageServer.
NAIP is US Department of Agriculture photography **in the public domain**, so it can be reproduced
in the artifact and committed here.

Photographs on Zillow, Redfin, Realtor.com and Homes.com are **not** reproduced. They are licensed
to those platforms and to the listing brokerage, and those sites block direct linking, so embedding
them would be both a licensing problem and a broken image. Each lot page links to the listing
galleries and to Google Street View instead, for ground-level views.

If you want a specific listing photograph inline, download it yourself and overwrite the relevant
file above — the artifact will pick it up on reload. Note that `tools/aerials.py` would overwrite it
again on the next run.

## Overlay accuracy

The yellow boundary is the appraisal district's mapping polygon reprojected onto the imagery. It is
for orientation only. Appraisal-district polygons are maintained for mapping rather than for
conveyancing, and on three of the four lots the polygon area differs from the acreage of record by
3–13%. Only a boundary survey establishes where the line actually is.
