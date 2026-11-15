# Values that need manual retrieval (Moon Trek / Mars Trek / PDS)

Everything retrievable from public NASA pages was retrieved and recorded in `data/target_evidence.csv`. The numbers below were NOT available in any page this
project could read; nobody should type them in from memory. For each one: open the tool, record the value, the layer name, the coordinates you sampled and a
screenshot or permalink, then add a row to `data/target_evidence.csv` (`status=supported`, `evidence_type=observed`) and rerun `scripts/build_target_evidence.py` after
adding the entry to its table.

| Target | Needed value | Why it matters | How to get it |
|---|---|---|---|
| MOON_PSR | Median LOLA slope on the Shackleton floor (and a second PSR floor, e.g. Faustini) | tests the "low roughness floor" rule (D4) | Moon Trek (trek.nasa.gov/moon): search "Shackleton", add the LRO LOLA slope layer, use the area/profile tool over the floor, note median slope and baseline |
| MOON_PSR | Diviner annual maximum and mean surface temperature of the floor | tests the cold rule quantitatively (D1) | Moon Trek Diviner temperature layers (or diviner.ucla.edu data products) over the same floor polygon |
| MOON_SP_RIDGE | LOLA slope statistics and percent-sunlit fraction on the Connecting Ridge / Peak Near Shackleton | quantifies D4 (rugged) and D7 for the ridge | Moon Trek: LOLA slope and illumination layers over the ridge polygon |
| MOON_SP_RIDGE | Surface composition (for example FeO wt %) at the ridge | confirms the feldspathic-highland statement used to retire D5 | Moon Trek: Lunar Prospector / Kaguya / Clementine FeO layers |
| MOON_LAVATUBE, MOON_MARE | Regional LOLA roughness for the maria that host pits (Mare Tranquillitatis, Marius Hills) | grounds the 0.3-0.7 terrain band (D4) | Moon Trek: LOLA slope over a mare box; record median slope and baseline |
| MARS_JEZERO | MOLA elevation and slope across the crater floor and delta | grounds the terrain band (D4) | Mars Trek (trek.nasa.gov/mars): MOLA elevation and slope layers over Jezero |
| MARS_ICE | MOLA slope and SWIM ice-consistency score over Arcadia Planitia | quantifies "flat plains with ice" (D4, D6) | Mars Trek MOLA slope; swim.psi.edu SWIM composite map |
| MARS_MUDVOLC | HiRISE/CTX mound counts and MOLA slope in Acidalia/Utopia | currently qualitative; origin is debated | Mars Trek CTX mosaic; HiRISE catalogue entries cited in the CSV |
| MARS_CHLORIDE | Latitude/longitude list of the ~200 THEMIS chloride deposits | to test whether any deposit-bearing region is resolvable at all (deposits are 1-25 km2, far below a 2.5 degree cell) | Osterloo et al. 2008 deposit table via NASA PDS / the Odyssey THEMIS release cited in the CSV |
| MARS_AEOLIAN | MOLA slope over a major dune field | quantifies "low relief" (D4) | Mars Trek MOLA slope over the dune polygon |

Weights and band limits stay unchanged until real values exist.
