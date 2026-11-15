"""Build data/planetary_measurements.csv (+ .json): numerical Moon/Mars measurements with full provenance.

Every row was read from a NASA/USGS/UCLA page or abstract on 2026-11-15. `retrieval` says how:
  primary_fetched  - the quoted number was read from the cited page/abstract itself
  search_summary   - the number appeared only in a web-search result summary of the cited source; the primary page could
                     not be fetched, so it must be re-verified before being relied on
Nothing here was measured by ASTRANOVUS. `evidence_class`: observed (instrument value), derived (computed from instrument
data, e.g. illumination from LOLA topography or depth from shadow length), inferred (interpretation of data).
`scope`: site (the named feature), region (a broader area), body (generic body property, NOT a site measurement).
Run:  python scripts/build_planetary_measurements.py
"""
import csv
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
RET = "2026-11-15"

U = {
    "diviner": "https://www.diviner.ucla.edu/science",
    "illum": "https://ntrs.nasa.gov/citations/20120010094",
    "shack_sci": "https://science.nasa.gov/resource/shackleton-craters-illuminated-rim-shadowed-interior/",
    "shack_svs": "https://svs.gsfc.nasa.gov/4716",
    "pits_nasa": "https://www.nasa.gov/solar-system/nasas-lro-finds-lunar-pits-harbor-comfortable-temperatures/",
    "pits_cave": "https://science.nasa.gov/solar-system/new-evidence-adds-to-findings-hinting-at-network-of-caves-on-moon/",
    "pit_marius": "https://lroc.im-ldi.com/images/202",
    "pit_tranq": "https://lroc.im-ldi.com/images/230",
    "pit_ingenii": "https://lroc.im-ldi.com/images/695",
    "slopes": "https://pubs.usgs.gov/publication/70223199",
    "moon_facts": "https://science.nasa.gov/moon/facts/",
    "mars_facts": "https://science.nasa.gov/mars/facts/",
    "jezero_sites": "https://marsnext.jpl.nasa.gov/landingsites/index.cfm",
    "jezero_kit": "https://www.jpl.nasa.gov/news/press_kits/mars_2020/launch/mission/landing_site/",
    "jezero_dtm": "https://astrogeology.usgs.gov/search/map/Mars/Mars2020/JEZ_hirise_soc_006_DTM_MOLAtopography_DeltaGeoid_1m_Eqc_latTs0_lon0_blend40",
    "meda": "https://science.nasa.gov/blog/daily-records-of-atmospheric-temperature-with-perseverance/",
    "arcadia_bramson": "https://arxiv.org/abs/1509.03210",
    "arcadia_hls2": "https://www.nasa.gov/wp-content/uploads/2015/06/hls2_newsletter_02-19_v19_tagged.pdf",
    "swim": "https://science.nasa.gov/resource/swim-map-shows-subsurface-water-ice-on-mars/",
    "mud_utopia": "https://science.nasa.gov/photojournal/candidate-mud-volcanoes-in-utopia-planitia/",
    "mud_acidalia": "https://ntrs.nasa.gov/citations/20100010305",
    "chloride": "https://www.nasa.gov/mission_pages/odyssey/odyssey-20080320.html",
}

