# Moon / Mars reference-site evidence

Generated from `scripts/build_target_evidence.py` → `data/target_evidence.csv` (one row per rule) and
`data/target_evidence_summary.json`. Sources were retrieved on 2026-11-15. **No weight or rule was changed**: evidence here is qualitative and supports direction only.

| Target | rules with a retrieved source | main sources |
|---|---|---|
| MOON_PSR | 2 / 6 (cold, ice) | UCLA Diviner (PSR ~25 K minima, <110 K ice trapping), NASA LRO 2009 release |
| MOON_SP_RIDGE | 1 / 7 (polar light) | NASA: Artemis III candidate regions have sites with continuous sunlight for 6.5 days |
| MOON_LAVATUBE | 1 / 5 (rock) | NASA LRO lunar pits / Mini-RF cave evidence |
| MARS_ICE | 2 / 6 (ice, low relief) | NASA/PSI SWIM subsurface ice maps |
| MARS_JEZERO | 3 / 6 (rock, aridity, terrain) | NASA/JPL Jezero landing-site and delta articles |
| MARS_MUDVOLC, MARS_CHLORIDE, MARS_AEOLIAN, MOON_MARE | 0 | none retrieved: **unverified** |

## Open concerns (flagged, not silently fixed)
* **MOON_PSR / D7_polar_light (weight 2, "high")**: a permanently shadowed region receives no sunlight, while D7 rewards a *large* Earth seasonal light swing. The direction is not justified. Review before relying on it.
* **MOON_LAVATUBE / D8 thermal swing "high"**: NASA reports pit interiors stay near 17 °C (stable). The rule only makes sense for the surface.
* Band limits (e.g. terrain 0.3–0.7) and all weights remain team drafts: percentile terrain has no physical LOLA/MOLA calibration yet.
* To strengthen the profiles, fill `value_found` with LOLA/MOLA/Diviner/SWIM *values* via Moon Trek / Mars Trek and only then adjust weights, documenting each change here.

Sources: [Diviner science](https://www.diviner.ucla.edu/science) · [Diviner ice stability](https://www.diviner.ucla.edu/single-post/diviner-data-used-to-map-the-stability-of-ices-at-the-lunar-poles) · [NASA Artemis III regions](https://www.nasa.gov/news-release/nasa-identifies-candidate-regions-for-landing-next-americans-on-moon/) · [LRO lunar pits](https://www.nasa.gov/solar-system/nasas-lro-finds-lunar-pits-harbor-comfortable-temperatures/) · [SWIM map](https://science.nasa.gov/resource/swim-map-shows-subsurface-water-ice-on-mars/) · [Jezero landing site](https://www.jpl.nasa.gov/news/press_kits/mars_2020/launch/mission/landing_site/)
