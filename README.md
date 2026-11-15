# ASTRANOVUS — NASA Space Apps 2026 (Team Astravant)

**Challenge:** *Identify Earth Locations that Analog the Permanent Moon Base Locations and Mars.*

ASTRANOVUS is an independent research prototype (not an official NASA tool, rating or landing-site certification).
You choose **Moon or Mars → an experiment you want to test → a compatible planetary reference site**, and an explainable
Python engine ranks the Earth regions that best fit that purpose, showing the NASA data behind every number, what is
missing, and what Earth cannot reproduce.

## Architecture
```
NASA POWER + MODIS (MOD11C3, MOD13C2, MOD10CM) + GPM IMERG  --scripts/build_earth_grid.py-->  data/processed/earth_grid.csv (+ features, metadata)
data/targets.json (reference sites) + data/purposes.json (mission profiles) + data/experiments.json (12 scenarios)
                         |
        model/scoring_core.py + model/recommend.py   (explainable weighted similarity, gates, regions)
                         |
        backend/main.py (+ backend/mission_api.py)   FastAPI
                         |
        frontend/ (React + Vite + TypeScript + Tailwind + Leaflet + globe)
```
No scoring happens in the browser.

## Run locally
```bash
# one-time: isolated data/backend environment (Python 3.12)
py -3.12 -m venv .venv-data
.venv-data/Scripts/pip install -r requirements-data.txt -r backend/requirements.txt

# backend (terminal 1)
.venv-data/Scripts/python -m uvicorn backend.main:app --port 8000

# frontend (terminal 2)
cd frontend && npm install && npm run dev        # http://localhost:5173
```
The API refuses to start without `data/processed/earth_grid.csv` (no silent synthetic fallback). For UI-only work with the
synthetic sample set `ASTRANOVUS_ALLOW_SAMPLE=1`; the UI then shows a red warning banner.

## Rebuild the Earth grid from the downloaded NASA files
```bash
.venv-data/Scripts/python scripts/build_earth_grid.py        # reads data/raw/*, never modifies it; backs up the old grid
python scripts/validate_data.py
python scripts/build_target_evidence.py
python scripts/validate_known_analogs.py                     # writes docs/VALIDATION.md
```

## Tests
```bash
.venv-data/Scripts/python -m pytest -q tests    # engine + API (real grid)
cd frontend && npm run lint && npm test && npm run build
```

## Honest status
* Real NASA-derived dimensions: D1 cold, D2 aridity, D7 light (POWER, annual); D3 barren (MODIS NDVI), D6 ice **proxy** (MODIS snow), D8 thermal swing (MODIS LST) — **calendar year 2024 (12 monthly granules; one year, not a multi-year climatology)**.
* D4 terrain: NASA SRTMGL30 (~1 km) landscape relief, static (SRTM 2000). Plus a finer 30 m SRTM check for the top regions.
* **Missing:** D5 rock (no defensible lithology data yet). It stays empty and is shown as "no data yet", never zero.
* Moon/Mars reference-site rules are team drafts; see `docs/TARGET_EVIDENCE.md` for which rules have a retrieved source.
* Grid is 2.5° (3,435 land cells incl. Antarctica; ~280 km cells). Regions are candidate areas, not verified ground-test sites.

## Docs
`docs/METHODOLOGY.md` · `docs/DATA_CONTRACT.md` · `docs/DATA_SOURCES.md` · `docs/TARGET_EVIDENCE.md` · `docs/VALIDATION.md` ·
`docs/SOLUTION.md` · `docs/DEPLOYMENT.md` · `docs/SUBMISSION.md` · `docs/PROJECT_HANDOFF.md` (history)

## Rules
Never change a column/field name without telling everyone. `scripts/validate_data.py` must pass before every push.
All data are attributed to NASA/NSIDC/LP DAAC/GES DISC products listed in `docs/METHODOLOGY.md`.
