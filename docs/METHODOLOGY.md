# ASTRANOVUS methodology

ASTRANOVUS is an independent prototype. Scores are team-generated, purpose-specific similarity estimates, **not** NASA ratings
or landing-site certifications, and an Earth site never reproduces lunar/Martian gravity, atmosphere or radiation.

## 1. Problem and solution
NASA's challenge asks for Earth places that resemble permanent Moon-base sites and Mars. Which place is "best" depends on
what is being tested (ice drilling needs cold, ice-bearing ground; rover tests need rough bare terrain). ASTRANOVUS therefore
ranks Earth regions for a **specific experiment**, not a generic similarity.

## 2. Data (all verified from the downloaded files' own metadata)
| Product | Version | Used for | Variable / conversion |
|---|---|---|---|
| MODIS Terra MOD11C3 (LP DAAC) | 061, HDF4, 0.05°, monthly | D8 | `LST_Day_CMG`, `LST_Night_CMG`: K = raw × 0.02, valid_range 7500–65535, fill 0; plausibility 150–380 K |
| MODIS Terra MOD13C2 | 061, HDF4 | D3 | `CMG 0.05 Deg Monthly NDVI`: NDVI = raw / 10000, valid −2000…10000, fill −3000; pixel reliability 0 (good) or 1 (marginal) only |
| MODIS Terra MOD10CM (NSIDC) | 061, HDF4 | D6 | `Snow_Cover_Monthly_CMG`: 0–100 % kept; 211 night, 250 cloud, 253 no decision, 254 water, 255 fill excluded |
| NASA SRTMGL30 (LP DAAC) | 002, 30 arc-second (~1 km), global (GTOPO30-filled outside 60N–56S) | D4 | raw big-endian int16 elevation, nodata −9999; relief = P95 − P5 within the cell |
| GPM IMERG Final Monthly | V07B, HDF5, 0.1° | cross-check of D2 | `Grid/precipitation` mm/hr × 24, fill −9999.9 |
| NASA POWER climatology | point API cache | D1, D2, D7 | T2M, PRECTOTCORR, ALLSKY_SFC_SW_DWN (annual) |

All **12 monthly granules of calendar year 2024** are processed for MODIS and GPM. This is a single year, not a multi-year climatology (2024 anomalies such as the El Niño-to-La Niña transition are included). If fewer months are present the builder labels results *partial seasonal*. Raw files are never modified.

## 3. Grid and normalisation
2.5° cells centred on the land cells of the NASA POWER grid (3,435 cells, lat −88.75…88.75, including Antarctica). Each MODIS 0.05° array is block-averaged over the
cell using only valid land pixels; a cell needs valid pixels over ≥30 % of its land pixels, else it stays empty. Every dimension is then converted
to a **percentile rank (0–1) among the valid cells** (1 = most of that trait). Empty = no data, never zero.

| Dimension | Definition | Status |
|---|---|---|
| D1_cold | POWER annual 2 m **air** temperature, inverted | derived, annual |
| D2_aridity | POWER annual precipitation, inverted | derived, annual |
| D3_barren | peak monthly MODIS NDVI over the 12 months, inverted | derived, 2024. Low NDVI also over ice; ice-sheet pixels are flagged "snow/ice" by MODIS and left empty |
| D4_terrain | percentile of 1-km elevation relief (P95−P5) inside the cell, from SRTMGL30 | derived, static. Landscape-scale relief only, not rover-scale slope. Cross-check vs the 30 m SRTM tiles of the top regions: Spearman ≈ 0.6 (n=10). **Finer 30 m check below.** NASA SRTMGL1 tiles were downloaded for the top candidate regions (`scripts/stage2_srtm.py` → `data/processed/stage2.json`): slope/relief/roughness are shown per region as a local check (1° tile) and are not part of the score; regions outside 60°N–56°S are marked unverified |
| D5_rock | — | **missing** (a categorical lithology will not be turned into a percentile without a documented method) |
| D6_ice | peak monthly MODIS snow cover | **proxy**: snow-cover extent, not permafrost or subsurface ice; 2024 annual peak |
| D7_polar_light | POWER seasonal swing of surface insolation | derived proxy; terrestrial seasonality does not reproduce lunar illumination |
| D8_thermal_swing | mean over months of MODIS LST day − night, requiring ≥ 9 of 12 valid months (polar-night cells without enough valid months stay empty) | derived, 2024 |

**Cross-checks** (`earth_grid_metadata.json`): POWER air temperature vs MODIS LST (Spearman 0.97), POWER precipitation vs GPM (0.83). The earlier
POWER-based D8 correlated **negatively** (−0.32) with MODIS diurnal range (it measured an annual air-temperature range), so D8 now uses MODIS surface temperatures.

## 4. Scoring (model/scoring_core.py)
Per dimension similarity `s`: *high* → p, *low* → 1−p, *band* → 1 inside [lo,hi] falling linearly to 0 over 0.5 outside.
`S = 100 · Σ(w·s) / Σ(w with data)`; `coverage = Σ(w with data) / Σ(w)`.

## 5. Mission-specific recommendation (model/recommend.py + data/experiments.json)
1. An **experiment** maps onto an existing mission profile (data/purposes.json). Reference sites offered are exactly that profile's targets for the chosen body.
2. The profile's **multipliers** scale each rule's weight; **gates** are hard requirements (failing cells are dropped; missing gate data is flagged "unverified", never silently passed).
3. Passing cells are ranked by score and grouped into **peak-seeded regions**: the best unassigned cell becomes a region's seed and claims all unassigned cells within 15° (great-circle), so a continent-sized plateau cannot collapse into one blob. The API considers the best 60 % of passing cells (engine default 15 %) so one huge high-scoring area such as the Antarctic plateau does not crowd out every other candidate. Confidence: high if coverage ≥ 85 % and ≥ 3 cells; medium if coverage ≥ 60 %; else low. Cell counts near the poles are inflated because 2.5° cells converge there.
4. UI data-state rule (backend/mission_api.py): *unavailable* if a gate dimension has no data at all, or under 50 % of the weighted criteria have data; *partial* if any dimension is missing or a proxy; otherwise *ready*. A clearly labelled provisional ranking can be requested for unavailable cases.
5. One draft variation exists: "Regolith & dust" adds ×1.5 on aridity and a dryness gate (≥0.4, copied from POWER_THERMAL). It is flagged as an ASTRANOVUS assumption.

## 6. Limits
2.5° grid (~280 km cells); a single year (2024) of MODIS/GPM; 1-km terrain and no rock data; target rules are drafts (see TARGET_EVIDENCE.md); percentile ranking compares Earth cells to each
other, not physical Moon/Mars values; region names are approximate bounding-box labels.

## 7. Attribution
NASA LP DAAC (MOD11C3, MOD13C2), NASA NSIDC DAAC (MOD10CM), NASA GES DISC (GPM IMERG), NASA POWER, NASA/JPL, LRO Diviner (UCLA), NASA SWIM (PSI). Product DOIs are in `earth_grid_metadata.json`.
