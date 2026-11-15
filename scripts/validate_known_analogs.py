"""Validate the scoring engine against known Earth analog sites using the REAL processed grid.

    python scripts/validate_known_analogs.py

For every (analog, target) pair the script scores the whole grid with model.scoring_core.score_grid (target default
weights) and reports the percentile rank of the analog's nearest grid cell among all scored cells. Controls are poor
analogs by construction. AUC = probability a random held-out positive outranks a random control (same targets).

Honest-evaluation rules:
  * The engine, weights and targets were NOT tuned on these sites in this task; nothing is fitted here.
  * Positives are split deterministically (alternating by sorted id) into `tuning` / `heldout`; the headline
    metrics use ONLY `heldout`, so a later round of rule tuning can use `tuning` without contaminating the test.
  * Refuses to run on the synthetic sample grid.
Writes docs/VALIDATION.md and data/validation_results.csv.
"""
import json
import pathlib
import sys

import numpy as np
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from model.scoring_core import score_grid  # noqa: E402

GRID_PATH = ROOT / "data/processed/earth_grid.csv"
MAX_DIST_DEG = 5.0


def nearest(grid, lat, lon):
    d = np.hypot(grid.lat - lat, (grid.lon - lon) * np.cos(np.radians(lat)))
    i = d.idxmin()
    return grid.loc[i], float(d.loc[i])


def auc(pos, neg):
    if not pos or not neg:
        return None
    wins = sum((p > n) + 0.5 * (p == n) for p in pos for n in neg)
    return wins / (len(pos) * len(neg))


