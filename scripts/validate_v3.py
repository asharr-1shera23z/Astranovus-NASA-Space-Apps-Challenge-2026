"""Validation v3: grouped, cohort-separated evaluation of the scoring variants.

    python scripts/validate_v3.py              # development stage: cohorts A and B only  -> data/validation_v3_dev.json
    python scripts/validate_v3.py --final      # additionally scores the frozen cohort C   -> data/validation_v3_final.json

Rules enforced here
  * The frozen cohort file must match its recorded hash (membership cannot drift after freezing).
  * Cohort C is scored ONLY with --final, once per variant, for disclosure. Variant choice is never based on C.
  * Positives are the pairs of eligible sites (primary analysis); exploratory pairs are reported separately.
  * Percentile = rank of the site's nearest-cell score among all scored cells for that target (generic target rules, no
    mission profile). Site-cluster bootstrap for intervals; metrics flagged unreliable when sites < 5.
  * Controls: target-scoped; every control carries a written, model-blind rationale in the dataset.
"""
import copy
import hashlib
import json
import pathlib
import sys

import numpy as np
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
from model.scoring_core import score_grid  # noqa: E402
from validate_known_analogs import auc, boot_ci, nearest  # noqa: E402

PAIR_EXPLORATORY = {("qaidam_dalangtan", "MARS_AEOLIAN")}  # yardangs are erosional, not dunes: partial relationship
MAX_DIST = {"A_historical": 5.0, "B_development": 3.5, "C_frozen_independent": 3.5}
MIN_SITES_RELIABLE = 5


def variants(targets):
    def mod(fn):
        out = copy.deepcopy(targets)
        for t in out.values():
            for dim, r in t["rules"].items():
                fn(dim, r)
        return out
    return {
        "raw": (targets, "score", None, False),
        "adjusted_50": (targets, "score_adj", None, False),
        "adjusted_target_median": (targets, "score_adj_med", None, False),
        "raw_mincov60": (targets, "score", 0.6, False),
        "equal_raw": (mod(lambda d, r: r.update(weight=1) if r["weight"] > 0 else None), "score", None, False),
        "equal_adjusted_50": (mod(lambda d, r: r.update(weight=1) if r["weight"] > 0 else None), "score_adj", None, False),
        "adjusted_50_drop_D4": (mod(lambda d, r: r.update(weight=0) if d == "D4_terrain" else None), "score_adj", None, False),
        "adjusted_50_exposed_surface": (targets, "score_adj", None, True),
        "raw_exposed_surface": (targets, "score", None, True),
        "exposed_adj_equal_weights": (mod(lambda d, r: r.update(weight=1) if r["weight"] > 0 else None), "score_adj", None, True),
        "exposed_adj_drop_proxies_D5_D6_D7": (mod(lambda d, r: r.update(weight=0) if d in ("D5_rock", "D6_ice", "D7_polar_light") else None), "score_adj", None, True),
        **{f"exposed_adj_drop_{dim}": (mod(lambda d, r, dim=dim: r.update(weight=0) if d == dim else None), "score_adj", None, True)
           for dim in ("D1_cold", "D2_aridity", "D3_barren", "D4_terrain", "D5_rock", "D6_ice", "D8_thermal_swing")},
    }


def pool_for(grid, tgt, col, restrict=False, readiness=None):
    g = grid
    if restrict and readiness["targets"].get(tgt["id"], {}).get("requires_exposed_surface"):
        g = grid[grid["D3_barren"].notna()]
    s = score_grid(g, tgt).dropna(subset=["score"]).set_index("cell_id")
    med = float(s.score.median())
    s["score_adj_med"] = s.coverage * s.score + (1 - s.coverage) * med
    return s


def pct(pool, col, cell_id, mincov):
    p = pool if mincov is None else pool[pool.coverage >= mincov]
    if cell_id not in p.index:
        return None
    v = p.loc[cell_id, col]
    return float((p[col] < v).mean() + 0.5 * (p[col] == v).mean())


