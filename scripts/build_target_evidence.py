"""Generate data/target_evidence.csv and data/target_evidence_summary.json from data/targets.json.

Every rule of every target gets one worksheet row. A row is marked `supported` ONLY when a source that was
actually retrieved (2026-11-15) states something consistent with the rule's DIRECTION. Quantities are copied as
quoted by the source (qualitative / literature values), never invented. Everything else stays `unverified`.
Targets.json is NOT modified: weight/rule changes need explicit evidence AND team approval (see docs/TARGET_EVIDENCE.md).

    python scripts/build_target_evidence.py
"""
import csv
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]

S = {
    "diviner_sci": "https://www.diviner.ucla.edu/science",
    "diviner_ice": "https://www.diviner.ucla.edu/single-post/diviner-data-used-to-map-the-stability-of-ices-at-the-lunar-poles",
    "lro_2009": "https://www3.nasa.gov/home/hqnews/2009/sep/HQ_09-215_LRO_First_Light.html",
    "artemis": "https://www.nasa.gov/news-release/nasa-identifies-candidate-regions-for-landing-next-americans-on-moon/",
    "pits": "https://www.nasa.gov/solar-system/nasas-lro-finds-lunar-pits-harbor-comfortable-temperatures/",
    "pits_cave": "https://science.nasa.gov/solar-system/new-evidence-adds-to-findings-hinting-at-network-of-caves-on-moon/",
    "swim": "https://science.nasa.gov/resource/swim-map-shows-subsurface-water-ice-on-mars/",
    "swim_psi": "https://swim.psi.edu/",
    "jezero_kit": "https://www.jpl.nasa.gov/news/press_kits/mars_2020/launch/mission/landing_site/",
    "jezero_lake": "https://www.jpl.nasa.gov/news/nasas-perseverance-rover-deciphers-ancient-history-of-martian-lake/",
    "perseverance": "https://science.nasa.gov/mission/mars-2020-perseverance/science-objectives/",
}

# (target, dimension) -> (status, value_found, [source keys], note)
EVIDENCE = {
    ("MOON_PSR", "D1_cold"): ("supported", "Diviner: PSR temperatures as low as ~25 K (UCLA Diviner); 40-110 K range cited for water-ice trapping; early NASA release: ~33 K", ["diviner_sci", "lro_2009"], "Direction (colder = more Moon-like) supported."),
    ("MOON_PSR", "D6_ice"): ("supported", "Large increase in water-ice-like features at temperatures <110 K; cold-trapping area for water ice ~17,000 km2 (Diviner-based study)", ["diviner_ice", "diviner_sci"], "Direction supported. Earth proxy is snow cover, not ground ice."),
    ("MOON_PSR", "D7_polar_light"): ("unverified", "", [], "AMBIGUOUS: a PSR never receives sunlight, while D7 (Earth seasonal insolation swing) rewards LARGE light variation. Direction not justified; review before relying on this weight."),
    ("MOON_SP_RIDGE", "D7_polar_light"): ("supported", "NASA: all 13 candidate regions near the south pole contain sites with continuous sunlight for a 6.5-day period", ["artemis"], "Supports 'extreme/near-continuous light' direction qualitatively; Earth latitude is only a proxy."),
    ("MOON_SP_RIDGE", "D1_cold"): ("unverified", "", [], "Ridge itself is sunlit; cold applies to neighbouring PSRs (Diviner). Not verified for the ridge."),
    ("MOON_LAVATUBE", "D5_rock"): ("supported", "NASA/LRO: pits in the maria; Mare Tranquillitatis pit ~100 m deep, probable collapsed lava tube; 16 of >200 known pits probably collapsed lava tubes", ["pits", "pits_cave"], "Basaltic mare setting supports 'rock/volcanic' direction qualitatively."),
    ("MOON_LAVATUBE", "D8_thermal_swing"): ("unverified", "", [], "NASA reports pit interiors stay near 17 C (stable), i.e. LOW swing inside. A 'high swing' rule applies to the surface only; rule intent unclear."),
    ("MARS_ICE", "D6_ice"): ("supported", "SWIM: shallow subsurface ice (0-5 m) mapped equatorward to ~30N in places; Arcadia plains and Deuteronilus Mensae match the most ice criteria", ["swim", "swim_psi"], "Direction supported."),
    ("MARS_ICE", "D4_terrain"): ("supported", "SWIM: broad plains of Arcadia match the greatest number of remote-sensing ice criteria", ["swim", "swim_psi"], "Supports 'low relief plains' qualitatively; no slope value retrieved."),
    ("MARS_JEZERO", "D5_rock"): ("supported", "NASA/JPL: ancient lake and delta deposits; parts of Jezero rich in carbonates; delta sediments", ["jezero_kit", "jezero_lake"], "Direction supported qualitatively."),
    ("MARS_JEZERO", "D2_aridity"): ("supported", "NASA: water once formed a lake/delta in Jezero before Mars dried up; present surface is dry", ["jezero_kit"], "Direction supported."),
    ("MARS_JEZERO", "D4_terrain"): ("supported", "Jezero is a ~45 km impact crater with a delta (steep scarps) inside; moderate-to-high local relief", ["jezero_kit", "jezero_lake"], "Supports non-flat terrain qualitatively; band limits (0.3-0.7) remain a team draft."),
}

WHERE = {
    "D1_cold": "Moon: LRO Diviner (diviner.ucla.edu); Mars: MGS/MRO thermal data via Mars Trek",
    "D2_aridity": "Literature / orbital hydrology context",
    "D3_barren": "Orbital imagery (LROC QuickMap / Mars Trek CTX)",
    "D4_terrain": "Moon: LRO LOLA via Moon Trek; Mars: MGS MOLA via Mars Trek",
    "D5_rock": "Moon: LROC/Kaguya mare units; Mars: CRISM / USGS geologic maps",
    "D6_ice": "Moon: Diviner cold traps / LAMP; Mars: SWIM (swim.psi.edu)",
    "D7_polar_light": "Moon: LOLA illumination maps; Mars: seasonal insolation (literature)",
    "D8_thermal_swing": "Moon: Diviner day/night temperatures; Mars: thermal inertia / TES",
}


def main():
    targets = json.load(open(ROOT / "data/targets.json", encoding="utf-8"))
    rows, summary = [], {}
    for t in targets:
        total = grounded = 0
        for dim, rule in t["rules"].items():
            ev = EVIDENCE.get((t["id"], dim))
            status, value, keys, note = ev if ev else ("unverified", "", [], "No retrieved source yet.")
            total += 1
            grounded += status == "supported"
            rows.append({
                "target_id": t["id"], "dimension": dim, "rule": rule["rule"], "weight": rule["weight"],
                "where_to_check": WHERE[dim], "status": status, "value_found": value,
                "source_url": " | ".join(S[k] for k in keys), "checked_on": "2026-11-15" if ev else "",
                "notes": note,
            })
        summary[t["id"]] = {"grounded": grounded, "total": total, "status": t.get("status")}
    with open(ROOT / "data/target_evidence.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    json.dump({"rows": len(rows), "supported_rows": sum(r["status"] == "supported" for r in rows),
               "targets": summary,
               "note": "'supported' = a retrieved source states something consistent with the rule direction (qualitative). No weights were changed."},
              open(ROOT / "data/target_evidence_summary.json", "w", encoding="utf-8"), indent=2)
    print({k: f"{v['grounded']}/{v['total']}" for k, v in summary.items()})


if __name__ == "__main__":
    main()
