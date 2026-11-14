# NASA data sources (challenge-suggested datasets come FIRST)

Source: challenge "Suggested datasets" list as mirrored on spacedata.swapniltamse.com (an unofficial aggregator;
the official spaceappschallenge.org page could not be opened by our tooling). **Team: re-check the Resources tab of the official challenge page and fix this file if different.**

| # | Dataset (challenge-suggested) | Provider | Used for | Access | Login? |
|---|---|---|---|---|---|
| 1 | EMIT L2B Surface Mineral ID (`EMITL2BMIN`, CMR `C2408034484-LPCLOUD`) | LP DAAC | Earth: D5_rock, D3_barren (arid regions only -> partial coverage, fine: empty = no data) | `earthaccess` / CMR | Download: free Earthdata Login |
| 2 | SRTM Global 1 arc-sec (`SRTMGL1` V003, `C2763266360-LPCLOUD`) | LP DAAC | Earth: D4_terrain (slope, relief). Covers 60N-56S only | `earthaccess` | Download: Earthdata Login |
| 3 | HLS Landsat 30 m (`HLSL30` v2.0, `C2021957657-LPCLOUD`) | LP DAAC | Earth: vegetation/bare ground check on the top candidates (too heavy for global grid) | `earthaccess` | Earthdata Login |
| 4 | MRO CRISM MTRDR mineral maps | PDS Geosciences | Mars targets: mineral signature (Jezero etc.) | ODE REST `https://ode.rsl.wustl.edu/mars/` | No |
| 5 | Mars Trek WMTS (CTX mosaic, MOLA colour hillshade) | Solar System Treks (JPL) | Mars terrain + basemap/verify links in UI | WMTS tiles, open CORS | No |
| 6 | LRO Diviner surface & polar temperature maps | UCLA / PDS | Moon targets: temperature, cold traps, thermal swing | `https://www.diviner.ucla.edu/data` | No |

## Gap: the list has no Earth climate data
Cold, aridity, ice, polar light and thermal swing need Earth climate. Use **NASA POWER climatology** (free, no login, API)
as the supporting NASA source. In the app/video say clearly: "primary = challenge datasets, POWER = supporting".

## Do FIRST (Boy 1, Earthdata login = 5 min, do it NOW)
1. Create free account: https://urs.earthdata.nasa.gov  -> `pip install earthaccess` -> `earthaccess.login()`
2. Run `python scripts/earthdata_search.py` (search only, proves access works).
3. Pipeline order: SRTMGL1 -> D4 first (easiest), POWER -> D1,D2,D6,D7,D8, EMIT -> D5,D3 last (hardest, partial coverage OK).

## Safety net
If a download fails or is too slow: keep the sample grid (data/sample), say so honestly, and ship. A working
app with 4 real dimensions beats a broken one with 8.
