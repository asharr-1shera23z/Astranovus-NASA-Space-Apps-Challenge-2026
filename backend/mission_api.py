"""Mission / experiment layer on top of the existing scientific engine.

Nothing here scores anything itself. Scoring, gating and region clustering are done by
model.recommend.recommend() and model.scoring_core (unchanged). This module only
  1. maps user-facing experiments (data/experiments.json) onto the existing mission profiles
     in data/purposes.json (plus optional, clearly flagged draft multiplier overrides),
  2. reports honestly which dimensions the loaded Earth grid actually has, and
  3. enriches the engine's regions with per-dimension detail, labels and caveats for the UI.
"""
from __future__ import annotations

import json
import pathlib

import numpy as np
import pandas as pd
from fastapi import APIRouter, HTTPException

from model.recommend import apply_purpose, recommend as _recommend
from model.scoring_core import explain_cell

from .geo_labels import label_for

# Below this share of (purpose-weighted) target weight that has ANY data in the grid, we refuse
# to present a ranking by default. Documented in docs/DATA_CONTRACT.md section 7.
# Share of passing cells (best first) turned into regions. 60% (engine default is 15%) so one huge high-scoring
# area such as the Antarctic plateau cannot crowd every other candidate region out of the list.
TOP_PCT = 0.60
MIN_RESULT_COVERAGE = 0.5

# What we know about how each dimension is built (see scripts/fetch_power_grid.py).
# "missing" is never taken from this table - it is computed from the loaded grid.
_PROVENANCE: dict[str, tuple[str, str]] = {
    "D1_cold": ("derived", "NASA POWER T2M annual-mean 2 m air temperature, percentile-ranked (colder = higher). Air temperature, not land-surface temperature."),
    "D2_aridity": ("derived", "NASA POWER PRECTOTCORR annual precipitation, percentile-ranked (drier = higher)."),
    "D6_ice": ("proxy", "PROXY: share of months with NASA POWER mean air temperature below 0 C. This is not a snow or ice measurement."),
    "D7_polar_light": ("derived", "NASA POWER ALLSKY_SFC_SW_DWN seasonal swing in surface solar irradiance, percentile-ranked."),
    "D8_thermal_swing": ("derived", "NASA POWER T2M_MAX minus T2M_MIN annual air-temperature range, percentile-ranked."),
}

LIMITS_ON_EARTH = {
    "moon": [
        "Gravity: Earth is about 6x the Moon's surface gravity.",
        "Atmosphere: the Moon has essentially none; every Earth site has air, weather and humidity.",
        "Radiation: Earth's atmosphere and magnetic field shield sites from the radiation a lunar surface receives.",
        "Dust and regolith: Earth soils are weathered and moist; lunar regolith is sharp, dry and electrostatically charged.",
    ],
    "mars": [
        "Gravity: Earth is about 2.6x Mars' surface gravity.",
        "Atmosphere: Mars' surface pressure is about 6 mbar (roughly 0.6% of Earth's) and mostly CO2.",
        "Radiation: Mars' thin atmosphere gives far less UV and cosmic-ray shielding than Earth.",
        "Chemistry and biology: Earth sites are shaped by liquid water and life in ways Mars is not.",
    ],
}

DISCLAIMER = (
    "ASTRANOVUS scores are team-generated, purpose-specific similarity estimates computed from percentile "
    "ranks of public Earth-observation data. They are not official NASA ratings, landing-site "
    "certifications or proof that an Earth site reproduces lunar or Martian gravity, atmosphere or radiation."
)


def _py(o):
    """Recursively convert numpy/pandas scalars to plain Python so FastAPI can serialise them."""
    if isinstance(o, dict):
        return {str(k): _py(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_py(v) for v in o]
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, np.floating):
        return None if np.isnan(o) else float(o)
    if isinstance(o, float) and np.isnan(o):
        return None
    if isinstance(o, np.bool_):
        return bool(o)
    return o