def metrics(pos, ctrl):
    out = {"n_pairs": int(len(pos)), "n_sites": int(pos.site_id.nunique())}
    if not len(pos):
        return out
    pv = pos.percentile.to_numpy()
    out.update(median_percentile=round(float(np.median(pv)), 3), top10_hit=round(float((pv >= 0.9).mean()), 3), top25_hit=round(float((pv >= 0.75).mean()), 3),
               median_ci95_site_cluster=boot_ci(pv, np.median, groups=pos.site_id.to_numpy()), reliable=bool(pos.site_id.nunique() >= MIN_SITES_RELIABLE))
    aucs_all, aucs_hard = [], []
    for t in pos.target.unique():
        p = pos[pos.target == t].percentile.to_numpy()
        n_all = ctrl[ctrl.target == t].percentile.dropna().to_numpy()
        n_hard = ctrl[(ctrl.target == t) & ctrl.hard].percentile.dropna().to_numpy()
        a, h = auc(p, n_all), auc(p, n_hard)
        if a is not None:
            aucs_all.append(a)
        if h is not None:
            aucs_hard.append(h)
    out["auc_vs_all_controls_by_target"] = round(float(np.mean(aucs_all)), 3) if aucs_all else None
    out["auc_vs_hard_controls_by_target"] = round(float(np.mean(aucs_hard)), 3) if aucs_hard else None
    out["n_targets_with_hard_control"] = len(aucs_hard)
    return out


