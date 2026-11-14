# ASTRANOVUS — NASA Space Apps 2026 (Team Astravant)

Challenge: **Identify Earth Locations that Analog the Permanent Moon Base Locations and Mars**

ASTRANOVUS scores every 0.25° Earth land cell (0-100) for how closely it resembles a chosen
Moon/Mars target, explains *why* (per-dimension breakdown) and lets users change the weights.

## Repo layout
```
data/dimensions.json     8 comparison dimensions (the shared vocabulary)
data/targets.json        Moon/Mars target profiles (rules + weights)   <- Boy 2 owns
data/sample/             tiny synthetic Earth grid so everyone can start now
data/processed/          real earth_grid.csv goes here                 <- Boy 1 owns
model/scoring_core.py    the scoring function (the heart of the project)
backend/main.py          FastAPI: /targets /score /site /compare
frontend/                React + Vite + Leaflet map UI
scripts/                 make_sample_grid.py, validate_data.py
docs/DATA_CONTRACT.md    READ THIS FIRST - exact file formats
docs/DATA_SOURCES.md     the NASA challenge datasets + how to get them (Boy 1 starts here)
```

## Run it (5 minutes)
```bash
# 1. data + backend
pip install -r backend/requirements.txt
python scripts/make_sample_grid.py        # makes data/sample/earth_grid_sample.csv
python scripts/validate_data.py           # must print OK
uvicorn backend.main:app --reload --port 8000

# 2. frontend (new terminal)
cd frontend && npm install && npm run dev
```
Open http://localhost:5173 — pick a target, see the score map.

## Rules
- Never change a column/field name without telling everyone (see DATA_CONTRACT.md).
- `python scripts/validate_data.py` must pass before every push.
- Small commits, push often, one branch per person: `git checkout -b yourname/feature`.
- **All data here is PLACEHOLDER until Boy 1 / Boy 2 replace it with real NASA-derived data.**
