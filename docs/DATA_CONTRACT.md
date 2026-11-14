# DATA CONTRACT (v0) — the one thing everybody must agree on

## 1. Dimensions  (`data/dimensions.json`)
Eight dimensions, ids fixed:
`D1_cold, D2_aridity, D3_barren, D4_terrain, D5_rock, D6_ice, D7_polar_light, D8_thermal_swing`

Each Earth cell has, for every dimension, a **percentile 0-1 among all land cells**
(1 = the most of that trait: coldest, driest, most barren, roughest, rockiest, most ice,
biggest seasonal daylight swing, biggest day/night temperature swing).
Percentiles let us compare Earth to the Moon/Mars by *rank and direction*, not raw units.

## 2. Earth grid  (`data/processed/earth_grid.csv`, sample in `data/sample/`)
One row per 0.25° land cell.

| column | type | meaning |
|---|---|---|
| cell_id | int | unique id |
| lat, lon | float | cell centre, degrees (lat -90..90, lon -180..180) |
| D1_cold ... D8_thermal_swing | float 0-1 or empty | percentile; **empty = no data** (never write 0 for missing) |
| country | str, optional | for display |

## 3. Targets  (`data/targets.json`)
List of objects:
```json
{
  "id": "MARS_JEZERO", "body": "mars", "name": "...", "description": "...", "status": "core|optional",
  "rules": {
    "D2_aridity": {"rule": "high", "weight": 3},
    "D1_cold":    {"rule": "band", "lo": 0.4, "hi": 0.7, "weight": 2}
  }
}
```
Rules: `high` (more is better), `low` (less is better), `band` (best inside lo..hi).
Weight: 0 (ignore) to 3 (critical). Dimensions not listed are ignored.

## 4. Score formula
`s` = per-dimension similarity 0-1 (high: p, low: 1-p, band: 1 inside, falls linearly to 0 over 0.5 outside)
`S = 100 * sum(w*s) / sum(w)` over dimensions that have data for that cell.
`coverage = sum(w with data) / sum(w total)` is returned too; low coverage = low trust.

## 5. API  (`backend/main.py`)
| endpoint | returns |
|---|---|
| GET /health | `{"ok": true}` |
| GET /targets | list of targets |
| GET /dimensions | dimension list |
| GET /score?target=ID&min_score=0&limit=5000 | `[{cell_id,lat,lon,score,coverage}]` best first |
| GET /site?lat=..&lon=..&target=ID | per-dimension breakdown for the nearest cell |
| GET /compare?lat=..&lon=..  | that cell's score against every target |
| POST /score_custom | body: `{"target": {...rules...}}` score with user-edited weights |