def main():
    final = "--final" in sys.argv
    ds = json.load(open(ROOT / "data/analog_dataset_v3.json", encoding="utf-8"))
    fz = json.load(open(ROOT / "data/analog_cohorts_v3_frozen.json", encoding="utf-8"))
    chk = hashlib.sha256(json.dumps([fz["C_members"], fz["B_members"]]).encode()).hexdigest()
    assert chk == fz["sha256"], "frozen cohort membership changed after freezing"
    members_now = {"C": sorted([s["site_id"] for s in ds["sites"] if s["cohort"] == "C_frozen_independent"] + ["ctl:" + c["site_id"] for c in ds["controls"] if c["cohort"] == "C_frozen_independent"])}
    assert members_now["C"] == fz["C_members"], "dataset cohort C differs from the frozen list"

    grid = pd.read_csv(ROOT / "data/processed/earth_grid.csv")
    targets = {t["id"]: t for t in json.load(open(ROOT / "data/targets.json", encoding="utf-8"))}
    cohorts = ["A_historical", "B_development"] + (["C_frozen_independent"] if final else [])

    rows_pos, rows_ctl = [], []
    for s in ds["sites"]:
        if s["cohort"] not in cohorts or s["validation_eligibility"] not in ("eligible", "eligible_historical", "exploratory"):
            continue
        cell, d = nearest(grid, s["lat"], s["lon"])
        for pr in s["pairs"]:
            if pr["target"] not in targets:
                continue
            exploratory = s["validation_eligibility"] == "exploratory" or (s["site_id"], pr["target"]) in PAIR_EXPLORATORY
            rows_pos.append(dict(site_id=s["site_id"], cohort=s["cohort"], target=pr["target"], cell_id=int(cell.cell_id), dist=d, in_grid=d <= MAX_DIST[s["cohort"]],
                                 exploratory=exploratory, strength=s["support_strength"], analog_types=",".join(pr["analog_types"])))
    for c in ds["controls"]:
        if c["cohort"] not in cohorts:
            continue
        cell, d = nearest(grid, c["lat"], c["lon"])
        tg = list(targets) if c["targets"] == "all" else c["targets"]
        for t in tg:
            if t in targets:
                rows_ctl.append(dict(site_id=c["site_id"], cohort=c["cohort"], target=t, cell_id=int(cell.cell_id), dist=d, in_grid=d <= MAX_DIST[c["cohort"]], hard=c["hard"]))
    P, C = pd.DataFrame(rows_pos), pd.DataFrame(rows_ctl)

    res = {"stage": "final" if final else "development", "cohorts_scored": cohorts, "frozen_hash": fz["sha256"], "variants": {}, "excluded_out_of_grid": {}}
    res["excluded_out_of_grid"] = {"positives": P[~P.in_grid][["site_id", "target", "dist"]].round(2).to_dict("records"), "controls": C[~C.in_grid][["site_id", "target", "dist"]].round(2).drop_duplicates().to_dict("records")}
    P, C = P[P.in_grid].copy(), C[C.in_grid].copy()

    readiness = json.load(open(ROOT / "data/target_readiness.json", encoding="utf-8"))
    for vname, (tgs, col, mincov, restrict) in variants(targets).items():
        pools = {t: pool_for(grid, tg, col, restrict, readiness) for t, tg in tgs.items()}
        for D in (P, C):
            D["percentile"] = [pct(pools[r.target], col, r.cell_id, mincov) for r in D.itertuples()]
            D["coverage"] = [float(pools[r.target].loc[r.cell_id, "coverage"]) if r.cell_id in pools[r.target].index else np.nan for r in D.itertuples()]
        Pv, Cv = P[P.percentile.notna()].copy(), C[C.percentile.notna()].copy()
        v = {"unrankable_pairs": int(P.percentile.isna().sum()), "unrankable_controls": int(C.percentile.isna().sum())}
        prim = Pv[~Pv.exploratory]
        sets = {"A": prim[prim.cohort == "A_historical"], "B": prim[prim.cohort == "B_development"], "A+B": prim[prim.cohort != "C_frozen_independent"]}
        if final:
            sets["C"] = prim[prim.cohort == "C_frozen_independent"]
        for k, sub in sets.items():
            v[k] = metrics(sub, Cv[Cv.cohort.isin(sub.cohort.unique())] if k in ("A", "B", "C") else Cv[Cv.cohort != "C_frozen_independent"])
        v["exploratory_pairs"] = metrics(Pv[Pv.exploratory & (Pv.cohort != "C_frozen_independent")], Cv[Cv.cohort != "C_frozen_independent"])
        dev = prim[prim.cohort != "C_frozen_independent"]
        v["by_target_A+B"] = {t: metrics(dev[dev.target == t], Cv[(Cv.cohort != "C_frozen_independent")]) for t in sorted(dev.target.unique())}
        v["by_completeness_A+B"] = {"coverage>=0.9": metrics(dev[dev.coverage >= 0.9], Cv), "coverage<0.9": metrics(dev[dev.coverage < 0.9], Cv)}
        res["variants"][vname] = v
        if final:
            # per-pair listing of the frozen cohort for the report (no selection based on it)
            res.setdefault("frozen_pairs", {})[vname] = Pv[Pv.cohort == "C_frozen_independent"][["site_id", "target", "percentile", "coverage", "exploratory"]].round(3).to_dict("records")
        if vname == "raw":
            res["pairs_raw_dev"] = Pv[Pv.cohort != "C_frozen_independent"][["site_id", "cohort", "target", "percentile", "coverage", "exploratory", "dist"]].round(3).to_dict("records")
            res["controls_raw_dev"] = Cv[Cv.cohort != "C_frozen_independent"][["site_id", "target", "hard", "percentile", "coverage"]].round(3).to_dict("records")

    out = ROOT / ("data/validation_v3_final.json" if final else "data/validation_v3_dev.json")
    json.dump(res, open(out, "w", encoding="utf-8"), indent=1)
    for vn, v in res["variants"].items():
        a = v["A+B"]
        print(f"{vn:26s} A+B n={a['n_pairs']:2d}/{a['n_sites']:2d} med={a.get('median_percentile')} CI={a.get('median_ci95_site_cluster')} top25={a.get('top25_hit')} aucAll={a.get('auc_vs_all_controls_by_target')} aucHard={a.get('auc_vs_hard_controls_by_target')}"
              + (f" | C med={v['C'].get('median_percentile')} n={v['C']['n_pairs']}" if final else ""))
    print("A (baseline repro):", res["variants"]["raw"]["A"].get("median_percentile"), res["variants"]["raw"]["A"]["n_pairs"], "excluded:", res["excluded_out_of_grid"])


if __name__ == "__main__":
    main()
