# NASA Space Apps 2026 — submission material (DRAFT, not submitted)

> Nothing has been submitted. **Deadline not verified:** the official site could not be fetched from this environment (certificate error), and the
> proposal (Sun 15 Nov, 11:59 PM local) and the handoff ("~15 hours left" on Saturday evening) disagree. Check the official team/challenge page for the exact local-event
> and global deadlines, the demo limit (the proposal says a video up to 30 s or up to 7 slides) and any live-pitch time before relying on these notes.

## Project overview
**ASTRANOVUS** (Team Astravant, Islamabad). Challenge: *Identify Earth Locations that Analog the Permanent Moon Base Locations and Mars.*

## Problem
Teams that test rovers, drills or instruments need Earth sites that resemble a specific lunar or Martian environment, but "best analog" depends on what is being tested,
and analog choices are rarely accompanied by transparent data coverage and limits.

## Solution
Pick Moon/Mars → pick an experiment (12 scenarios, each labelled NASA-documented / related / ASTRANOVUS proposal, with NASA links) → pick a compatible reference site →
an explainable Python engine ranks Earth regions with reasons, per-dimension NASA datasets, weak/missing data, confidence, and what Earth cannot reproduce.

## NASA data used
MODIS Terra MOD11C3 / MOD13C2 / MOD10CM (collection 061), GPM IMERG V07B, NASA POWER climatology; reference-site evidence from NASA/LRO Diviner, NASA Artemis, NASA/PSI SWIM, NASA/JPL Perseverance. NASA SRTMGL1 (v003) tiles for the top candidate regions (local terrain check only).

## Differentiators
Purpose-driven recommendations; data-unavailable states instead of invented results; proxies and partial-season data labelled; held-out validation against NASA-documented analog sites; no opaque model.

## Limitations (say these out loud)
5° grid; MODIS/GPM cover a single year (2024); terrain and rock missing; ice is a snow proxy; reference-site rules are drafts with partial evidence; results are candidate regions, not verified test sites; not an official NASA tool.

## AI usage disclosure (suggested wording)
"Code, documentation and parts of the data pipeline were developed with the assistance of Claude (Anthropic). Data sources, scientific choices and all results were reviewed by the team. The recommendation engine is a transparent rule-and-weight model, not a generative or black-box AI system."

## Demo scenarios (real model outputs from the current grid, built after the full-year 2024 integration)
**Moon — water-ice prospecting, reference site "Permanently shadowed crater floor"** (data state: partial; ice is a snow-cover proxy); marker = highest-scoring 5° cell of each region:
1. Greenland (77.5°N, 42.5°W): score 95.97, coverage 77 %, medium confidence, region of 44 cells, outside SRTM coverage (terrain not verified)
2. Siberia (72.5°N, 107.5°E): score 85.27, coverage 93 %, high confidence, region of 3 cells
3. Land region near 72.5°N, 142.5°E: score 84.91, coverage 93 %, medium confidence, region of 1 cells

**Mars — geological sampling, reference site "Jezero crater delta"** (data state: partial; terrain and rock not in the score); marker = highest-scoring 5° cell of each region:
1. Taklamakan Desert (37.5°N, 87.5°E): score 98.24, coverage 76 %, medium confidence, region of 54 cells, SRTM 1° tile: moderate, mean slope 14.04°
2. Atacama Desert (22.5°S, 67.5°W): score 94.41, coverage 76 %, medium confidence, region of 1 cells, SRTM 1° tile: moderate, mean slope 8.55°
3. Land region near 27.5°S, 17.5°E: score 91.02, coverage 76 %, medium confidence, region of 1 cells, SRTM 1° tile: moderate, mean slope 7.74°

Re-run before recording: numbers change if the grid or profiles change. Validation: see `docs/VALIDATION.md` (small sample; indicative only).

## Pitch narrative (≈3 min)
1. "Where on Earth should we test for the Moon or Mars?" depends on *what* you test. 2. Walk the wizard (Moon → water ice → shadowed crater). 3. Show the map, the top region's
reasons, datasets and **missing data**. 4. Compare two regions. 5. Methodology page: honest limits and validation. 6. "Next: full-year MODIS, SRTM terrain, EMIT geology, grounded LOLA/MOLA/Diviner values."

## Checklist
[ ] verify deadline/format officially · [ ] confirm GitHub link + AI disclosure · [ ] deploy and run final real-data check · [ ] record 30 s video / ≤7 slides · [ ] submit yourself