def main():
    if not GRID_PATH.exists():
        sys.exit("earth_grid.csv missing: refusing to validate on synthetic data.")
    grid = pd.read_csv(GRID_PATH)
    meta = json.load(open(ROOT / "data/processed/earth_grid_metadata.json", encoding="utf-8"))
    targets = {t["id"]: t for t in json.load(open(ROOT / "data/targets.json", encoding="utf-8"))}
    ka = json.load(open(ROOT / "data/known_analogs.json", encoding="utf-8"))

    scored = {}
    for tid, t in targets.items():
        s = score_grid(grid, t).dropna(subset=["score"])
        scored[tid] = s.set_index("cell_id")

    def pct_rank(tid, cell_id):
        s = scored[tid]
        if cell_id not in s.index:
            return None, None
        v = s.loc[cell_id, "score"]
        return float((s.score < v).mean() + 0.5 * (s.score == v).mean()), float(v)

    pos_sorted = sorted(ka["positives"], key=lambda x: x["id"])
    split = {p["id"]: ("heldout" if i % 2 == 0 else "tuning") for i, p in enumerate(pos_sorted)}
    rows = []
    for p in ka["positives"]:
        cell, dist = nearest(grid, p["lat"], p["lon"])
        for tid in p["targets"]:
            r, v = pct_rank(tid, int(cell.cell_id))
            rows.append({"kind": "positive", "split": split[p["id"]], "site": p["name"], "target": tid, "cell_lat": cell.lat,
                         "cell_lon": cell.lon, "dist_deg": round(dist, 2), "score": v, "percentile": r,
                         "in_grid": dist <= MAX_DIST_DEG})
    target_ids = sorted({t for p in ka["positives"] for t in p["targets"]})
    for c in ka["controls"]:
        cell, dist = nearest(grid, c["lat"], c["lon"])
        for tid in target_ids:
            r, v = pct_rank(tid, int(cell.cell_id))
            rows.append({"kind": "control", "split": "control", "site": c["name"], "target": tid, "cell_lat": cell.lat,
                         "cell_lon": cell.lon, "dist_deg": round(dist, 2), "score": v, "percentile": r, "in_grid": dist <= MAX_DIST_DEG})
    for h in ka["hypotheses_pakistan"]["sites"]:
        cell, dist = nearest(grid, h["lat"], h["lon"])
        for tid in h["targets"]:
            r, v = pct_rank(tid, int(cell.cell_id))
            rows.append({"kind": "hypothesis", "split": "n/a", "site": h["name"], "target": tid, "cell_lat": cell.lat,
                         "cell_lon": cell.lon, "dist_deg": round(dist, 2), "score": v, "percentile": r, "in_grid": dist <= MAX_DIST_DEG})
    df = pd.DataFrame(rows)
    df.to_csv(ROOT / "data/validation_results.csv", index=False)

    def stats(sub, ctrl_sub):
        sub = sub[sub.in_grid & sub.percentile.notna()]
        if sub.empty:
            return None
        ctrl = ctrl_sub[ctrl_sub.target.isin(sub.target.unique()) & ctrl_sub.percentile.notna()]
        return {"n": len(sub), "median_percentile": round(float(sub.percentile.median()), 3),
                "top25_hit_rate": round(float((sub.percentile >= 0.75).mean()), 3),
                "top50_hit_rate": round(float((sub.percentile >= 0.5).mean()), 3),
                "auc_vs_controls": None if auc(list(sub.percentile), list(ctrl.percentile)) is None else round(auc(list(sub.percentile), list(ctrl.percentile)), 3),
                "controls_median_percentile": round(float(ctrl.percentile.median()), 3) if len(ctrl) else None}

    pos = df[df.kind == "positive"]
    ctrl = df[df.kind == "control"]
    held, tune, allp = stats(pos[pos.split == "heldout"], ctrl), stats(pos[pos.split == "tuning"], ctrl), stats(pos, ctrl)

    L = []
    L.append("# ASTRANOVUS validation against known Earth analogs\n")
    L.append(f"*Generated by `scripts/validate_known_analogs.py` on the REAL processed grid (built {meta['built_utc']}). Not synthetic.*\n")
    L.append("## Dataset and method\n")
    L.append(f"- Grid: {meta['grid']['cells']} cells, {meta['grid']['step_deg']} deg spacing, lat {meta['grid']['lat_range'][0]} to {meta['grid']['lat_range'][1]}.")
    L.append(f"- Dimensions with data: {', '.join(d for d, v in meta['coverage_by_dimension'].items() if v > 0)}. Missing: {', '.join(d for d, v in meta['coverage_by_dimension'].items() if v == 0)}.")
    L.append(f"- Temporal coverage of MODIS/GPM-derived dimensions: {', '.join(meta['temporal_coverage']['MODIS_GPM_months'])} .")
    L.append("- Each site is evaluated at its nearest grid cell (2.5 degrees) (far coarser than the site) using generic target weights (no mission profile).")
    L.append("- Metric: percentile of the site's score among all scored cells for the mapped target; AUC against 6 control regions.")
    L.append("- No rule or weight was tuned on these sites. Positives were split into `tuning` and `heldout` (alternating by id); the headline uses `heldout` only.")
    L.append("- Target-to-site mapping is an ASTRANOVUS judgement. Controls are poor analogs by construction (no citation).\n")
    L.append("## Summary\n")
    L.append("| subset | n pairs | median percentile | top-25% hit rate | top-50% hit rate | AUC vs controls | controls median pct |")
    L.append("|---|---|---|---|---|---|---|")
    for nm, s in [("**held-out positives (headline)**", held), ("tuning positives", tune), ("all positives", allp)]:
        if s:
            L.append(f"| {nm} | {s['n']} | {s['median_percentile']} | {s['top25_hit_rate']} | {s['top50_hit_rate']} | {s['auc_vs_controls']} | {s['controls_median_percentile']} |")
    L.append("\nSmall sample (a handful of sites): these numbers are indicative, not statistically strong.\n")
    L.append("## Per-site results\n")
    L.append("| kind | split | site | target | nearest cell | dist (deg) | score | percentile |")
    L.append("|---|---|---|---|---|---|---|---|")
    for r in df.sort_values(["kind", "site", "target"]).itertuples():
        pc = "n/a" if r.percentile is None or pd.isna(r.percentile) else f"{r.percentile:.2f}"
        sc = "n/a" if r.score is None or pd.isna(r.score) else f"{r.score:.1f}"
        L.append(f"| {r.kind} | {r.split} | {r.site} | {r.target} | {r.cell_lat},{r.cell_lon} | {r.dist_deg} | {sc} | {pc} |")
    L.append("\n## Pakistani hypotheses (NOT validation)\n")
    L.append("Reported for transparency. No NASA analog citation was retrieved for these sites; cells are too coarse to resolve them; treat as hypotheses.\n")
    L.append("## Unverified candidates excluded\n")
    for e in ka["_meta"]["excluded_unverified"]:
        L.append(f"- {e['name']}: {e['reason']}")
    L.append("\n## Interpretation and limits\n")
    L.append("- Rock (D5) is missing and terrain (D4) is only 1-km relief (absent south of 60S), so volcanic and lava-tube analogs cannot be separated by the dimensions that define them; their weaker scores reflect missing data, not necessarily a poor analog.")
    L.append("- Low-latitude desert targets are driven by dryness and barrenness; polar targets by cold and the snow proxy.")
    L.append("- Anything below the control median for its target should be investigated before claiming the method works for that target.")
    json.dump({"grid_built_utc": meta["built_utc"], "heldout": held, "tuning": tune, "all": allp,
               "temporal_coverage": meta["temporal_coverage"]["MODIS_GPM_months"],
               "dimensions_missing": [d for d, v in meta["coverage_by_dimension"].items() if v == 0],
               "rows": json.loads(df[df.kind != "hypothesis"].to_json(orient="records")),
               "hypotheses": json.loads(df[df.kind == "hypothesis"].to_json(orient="records")),
               "note": "Small sample; controls are easy by construction; Kilauea and Iceland fall outside the grid land cells (>5 deg) and are excluded."},
              open(ROOT / "data/validation_summary.json", "w", encoding="utf-8"), indent=1)
    (ROOT / "docs/VALIDATION.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print(json.dumps({"heldout": held, "tuning": tune, "all": allp}, indent=1))
    print(df[df.kind != "control"][["kind", "site", "target", "score", "percentile", "dist_deg"]].to_string())


if __name__ == "__main__":
    main()