def _terrain(e):
    """SRTM stage-2 verification for a region's best cell (None-safe, never fabricated)."""
    if e is None:
        return {"state": "not_checked", "note": "SRTM terrain was only computed for the top candidate regions; this region has not been checked."}
    if not e.get("covered"):
        return {"state": "outside_coverage", "note": "Outside SRTM coverage (60N to 56S): terrain NOT verified."}
    keys = ("terrain_class", "slope_mean_deg", "slope_p95_deg", "relief_m", "roughness_std_m", "elevation_mean_m", "note")
    return {"state": "verified_local", **{k: e.get(k) for k in keys}}


def create_router(grid: pd.DataFrame, targets: dict, dimensions: list, purposes: dict,
                  root: pathlib.Path, grid_is_sample: bool, grid_name: str) -> APIRouter:
    router = APIRouter()
    meta = json.load(open(root / "data/experiments.json", encoding="utf-8"))
    sources = meta["_meta"]["sources"]
    experiments = {e["id"]: e for e in meta["experiments"]}
    dim_meta = {d["id"]: d for d in dimensions}
    ev_path = root / "data/target_evidence_summary.json"
    evidence = json.load(open(ev_path, encoding="utf-8")) if ev_path.exists() else {"targets": {}}
    s2_path = root / "data/processed/stage2.json"
    stage2 = {}
    if s2_path.exists():
        for e in json.load(open(s2_path, encoding="utf-8")):
            stage2[(e["lat"], e["lon"])] = e
    meta_path = root / "data/processed/earth_grid_metadata.json"
    grid_meta = None
    if meta_path.exists() and not grid_is_sample:
        grid_meta = json.load(open(meta_path, encoding="utf-8"))

    def dim_kind(did: str) -> tuple[str, str, str]:
        """(status, provenance, temporal) from the build metadata when present, else the static table."""
        gm = (grid_meta or {}).get("dimensions", {}).get(did)
        if gm and gm.get("status") != "missing":
            return gm["status"], gm["source"], gm.get("temporal", "")
        if did in _PROVENANCE:
            return _PROVENANCE[did][0], _PROVENANCE[did][1], ""
        return "derived", f"Populated in the loaded grid; intended source per dimensions.json: {dim_meta.get(did, {}).get('earth_source', 'n/a')} (verify pipeline).", ""

    # ---- data status -------------------------------------------------------------------
    def dim_has_data(dim: str) -> bool:
        return dim in grid.columns and bool(grid[dim].notna().any())

    def data_status() -> dict:
        lats = np.sort(grid.lat.unique())
        step = float(np.min(np.diff(lats))) if len(lats) > 1 else None
        dims = []
        for d in dimensions:
            did = d["id"]
            frac = float(grid[did].notna().mean()) if did in grid.columns else 0.0
            if frac == 0.0:
                status = "missing"
                prov = f"No data in the loaded grid yet. Intended source: {d.get('earth_source', 'n/a')}."
                temporal = ""
            else:
                status, prov, temporal = dim_kind(did)
            dims.append({"id": did, "name": d["name"], "description": d.get("description", ""),
                         "status": status, "cell_coverage": round(frac, 3), "provenance": prov, "temporal": temporal,
                         "intended_earth_source": d.get("earth_source", ""),
                         "planetary_source": d.get("target_source", "")})
        return {
            "grid": {"file": grid_name, "is_synthetic_sample": grid_is_sample, "cells": int(len(grid)),
                     "step_deg": step,
                     "lat_range": [float(grid.lat.min()), float(grid.lat.max())]},
            "dimensions": dims,
            "n_dimensions_with_data": sum(1 for x in dims if x["status"] != "missing"),
            "n_dimensions": len(dims),
            "values_are": "percentile ranks (0-1) among the loaded land cells, not raw physical units",
            "build": ({"built_utc": grid_meta["built_utc"], "temporal_coverage": grid_meta["temporal_coverage"],
                       "products": {k: v.get("version", v.get("source")) for k, v in grid_meta["products"].items()},
                       "cross_checks": grid_meta.get("cross_checks", {})} if grid_meta else None),
            "disclaimer": DISCLAIMER,
        }

    # ---- experiment -> engine inputs ---------------------------------------------------
    def parse_weights(raw: str | None) -> dict:
        """'D1_cold:1.5,D2_aridity:0' -> {dim: factor}. Factors 0-3 multiply the profile's weights (user tuning)."""
        out: dict = {}
        if not raw:
            return out
        for part in raw.split(","):
            try:
                k, v = part.split(":")
                v = float(v)
            except ValueError:
                raise HTTPException(422, f"bad weights entry {part!r}; use DIM:factor,DIM:factor")
            if k not in dim_meta or not 0 <= v <= 3:
                raise HTTPException(422, f"weight {part!r}: unknown dimension or factor outside 0-3")
            out[k] = v
        return out

    def effective_purpose(exp: dict, custom: dict | None = None) -> dict:
        pu = purposes[exp["purpose_id"]]
        mult = dict(pu.get("multipliers", {}))
        for dim, m in exp.get("multiplier_overrides", {}).items():
            mult[dim] = mult.get(dim, 1.0) * m
        for dim, m in (custom or {}).items():
            mult[dim] = mult.get(dim, 1.0) * m
        gates = list(pu.get("gates", [])) + list(exp.get("extra_gates", []))
        return {**pu, "multipliers": mult, "gates": gates}

    def allowed_target_ids(exp: dict) -> list[str]:
        pu = purposes[exp["purpose_id"]]
        return [t for t in pu["targets"] if t in targets and targets[t]["body"] == exp["body"]]

    def assess(exp: dict, target: dict, custom: dict | None = None) -> dict:
        pu = effective_purpose(exp, custom)
        eff = apply_purpose(target, pu)
        total = have = 0.0
        missing, proxies = [], []
        for dim, r in eff["rules"].items():
            w = float(r["weight"])
            if w <= 0:
                continue
            total += w
            if dim_has_data(dim):
                have += w
                if dim_kind(dim)[0] == "proxy":
                    proxies.append(dim)
            else:
                missing.append(dim)
        gate_missing = [g for g in pu.get("gates", []) if not dim_has_data(g["dim"])]
        max_cov = (have / total) if total else 0.0
        if gate_missing or max_cov < MIN_RESULT_COVERAGE:
            state = "unavailable"
        elif missing or proxies:
            state = "partial"
        else:
            state = "ready"
        notes = []
        for g in gate_missing:
            notes.append(f"Required check not possible yet: {dim_meta.get(g['dim'], {}).get('name', g['dim'])} has no data ({g['why']}).")
        if not gate_missing and max_cov < MIN_RESULT_COVERAGE:
            notes.append(f"Only {max_cov:.0%} of this mission/site's weighted criteria have data (minimum {MIN_RESULT_COVERAGE:.0%}).")
        for d in proxies:
            notes.append(f"{dim_meta.get(d, {}).get('name', d)} is a proxy, not a direct measurement.")
        return {"state": state, "max_coverage": round(max_cov, 3),
                "missing_dimensions": missing, "proxy_dimensions": proxies,
                "gate_dimensions_missing": [g["dim"] for g in gate_missing], "notes": notes}

    def target_card(t: dict, exp: dict) -> dict:
        card = {k: v for k, v in t.items() if k != "rules"}
        card["rules"] = t["rules"]
        card["is_draft"] = "draft" in str(t.get("_note", "")).lower()
        card["evidence"] = evidence["targets"].get(t["id"], {"grounded": 0, "total": len(t["rules"])})
        card["readiness"] = assess(exp, t)
        return card

    def resolve_sources(exp: dict) -> list[dict]:
        return [{"id": sid, **sources[sid]} for sid in exp["nasa_documented"]["sources"]]

    def experiment_view(exp: dict) -> dict:
        pu = effective_purpose(exp)
        allowed = allowed_target_ids(exp)
        out = {k: v for k, v in exp.items()}
        out["nasa_documented"] = {**exp["nasa_documented"], "sources": resolve_sources(exp)}
        out["purpose"] = {"id": pu["id"], "name": pu["name"], "question": pu["question"],
                          "nasa_basis": pu["nasa_basis"], "multipliers": pu["multipliers"], "gates": pu["gates"]}
        out["allowed_targets"] = [target_card(targets[t], exp) for t in allowed]
        out["default_target"] = allowed[0] if allowed else None
        out["key_dimensions"] = sorted(pu["multipliers"], key=lambda d: -pu["multipliers"][d])
        return out

    # ---- endpoints ---------------------------------------------------------------------
    @router.get("/experiments")
    def list_experiments(body: str | None = None):
        items = [experiment_view(e) for e in experiments.values() if body is None or e["body"] == body]
        info = meta["_meta"]
        return _py({"notice": info["notice"], "classification": info["classification"],
                    "sources_verified_on": info["sources_verified_on"], "experiments": items})

    @router.get("/validation")
    def get_validation():
        p = root / "data/validation_summary.json"
        if not p.exists():
            return {"available": False, "note": "Validation has not been run on the real grid (python scripts/validate_known_analogs.py)."}
        return {"available": True, **json.load(open(p, encoding="utf-8"))}

    @router.get("/data_status")
    def get_data_status():
        return _py(data_status())

    @router.get("/mission/recommend")
    def mission_recommend(experiment: str, target: str | None = None, min_coverage: float = 0.4,
                          top: int = 10, allow_unverified: bool = False, weights: str | None = None):
        if experiment not in experiments:
            raise HTTPException(404, f"unknown experiment {experiment}")
        exp = experiments[experiment]
        allowed = allowed_target_ids(exp)
        if not allowed:
            raise HTTPException(422, f"experiment {experiment} has no compatible {exp['body']} targets")
        tid = target or allowed[0]
        if tid not in allowed:
            raise HTTPException(422, f"target {tid} not valid for this experiment; use one of {allowed}")
        t = targets[tid]
        custom = parse_weights(weights)
        pu = effective_purpose(exp, custom)
        eff = apply_purpose(t, pu)
        assessment = assess(exp, t, custom)
        status = data_status()
        status_by_id = {d["id"]: d for d in status["dimensions"]}

        base = {
            "experiment": {k: v for k, v in experiment_view(exp).items() if k != "allowed_targets"},
            "target_info": target_card(t, exp),
            "allowed_targets": [target_card(targets[x], exp) for x in allowed],
            "assessment": assessment,
            "data_state": assessment["state"],
            "provisional": False,
            "custom_weights": custom,
            "grid": status["grid"],
            "dimension_status": status["dimensions"],
            "limits_on_earth": LIMITS_ON_EARTH[exp["body"]] + exp.get("cannot_reproduce", []),
            "disclaimer": DISCLAIMER,
        }

        if assessment["state"] == "unavailable" and not allow_unverified:
            return _py({**base, "regions": [], "n_cells_passed": 0, "weights_used": {}})

        out = _recommend(grid, t, pu, dimensions, min_coverage=min_coverage, top_regions=top, top_pct=TOP_PCT)
        base["provisional"] = assessment["state"] == "unavailable"
        regions = []
        for r in out.get("regions", []):
            lat, lon = r["best_cell"]["lat"], r["best_cell"]["lon"]
            hit = grid[(grid.lat == lat) & (grid.lon == lon)]
            dims = []
            if len(hit):
                for row in explain_cell(hit.iloc[0], eff):
                    if float(row["weight"]) <= 0:
                        continue
                    st = status_by_id.get(row["dimension"], {})
                    dims.append({**row, "name": dim_meta.get(row["dimension"], {}).get("name", row["dimension"]),
                                 "data_status": "missing" if row["percentile"] is None else st.get("status", "derived"),
                                 "temporal": st.get("temporal", ""),
                                 "source": st.get("provenance", "")})
            # The engine's lat/lon is the CENTROID of the merged cells, which can lie far from the best cell for wide
            # belts. Show the best cell (the place the score, terrain check and label all refer to); keep the centroid.
            lab = label_for(lat, lon)
            regions.append({**r, "centroid": {"lat": r["lat"], "lon": r["lon"]}, "lat": lat, "lon": lon,
                            "id": f"R{r['rank']}", "location_label": lab["label"],
                            "region_name": lab["region_name"], "label_basis": lab["basis"],
                            "dimensions": dims, "applications": exp["applications"],
                            "terrain": _terrain(stage2.get((lat, lon)))})
        base["regions"] = regions
        base["n_cells_passed"] = out.get("n_cells_passed", 0)
        base["weights_used"] = out.get("weights_used", {})
        return _py(base)

    return router
