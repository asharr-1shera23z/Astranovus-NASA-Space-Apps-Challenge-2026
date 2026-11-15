<div align="center">

# ASTRANOVUS

### Finding Earth Analogues for Lunar and Martian Mission Research

**An explainable, data-driven platform for exploring where on Earth specific Moon- and Mars-related field experiments may be studied.**

[![Challenge](https://img.shields.io/badge/NASA%20Space%20Apps%20Challenge-2026-0B3D91?style=for-the-badge&logo=nasa&logoColor=white)](https://www.spaceappschallenge.org/)
[![Frontend](https://img.shields.io/badge/Frontend-React%20%2B%20TypeScript-3178C6?style=for-the-badge&logo=typescript&logoColor=white)](https://react.dev/)
[![Backend](https://img.shields.io/badge/Backend-FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Data](https://img.shields.io/badge/Data-NASA%20Earth%20Observation-0B3D91?style=for-the-badge&logo=nasa&logoColor=white)](https://earthdata.nasa.gov/)

[**Launch Astranovus**](https://astranovus.vercel.app/) · [**Explore the source code**](https://github.com/asharr-1shera23z/Astranovus-NASA-Space-Apps-Challenge-2026) · [**Read the methodology**](docs/METHODOLOGY.md)

</div>

---

## The challenge

Preparing for long-duration human and robotic exploration of the Moon and Mars requires testing instruments, mobility systems, habitat operations, resource-prospecting techniques, and field procedures in demanding environments.

Earth offers valuable analogue environments, but there is no single place that is universally the best analogue. A location suitable for studying dry, barren terrain may be a poor choice for investigating cold-trap conditions or ice-prospecting workflows.

The central question behind Astranovus is:

> **For a particular lunar or Martian mission experiment, which regions on Earth share the most relevant measurable environmental characteristics, and how strong is the evidence behind that comparison?**

## What is Astranovus?

**Astranovus** is an independent research prototype developed by **Team Astravant** for the NASA Space Apps Challenge 2026 challenge, *Identify Earth Locations that Analog the Permanent Moon Base Locations and Mars*.

It is a purpose-driven Earth-analogue exploration platform. Users select a planetary body, a mission experiment, and a compatible lunar or Martian reference environment. Astranovus then evaluates Earth land-grid cells, applies experiment-specific requirements, groups nearby candidates into regions, and presents ranked results with explanations.

Rather than returning a black-box similarity score, the platform exposes:

- The environmental dimensions contributing to each recommendation.
- The public Earth-observation products used to calculate those dimensions.
- Data coverage, missing measurements, and proxy-based evidence.
- The reasons a candidate matches, where it is weak, and what remains unverified.
- Important physical differences that no Earth location can reproduce.

**Astranovus is a decision-support and research exploration prototype, not an official NASA product, a landing-site selection system, or a certification of field-site suitability.**

## Explore the platform

**Live application:** [https://astranovus.vercel.app/](https://astranovus.vercel.app/)

The application is designed around a mission-oriented workflow:

1. **Choose a planetary body:** Moon or Mars.
2. **Choose an experiment:** Select one of the supported mission scenarios.
3. **Select a reference environment:** Choose a compatible planetary target.
4. **Explore candidate regions:** Inspect the ranked Earth regions on the map.
5. **Understand the evidence:** Review dimension-level matches, data coverage, confidence indicators, and caveats.
6. **Compare limitations:** See which environmental conditions cannot be reproduced on Earth.

> The live application and API must be available for interactive features. Consult the deployment documentation if a service is temporarily unavailable.

## What makes Astranovus different?

| Design principle | How Astranovus applies it |
|---|---|
| **Purpose-specific comparison** | Ranks locations for a defined experiment instead of treating every mission as the same problem. |
| **Explainable scoring** | Uses explicit dimension rules, weights, gates, and similarity calculations rather than an opaque generative model. |
| **Evidence visibility** | Exposes the data source, dimension status, coverage, and limitations behind a result. |
| **Missing-data awareness** | Missing observations remain missing; they are not silently converted into favourable measurements. |
| **Physical constraints** | Separates environmental resemblance from fundamental differences in gravity, atmosphere, radiation, and surface material. |
| **Validation and reproducibility** | Includes data checks, experiment-level invariants, benchmark analyses, sensitivity tests, and provenance records. |

---

## Scientific and technical approach

### 1. Earth observation data pipeline

Astranovus builds a global Earth land grid from downloaded and processed public Earth-observation and environmental datasets.

The current processed grid contains **3,435 land cells** at a **2.5° spatial resolution** (approximately 280 km at the equator), including Antarctica. Each cell is described using up to eight environmental dimensions.

The pipeline is designed to preserve source data, document transformations, and distinguish measured or derived values from proxies and unavailable evidence.

### 2. Environmental dimensions

| ID | Dimension | What it represents | Current evidence |
|---|---|---|---|
| D1 | Cold | Relative coldness based on annual 2 m air temperature | NASA POWER-derived |
| D2 | Aridity | Relative dryness based on annual precipitation | NASA POWER-derived; cross-checked against GPM IMERG |
| D3 | Barren surface | Low vegetation signal based on peak monthly NDVI | MODIS MOD13C2-derived; unavailable for selected snow/ice-covered cells |
| D4 | Terrain | Coarse within-cell elevation relief | SRTMGL30 and NSIDC Antarctic DEM-derived |
| D5 | Rock composition | Silicate-emissivity contrast over eligible bare-ground cells | ASTER GED proxy; sparse coverage |
| D6 | Ice / snow | Mean observed snow-cover signal | MODIS MOD10CM proxy; not a measurement of subsurface water ice |
| D7 | Polar light | Seasonal swing in surface solar irradiance | NASA POWER-derived proxy |
| D8 | Thermal swing | Day/night land-surface temperature difference | MODIS MOD11C3-derived |

All dimensions are normalized as percentile ranks among valid Earth cells. A higher percentile means a stronger value of the corresponding trait, not necessarily a better match for every planetary target.

**Important:** a dimension's availability and evidence quality vary. In particular, D5 is available for only a small fraction of cells, while D6 is a snow-cover proxy and must not be interpreted as direct evidence of subsurface ice.

### 3. Data sources

The current pipeline uses the following public datasets and products:

| Dataset / product | Provider | Role in Astranovus |
|---|---|---|
| [NASA POWER](https://power.larc.nasa.gov/) | NASA | Annual temperature, precipitation, and surface solar-irradiance inputs |
| [MODIS Terra MOD11C3](https://lpdaac.usgs.gov/products/mod11c3v061/) | NASA LP DAAC | Daytime and nighttime land-surface temperature |
| [MODIS Terra MOD13C2](https://lpdaac.usgs.gov/products/mod13c2v061/) | NASA LP DAAC | Monthly vegetation index (NDVI) |
| [MODIS Terra MOD10CM](https://nsidc.org/data/mod10cm/versions/61) | NASA / NSIDC | Monthly snow-cover observations |
| [GPM IMERG](https://gpm.nasa.gov/data/imerg) | NASA | Precipitation cross-check |
| [SRTM](https://lpdaac.usgs.gov/products/srtmgl1v003/) / SRTMGL30 | NASA / LP DAAC | Elevation and terrain-relief information |
| [NSIDC Antarctic DEM](https://nsidc.org/data/nsidc-0422) | NSIDC | Antarctic terrain coverage |
| ASTER Global Emissivity Dataset (GED) | NASA / LP DAAC | Bare-ground silicate-emissivity proxy |

Planetary reference profiles and mission context are assembled from documented sources including NASA, NASA/JPL, LRO/Diviner, Mars Trek, and related scientific references. The evidence status of individual profile rules is tracked in the repository documentation.

See [Data Sources](docs/DATA_SOURCES.md), [Methodology](docs/METHODOLOGY.md), and [Target Evidence](docs/TARGET_EVIDENCE.md) for product details, provenance, and evidence status.

### 4. Scoring and ranking

Astranovus uses an interpretable weighted-similarity model.

For each target, a set of rules describes whether a dimension should be relatively high, relatively low, or within a preferred interval.

For a dimension with percentile value \(p\), the similarity function is:

- **High is preferred:** \(s = p\)
- **Low is preferred:** \(s = 1-p\)
- **A preferred band is defined:** similarity is 1 inside the interval and decreases linearly with distance outside it.

The raw score for a cell is the weighted mean of the available dimension similarities:

\[
S = 100 \times \frac{\sum_i w_i s_i}{\sum_i w_i}
\]

where \(w_i\) is the configured importance weight and \(s_i\) is the dimension-level similarity.

The engine also reports **coverage**, the fraction of the target's total configured weight for which the cell has usable data. The evidence-adjusted score accounts for missing weighted evidence by assigning the missing share a neutral score of 50:

\[
S_{\mathrm{adj}} = C S + (1-C)\times 50
\]

where \(C\) is weighted coverage expressed from 0 to 1.

This distinction matters: a high raw score based on limited evidence should not be treated as equivalent to a similarly high score supported by complete observations.

### 5. Experiment-specific requirements

The mission layer maps **12 experiment scenarios** onto compatible lunar and Martian reference profiles. Each experiment includes a NASA-grounding classification:

- **Direct:** supported by directly relevant NASA mission or dataset context.
- **Related:** connected to relevant mission needs, but not a NASA-published Earth-site selection rule.
- **Indirect:** a team-proposed mapping that requires additional evidence.

Experiment profiles can apply:

- **Dimension multipliers** to change the relative importance of environmental characteristics.
- **Hard gates** to exclude cells that do not meet required conditions.
- **Coverage thresholds** to prevent weakly supported cells from being presented as reliable recommendations.

A missing value does not silently pass a gate. It is treated as unverified or excluded according to the selected result mode and documented rules.

### 6. From grid cells to candidate regions

The scoring engine evaluates individual grid cells. The recommendation layer then groups nearby high-ranking cells into broader candidate regions.

A displayed region is an exploration lead, not a surveyed field site. Its marker and footprint represent the underlying grid cell and region grouping, not a precise operational boundary.

---

## Validation, evaluation, and scientific limitations

Astranovus includes validation at multiple levels:

- **Data validation:** checks processed inputs, expected fields, ranges, and missing-data behaviour.
- **Experiment validation:** evaluates 12 scenarios across 25 compatible experiment-target pairs through the real API code path.
- **Invariant checks:** checks that required gates, coverage rules, ranking order, and dry-ground exclusions behave as intended.
- **Analogue benchmarking:** compares documented analogue-site cells with the wider Earth-cell ranking and target-scoped negative controls.
- **Sensitivity analysis:** examines how rankings respond to weight perturbations, missing dimensions, and alternative scoring choices.
- **Provenance tracking:** records dataset and configuration hashes, seeds, cohort membership, and other reproducibility information in validation outputs.

### Current validation snapshot

The repository's current reports document:

- **3,435** processed Earth land-grid cells.
- **12** experiment scenarios.
- **25** experiment-target combinations checked.
- **0** invariant violations in the reported experiment-validation run.
- **49** planetary-reference evidence rows, of which **32** are marked supported, **4** rules were retired, and **13** remain unverified in the current project-status report.

These figures describe the project's current documented state, not a claim of complete scientific validation.

The benchmark is deliberately narrow. Its central question is whether documented analogue-site cells rank above the median Earth cell and above selected negative controls for the corresponding target. It does **not** establish that a recommended location is operationally suitable for a particular experiment.

The current scientific validation report also identifies important weaknesses: small benchmark cohorts, limited independent evaluation, weak coverage for some lunar and Martian target types, and no demonstrated advantage over a simple dry-and-barren baseline on the current benchmark. These findings are retained rather than hidden.

For full results, uncertainty intervals, failure cases, baselines, and interpretation, see:

- [Validation report](docs/VALIDATION.md)
- [Scientific validation report](docs/SCIENTIFIC_VALIDATION_REPORT.md)
- [Experiment validation](docs/EXPERIMENT_VALIDATION.md)
- [Failure-case analysis](docs/FAILURE_CASE_ANALYSIS.md)
- [Ranking stability](data/ranking_stability.json)
- [Project status](docs/PROJECT_STATUS.md)

### What Earth cannot reproduce

Even an excellent environmental analogue cannot reproduce the full lunar or Martian environment.

**Moon-related limitations**
- Earth's surface gravity is approximately six times lunar gravity.
- Earth has an atmosphere, weather, and humidity; the Moon essentially does not.
- Earth's atmosphere and magnetic field provide radiation shielding absent at the lunar surface.
- Terrestrial soils do not reproduce the physical and electrostatic properties of lunar regolith.

**Mars-related limitations**
- Earth's surface gravity is approximately 2.6 times Martian gravity.
- Mars has a very thin, mostly carbon-dioxide atmosphere.
- Radiation exposure differs substantially from that at Earth's surface.
- Terrestrial geology and biology cannot fully reproduce Martian surface chemistry and environmental history.

Astranovus therefore treats analogue selection as a comparison of selected measurable characteristics, not a claim that Earth can recreate another world.

### Known limitations

The following limitations are important when interpreting results:

1. **Spatial resolution:** the global grid uses 2.5° cells, roughly 280 km at the equator. It is suitable for broad regional screening, not site-scale engineering decisions.
2. **Temporal coverage:** MODIS vegetation and temperature and GPM inputs cover calendar year 2024, a single year. MODIS snow cover uses a 2015–2024 monthly climatology.
3. **Terrain scale:** global terrain relief is approximately 1 km scale. Separate 30 m SRTM checks exist only for selected candidate regions, and SRTM does not cover every latitude.
4. **Rock-composition proxy:** ASTER emissivity is not a direct mineralogical survey and is currently available for only about 13% of grid cells.
5. **Ice proxy:** MODIS snow cover is not a direct measurement of glacier thickness, permafrost, or subsurface water ice.
6. **Planetary evidence:** some reference-site rules remain unverified or are based on general planetary context rather than site-specific measurements.
7. **Benchmark size:** the analogue-site benchmark is small. Frozen independent evaluation currently contains only three primary site pairs, so its metrics are not conclusive.
8. **No experiment-level ground truth:** there is no verified dataset establishing that a recommended Earth region will work for a specific rover, drill, instrument, or habitat experiment.

These limitations are surfaced because responsible scientific tools should communicate uncertainty as clearly as they communicate results.

---

## System architecture

Astranovus separates data preparation, scientific computation, API delivery, and visualization.

```text
                 PUBLIC EARTH-OBSERVATION DATA
       NASA POWER · MODIS · GPM IMERG · SRTM · ASTER · NSIDC
                              |
                              v
                    DATA PROCESSING PIPELINE
             scripts/build_earth_grid.py and validators
                              |
                              v
                   PROCESSED EARTH LAND GRID
          earth_grid.csv · features · metadata · evidence
                              |
                              v
                   SCIENTIFIC MODEL LAYER
             model/scoring_core.py · model/recommend.py
         weighted similarity · gates · coverage · regions
                              |
                              v
                       FASTAPI BACKEND
              backend/main.py · backend/mission_api.py
                              |
                              v
                    REACT WEB APPLICATION
           React · TypeScript · Vite · Tailwind CSS
                 Leaflet maps · 3D globe · charts
```

**Scoring is performed by the Python backend, not in the browser.** The frontend presents API results and their supporting explanations.

### Technology stack

| Layer | Technologies |
|---|---|
| Frontend | React, TypeScript, Vite |
| Styling and UI | Tailwind CSS, Lucide React |
| Maps and visualization | Leaflet, React Leaflet, `react-globe.gl`, Recharts |
| Backend | Python, FastAPI |
| Data processing | pandas, NumPy, geospatial and scientific data tooling |
| Testing | pytest, Vitest, TypeScript checks |
| Deployment | Vercel (frontend), Render / Docker configuration (backend) |

---

## Repository structure

```text
Astranovus-NASA-Space-Apps-Challenge-2026/
├── backend/                 # FastAPI application and mission API
├── data/
│   ├── raw/                 # Downloaded source data (not all raw files are committed)
│   ├── processed/           # Built Earth grid and derived outputs
│   ├── sample/              # Synthetic sample data for UI-only development
│   ├── targets.json         # Lunar and Martian reference profiles
│   ├── purposes.json        # Mission-purpose definitions
│   └── experiments.json     # Experiment scenarios
├── docs/                    # Methodology, data, validation, and deployment reports
├── frontend/                # React + TypeScript application
├── model/                   # Scoring and recommendation engine
├── scripts/                 # Data acquisition, processing, and validation
├── tests/                   # Backend and scientific-engine tests
├── Dockerfile
├── render.yaml
├── requirements-data.txt
└── README.md
```

---

## Run locally

### Prerequisites

- Python **3.12**
- Node.js and npm
- Git
- The processed real-data grid at `data/processed/earth_grid.csv` for normal backend operation

### 1. Clone the repository

```bash
git clone https://github.com/asharr-1shera23z/Astranovus-NASA-Space-Apps-Challenge-2026.git
cd Astranovus-NASA-Space-Apps-Challenge-2026
```

### 2. Set up the Python environment

**Windows PowerShell**

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-data.txt -r backend/requirements.txt
```

**macOS / Linux**

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-data.txt -r backend/requirements.txt
```

### 3. Start the backend

From the repository root:

```bash
python -m uvicorn backend.main:app --reload --port 8000
```

The API is available at:

- `http://localhost:8000`
- Interactive API documentation: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/health`

The backend intentionally refuses to start if the real processed grid is missing. It does not silently substitute synthetic data.

For UI-only development, the synthetic sample grid can be enabled explicitly:

**Windows PowerShell**
```powershell
$env:ASTRANOVUS_ALLOW_SAMPLE="1"
python -m uvicorn backend.main:app --reload --port 8000
```

**macOS / Linux**
```bash
ASTRANOVUS_ALLOW_SAMPLE=1 python -m uvicorn backend.main:app --reload --port 8000
```

When sample data is enabled, the API and UI identify it as synthetic. Do not use sample results as scientific findings.

### 4. Start the frontend

Open a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Vite prints the local frontend URL, normally `http://localhost:5173`.

### 5. Run checks

Backend tests:

```bash
python -m pytest -q tests
```

Frontend checks:

```bash
cd frontend
npm run lint
npm test
npm run build
```

---

## Rebuilding and validating the data

The repository includes scripts for rebuilding the Earth grid and reproducing the validation workflow. These commands assume the required source files have already been downloaded and placed in the expected `data/raw/` locations.

```bash
python scripts/build_earth_grid.py
python scripts/validate_data.py
python scripts/build_target_evidence.py
python scripts/validate_known_analogs.py
python scripts/sensitivity_analysis.py
python scripts/experiment_validation.py
python scripts/build_planetary_measurements.py
```

The versioned analogue-dataset workflow includes:

```bash
python scripts/build_analog_dataset_v3.py
python scripts/validate_v3.py
```

**Important reproducibility note:** `build_analog_dataset_v3.py` rebuilds the dataset and freezes cohort membership. Do not run it casually when trying to reproduce the already-reported frozen evaluation. Read the validation documentation first. The frozen cohort is scored with `python scripts/validate_v3.py --final`; the final evaluation is intended to be run once under the documented protocol.

Additional diagnostics:

```bash
python scripts/diagnose_targets.py
python scripts/d4_analysis.py
python scripts/ranking_stability.py
```

For the exact data contract, expected inputs, product metadata, and validation sequence, consult the relevant files in `docs/`.

---

## Configuration

| Variable | Component | Purpose |
|---|---|---|
| `ASTRANOVUS_ENV=production` | Backend | Enables production safeguards, including rejecting wildcard CORS |
| `ASTRANOVUS_CORS_ORIGINS` | Backend | Comma-separated list of allowed frontend origins |
| `ASTRANOVUS_ALLOW_SAMPLE=1` | Backend | Explicitly permits the synthetic sample grid for UI development |
| `VITE_API_URL` | Frontend | Backend API base URL; defaults to `/api` for local proxy configuration |

For deployment instructions, see [Deployment](docs/DEPLOYMENT.md) and the repository's `Dockerfile` and `render.yaml`.

---

## Documentation

The repository contains detailed technical and scientific documentation. Start with these:

| Document | Description |
|---|---|
| [Methodology](docs/METHODOLOGY.md) | Data processing, dimensions, normalization, and scientific approach |
| [Data sources](docs/DATA_SOURCES.md) | Dataset providers, products, and acquisition notes |
| [Data contract](docs/DATA_CONTRACT.md) | Input schema, scoring rules, coverage, and API behaviour |
| [Scoring methodology](docs/SCORING_METHODOLOGY.md) | Mathematical details of the ranking model |
| [Target evidence](docs/TARGET_EVIDENCE.md) | Evidence supporting planetary reference-profile rules |
| [Validation](docs/VALIDATION.md) | Analogue validation results |
| [Scientific validation](docs/SCIENTIFIC_VALIDATION_REPORT.md) | Benchmark design, results, uncertainty, and limitations |
| [Experiment validation](docs/EXPERIMENT_VALIDATION.md) | Experiment-target matrix and invariant checks |
| [Failure-case analysis](docs/FAILURE_CASE_ANALYSIS.md) | Cases where the model performs poorly |
| [Project status](docs/PROJECT_STATUS.md) | Current data, evidence, and implementation status |
| [Deployment](docs/DEPLOYMENT.md) | Hosting and deployment configuration |
| [Submission notes](docs/SUBMISSION.md) | Challenge presentation notes and submission checklist |

---

## Responsible interpretation

Astranovus is intended to help researchers and mission planners **explore, compare, and question** possible Earth analogues. It should not be used as the sole basis for selecting field locations, certifying equipment, assessing crew safety, or making mission-critical decisions.

A high score means that a location resembles a selected set of measurable characteristics under the current model configuration. It does not mean that the location is a complete physical analogue, that all relevant data are available, or that the model has established operational suitability.

Always inspect the per-dimension evidence, coverage, proxy labels, validation reports, and known limitations before interpreting a recommendation.

## Team

**Team Astravant**  
NASA Space Apps Challenge 2026

Project: **Astranovus**

---

## Acknowledgements

We acknowledge NASA, NASA LP DAAC, NASA POWER, NASA GPM, NSIDC, and the scientific teams responsible for the public Earth-observation and planetary datasets used in this project.

We are grateful to the open-source communities behind Python, FastAPI, React, Vite, pandas, NumPy, Leaflet, and the other tools that make this research prototype possible.

## AI assistance

AI tools assisted parts of the software development and documentation process. The project’s data-source selection, scientific assumptions, model configuration, validation procedures, and interpretation require human review by the team. Astranovus's recommendation engine is an explicit rule-and-weight model; it is **not** a generative AI model.

## License

No license is specified in this repository at the time of writing. Unless a license is added, standard copyright restrictions apply. Add an appropriate `LICENSE` file before inviting reuse, redistribution, or contributions under open-source terms.

---

<div align="center">

**ASTRANOVUS · Explore Earth. Understand other worlds.**

Built by **Team Astravant** for the NASA Space Apps Challenge 2026.

</div>
