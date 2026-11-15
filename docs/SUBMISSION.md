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
5° grid; MODIS/GPM cover a single year (2024); rock missing and terrain only 1-km relief; ice is a snow proxy; reference-site rules are drafts with partial evidence; results are candidate regions, not verified test sites; not an official NASA tool.

## AI usage disclosure (suggested wording)
"Code, documentation and parts of the data pipeline were developed with the assistance of Claude (Anthropic). Data sources, scientific choices and all results were reviewed by the team. The recommendation engine is a transparent rule-and-weight model, not a generative or black-box AI system."

## Demo scenarios (real model outputs from the final 2.5° grid)
**Moon — water-ice prospecting, reference site "Permanently shadowed crater floor"** (data state: partial; ice is a snow-cover proxy); marker = highest-scoring 2.5° cell of each region, regions bounded to 15°:
1. Antarctica (81.2°S, 93.8°E): score 90.77, coverage 77 %, medium confidence, outside SRTM coverage (30 m terrain not verified)
2. Antarctica (76.2°S, 11.2°E): score 84.42, coverage 77 %, medium confidence, 30 m terrain check not run for this region
3. Antarctica (71.2°S, 146.2°E): score 80.74, coverage 77 %, medium confidence, 30 m terrain check not run for this region
4. Antarctica (81.2°S, 91.2°W): score 77.94, coverage 77 %, medium confidence, 30 m terrain check not run for this region
5. Greenland (71.2°N, 36.2°W): score 76.87, coverage 84 %, medium confidence, outside SRTM coverage (30 m terrain not verified)

**Mars — geological sampling, reference site "Jezero crater delta"** (data state: partial; rock missing; terrain is 1-km relief); marker = highest-scoring 2.5° cell of each region, regions bounded to 15°:
1. Gobi Desert (41.2°N, 91.2°E): score 95.16, coverage 76 %, medium confidence, SRTM 1° tile: flat, mean slope 2.21°
2. Sahara Desert (23.8°N, 16.2°E): score 93.8, coverage 76 %, medium confidence, SRTM 1° tile: flat, mean slope 3.54°
3. Sahara Desert (26.2°N, 33.8°E): score 92.57, coverage 76 %, medium confidence, 30 m terrain check not run for this region
4. Arabian Peninsula (16.2°N, 46.2°E): score 91.55, coverage 76 %, medium confidence, 30 m terrain check not run for this region
5. Sahara Desert (28.8°N, 1.2°W): score 90.35, coverage 76 %, medium confidence, 30 m terrain check not run for this region

Re-run before recording: numbers change if the grid or profiles change. Validation: see `docs/VALIDATION.md` (small sample; indicative only).

## Pitch narrative (≈3 min)
1. "Where on Earth should we test for the Moon or Mars?" depends on *what* you test. 2. Walk the wizard (Moon → water ice → shadowed crater). 3. Show the map, the top region's
reasons, datasets and **missing data**. 4. Compare two regions. 5. Methodology page: honest limits and validation. 6. "Next: full-year MODIS, SRTM terrain, EMIT geology, grounded LOLA/MOLA/Diviner values."

## Checklist
[ ] verify deadline/format officially · [ ] confirm GitHub link + AI disclosure · [ ] deploy and run final real-data check · [ ] record 30 s video / ≤7 slides · [ ] submit yourself