# id, target, location, lat, lon, quantity, value, units, resolution, period, uncertainty, instrument/method,
# dataset/publication, url key, extraction, class, scope, retrieval, note
R = [
    ("M01", "MOON_PSR", "south polar permanently shadowed regions", "", "", "minimum surface temperature", "25", "K", "n/s", "LRO Diviner mapping", "n/s",
     "LRO Diviner (infrared radiometer)", "Diviner science page (UCLA)", "diviner", "quoted: temperatures in permanently shadowed craters 'can fall as low as 25K'", "observed", "region", "primary_fetched",
     "Extreme minimum, not a typical value; not tied to one crater."),
    ("M02", "MOON_PSR", "lunar south pole (to 80 deg S)", -90, "", "total permanently shadowed area (south)", "16055", "km2", "240 m DEM", "simulated over several 18.6-year precession cycles, 6 h steps", "n/s",
     "LOLA topography + illumination model", "Mazarico et al., LOLA illumination (NTRS 20120010094)", "illum", "quoted from abstract (north: 12,866 km2)", "derived", "region", "primary_fetched", "Model product: depends on DEM resolution."),
    ("M03", "MOON_PSR", "Shackleton crater", "", "", "crater width", "21", "km", "n/s", "n/a", "n/s", "LOLA DEM (visualization)", "NASA SVS 4716", "shack_svs", "quoted: '21 kilometers wide'", "derived", "site", "primary_fetched", "Page gives no resolution or uncertainty."),
    ("M04", "MOON_PSR", "Shackleton crater", "", "", "crater depth", "4", "km", "n/s", "n/a", "n/s", "LOLA DEM (visualization)", "NASA SVS 4716", "shack_svs", "quoted: '4 km deep'", "derived", "site", "primary_fetched", "Page gives no floor diameter or wall slope; those remain manual items."),
    ("M05", "MOON_PSR", "Shackleton crater floor", "", "", "illumination state of the floor", "perpetual shadow", "", "n/s", "n/a", "n/s", "LOLA DEM (visualization)", "NASA SVS 4716", "shack_svs", "quoted: 'Shackleton's floor is in perpetual shadow'", "derived", "site", "primary_fetched", "Qualitative; supports retiring the D7 light rule for this target."),
    ("M06", "MOON_SP_RIDGE", "location near the Shackleton rim", "", "", "continuous sunlit period per year", "240", "days", "240 m DEM", "simulated over several 18.6-year cycles", "n/s", "LOLA topography + illumination model",
     "Mazarico et al. (NTRS 20120010094)", "illum", "quoted: 'sunlit continuously for 240 days' each year", "derived", "site", "primary_fetched", "Exact rim coordinates not in the abstract: manual item."),
    ("M07", "MOON_SP_RIDGE", "location near the Shackleton rim", "", "", "longest continuous darkness", "1.5", "days", "240 m DEM", "same simulation", "n/s", "LOLA topography + illumination model",
     "Mazarico et al. (NTRS 20120010094)", "illum", "quoted: 'longest continuous period in total darkness is about 1.5 days'", "derived", "site", "primary_fetched", ""),
    ("M08", "MOON_SP_RIDGE", "three points on the Shackleton rim", "", "", "collective sunlit fraction of the year", ">90", "percent", "n/s", "per year (axial tilt effect)", "n/s", "illumination analysis (image credit NASA/GSFC/ASU)",
     "NASA Science image page", "shack_sci", "quoted: 'collectively sunlit for more than 90% of the year'", "derived", "site", "primary_fetched", "Collective illumination of three points, not of one point."),
    ("M09", "MOON_LAVATUBE", "Mare Tranquillitatis pit", "", "", "pit depth", "~100", "m", "shadow measurement", "single LROC observation geometry", "n/s", "LROC NAC shadow length", "LROC image page / NASA LRO article", "pit_tranq",
     "shadow of 55 m at 26.5 deg incidence gives depth 'a bit over 100 meters'; NASA: roughly 100 m deep", "derived", "site", "search_summary", "Shadow-based: depends on illumination geometry."),
    ("M10", "MOON_LAVATUBE", "Mare Tranquillitatis pit", "", "", "pit diameter", "~100", "m", "LROC NAC", "n/s", "n/s", "LROC NAC", "LROC image page", "pit_tranq", "reported ~100 m", "observed", "site", "search_summary", ""),
    ("M11", "MOON_LAVATUBE", "Marius Hills pit", "", "", "pit depth (conflicting values)", "40 (LROC update) vs 34 (NASA article) vs 80-88 (Kaguya)", "m", "LROC NAC / Kaguya", "different illumination", "values disagree", "shadow measurement", "LROC image 202 and NASA articles", "pit_marius",
     "reported values listed side by side, not averaged", "derived", "site", "search_summary", "Do NOT quote a single depth."),
    ("M12", "MOON_LAVATUBE", "Mare Ingenii pit", "", "", "pit depth / width", "~70 / ~120-130", "m", "LROC NAC", "shadow measurement", "n/s", "LROC NAC shadow length", "LROC image page 695", "pit_ingenii", "reported ~70 m deep, 120-130 m wide", "derived", "site", "search_summary", "Cave beneath it unconfirmed."),
    ("M13", "MOON_LAVATUBE", "Mare Tranquillitatis pit (shaded floor)", "", "", "shaded-area temperature", "17 (63 F)", "C", "n/s", "stays steady through the lunar day", "n/s", "LRO Diviner + thermal modelling", "NASA article on lunar pits", "pits_nasa", "quoted: shaded locations 'hover around a comfortable 63 F (about 17 C)'", "derived", "site", "primary_fetched", "Model-assisted, not a direct in-situ value."),
    ("M14", "MOON_LAVATUBE", "Mare Tranquillitatis pit", "", "", "possible cave extent from radar", ">200", "ft", "Mini-RF re-analysis", "2010 data", "extent unknown", "LRO Mini-RF radar", "NASA Science article", "pits_cave", "re-analysis found evidence of a cave extending more than 200 feet from the pit base", "inferred", "site", "primary_fetched", "Inference; not a confirmed lava tube."),
    ("M15", "MOON_MARE", "lunar maria (LROC NAC stereo DTMs)", "", "", "median slope", "3.5", "degrees", "15 m baseline", "31 mare DTMs", "n/s", "LROC NAC stereo topography", "USGS publication 70223199", "slopes", "reported median; highlands 9.1 degrees from 81 DTMs", "derived", "region", "search_summary", "Baseline-dependent; mapped targets may be biased."),
    ("M16", "MOON_MARE", "lunar equator", 0, "", "noon / night surface temperature", "~385-400 / ~95-100", "K", "n/s", "equatorial noon and midnight", "n/s", "LRO Diviner", "Diviner science page (UCLA)", "diviner", "reported ranges from Diviner summaries", "observed", "region", "search_summary", "Equatorial value, not a polar one."),
    ("M17", "MOON_PSR", "Moon (generic)", "", "", "surface temperature extremes", "127 / -173", "C", "n/a", "full sun / night", "n/s", "NASA Moon fact page", "NASA Science Moon facts", "moon_facts", "quoted", "observed", "body", "primary_fetched", "Generic Moon property, not a PSR measurement."),
    ("J01", "MARS_JEZERO", "Jezero crater (landing-site listing)", 18.3628, 77.5945, "reference point and elevation", "-2656", "m (MOLA geoid)", "n/s", "n/a", "n/s", "MOLA topography (planetocentric, +E)", "NASA/JPL Mars landing-site listing", "jezero_sites",
     "reported as about 77.5945 E, 18.3628 N, elevation -2656 m", "derived", "site", "search_summary", "Primary page not fetchable (certificate mismatch): re-verify. This is a landing-site reference point, not a crater average."),
    ("J02", "MARS_JEZERO", "Jezero crater", "", "", "crater diameter", "45", "km", "n/a", "n/a", "n/s", "orbital imaging", "JPL Mars 2020 press kit", "jezero_kit", "reported: 45 kilometers across", "observed", "site", "search_summary", "Delta and lake interpretations are scientific interpretations."),
    ("J03", "MARS_JEZERO", "Jezero HiRISE terrain mosaic", "18.31 to 18.67", "77.22 to 77.58", "bounds of the 1 m HiRISE DTM (MOLA-referenced)", "bounds", "deg", "1 m DTM", "n/s", "n/s", "HiRISE stereo DTM", "USGS Astropedia product", "jezero_dtm", "bounds reported in the product listing", "derived", "region", "search_summary",
     "Use this product for local slope/elevation extraction (manual or via Astropedia download)."),
    ("J04", "MARS_JEZERO", "Jezero crater floor (Perseverance)", "", "", "surface temperature range on sampled sols", "-83 to +5", "C", "rover radiometer", "example sols", "TIRS channel accuracy +-0.75 K (separate study)", "MEDA thermal infrared sensor", "NASA Science blog", "meda",
     "quoted: surface about -83 C before dawn to about 5 C at noon", "observed", "site", "primary_fetched", "Sample sols, not seasonal statistics."),
    ("A01", "MARS_ICE", "Arcadia Planitia region", "36 to 56", "-176 to -132", "region extent used in a mapping study", "36-56 N, 132-176 W", "deg", "n/s", "n/a", "n/s", "regional mapping", "SWIM-related literature (as reported)", "swim", "region quoted in a search summary of NASA/PSI sources", "inferred", "region", "search_summary", "Re-verify against the primary SWIM paper."),
    ("A02", "MARS_ICE", "Arcadia Planitia", "", "", "excess water-ice volume", "~1e4", "km3", "n/s", "n/a", "n/s", "terrace depths in simple craters + radar sounding reflection", "Bramson et al. 2015 (arXiv:1509.03210)", "arcadia_bramson", "quoted from abstract: 'excess water ice ~10^4 km^3'; 'a widespread, decameters-thick layer'", "inferred", "region", "primary_fetched", "Ice thickness is 'decameters', no single value in the abstract."),
    ("A03", "MARS_ICE", "Arcadia Planitia", "", "", "ice-rich deposit thickness (preliminary map)", "15-60", "m", "SHARAD ~15 m vertical (free space)", "n/s", "preliminary", "SHARAD radar interpretation", "NASA Human Landing Sites newsletter", "arcadia_hls2", "reported preliminary map", "inferred", "region", "search_summary", "Radar cannot resolve the uppermost 15-20 m, so shallow ice can be missed."),
    ("A04", "MARS_ICE", "northern mid-latitudes", "", "", "shallow ice depth range", "0-5", "m", "n/s", "n/a", "n/s", "SWIM composite of orbital datasets", "SWIM (NASA/PSI)", "swim", "reported: shallow ice (0-5 m) extending equatorward to ~30 N in places", "inferred", "region", "primary_fetched", "Consistency score, not a direct drilling result."),
    ("A05", "MARS_ICE", "Mars (generic)", "", "", "surface temperature range", "-153 to +20", "C", "n/a", "extremes", "n/s", "NASA Mars fact page", "NASA Science Mars facts", "mars_facts", "quoted", "observed", "body", "primary_fetched", "Generic Mars property, not an Arcadia value."),
    ("U01", "MARS_MUDVOLC", "Utopia Planitia candidate mounds", "", "", "image scale", "0.304", "m/pixel", "HiRISE 30.4 cm/pixel (objects ~91 cm resolved)", "n/s", "n/a", "HiRISE (MRO)", "NASA photojournal", "mud_utopia", "quoted", "observed", "site", "primary_fetched",
     "Page gives no coordinates or feature sizes; interpretation stated as 'candidate' with lava as a competing explanation."),
    ("U02", "MARS_MUDVOLC", "Acidalia Planitia high-albedo mounds", "", "", "mound abundance", "'enormous numbers' (no count in abstract)", "", "CTX/HiRISE/CRISM", "n/s", "n/a", "CTX, HiRISE, CRISM + regional mapping", "NTRS 20100010305 abstract", "mud_acidalia", "quoted", "inferred", "region", "primary_fetched",
     "Origin interpreted variously as pseudocraters, cinder cones, tuff cones, pingos, ice-disintegration features or mud volcanoes."),
    ("C01", "MARS_CHLORIDE", "southern highlands", "", "", "number of candidate chloride deposits (THEMIS)", "~200", "deposits", "THEMIS", "2008 study", "n/s", "THEMIS spectral analysis", "NASA Odyssey release (2008)", "chloride", "reported ~200 sites; 1-25 km2 each; ~3.5-3.9 billion years", "inferred", "region", "search_summary", "Each deposit is far smaller than a 2.5 degree Earth cell."),
]

COLS = ["id", "target_id", "location", "lat", "lon", "quantity", "value", "units", "spatial_resolution", "observation_period", "uncertainty",
        "instrument_or_method", "dataset_or_publication", "source_url", "extraction_method", "evidence_class", "scope", "retrieval", "retrieved_on", "notes"]


def main():
    rows = []
    for r in R:
        (i, t, loc, lat, lon, q, val, un, res, per, unc, ins, ds, uk, ex, cl, sc, ret, note) = r
        rows.append(dict(zip(COLS, [i, t, loc, lat, lon, q, val, un, res, per, unc, ins, ds, U[uk], ex, cl, sc, ret, RET, note])))
    with open(ROOT / "data/planetary_measurements.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLS)
        w.writeheader()
        w.writerows(rows)
    json.dump(rows, open(ROOT / "data/planetary_measurements.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    from collections import Counter
    print(len(rows), "rows;", dict(Counter(r["scope"] for r in rows)), dict(Counter(r["retrieval"] for r in rows)))


if __name__ == "__main__":
    main()
