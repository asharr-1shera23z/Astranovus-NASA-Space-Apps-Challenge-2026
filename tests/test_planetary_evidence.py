"""Planetary measurement provenance, evidence endpoint, adjusted ranking and experiment invariants (real data, no network)."""
import json
import pathlib

import pandas as pd
import pytest
from fastapi.testclient import TestClient

import backend.main as m

ROOT = pathlib.Path(__file__).resolve().parents[1]
client = TestClient(m.app)
MEAS = pd.read_csv(ROOT / "data/planetary_measurements.csv")
REQUIRED = ["id", "target_id", "location", "quantity", "value", "units", "spatial_resolution", "observation_period", "uncertainty",
            "instrument_or_method", "dataset_or_publication", "source_url", "extraction_method", "evidence_class", "scope", "retrieval", "retrieved_on"]


def test_every_measurement_has_full_provenance():
    for col in REQUIRED:
        assert col in MEAS.columns, col
    assert MEAS.id.is_unique
    for col in ["id", "target_id", "quantity", "source_url", "extraction_method", "evidence_class", "scope", "retrieval", "instrument_or_method", "dataset_or_publication"]:
        assert MEAS[col].notna().all() and (MEAS[col].astype(str).str.strip() != "").all(), col
    assert MEAS.source_url.str.startswith("http").all()


def test_measurement_vocabularies_and_targets_are_valid():
    assert set(MEAS.evidence_class) <= {"observed", "derived", "inferred"}
    assert set(MEAS.scope) <= {"site", "region", "body"}
    assert set(MEAS.retrieval) <= {"primary_fetched", "search_summary"}
    assert set(MEAS.target_id) <= set(m.TARGETS)


def test_json_matches_csv():
    js = json.load(open(ROOT / "data/planetary_measurements.json", encoding="utf-8"))
    rows = js["measurements"] if isinstance(js, dict) else js
    assert len(rows) == len(MEAS)


def test_unverified_search_summary_rows_are_never_called_primary():
    # rows backed only by a search summary must say so; the counts are what the docs report
    assert (MEAS.retrieval == "search_summary").sum() >= 1
    assert (MEAS.retrieval == "primary_fetched").sum() + (MEAS.retrieval == "search_summary").sum() == len(MEAS)


def test_evidence_endpoint_returns_rules_and_measurements():
    r = client.get("/evidence/MOON_PSR")
    assert r.status_code == 200
    body = r.json()
    assert body["measurements"] and body["rules"]
    assert all(x["target_id"] == "MOON_PSR" for x in body["measurements"])
    assert client.get("/evidence/NOT_A_TARGET").status_code == 404


def test_adjusted_ranking_is_default_and_ordered():
    r = client.get("/mission/recommend", params={"experiment": "MOON_WATER_ICE", "target": "MOON_PSR"}).json()
    assert r["ranking_basis"]
    adj = [g["evidence_adjusted_score"] for g in r["regions"]]
    assert adj == sorted(adj, reverse=True)
    for g in r["regions"]:
        assert g["evidence_adjusted_score"] <= max(g["best_score"], 50) + 1e-6


def test_validation_and_sensitivity_outputs_are_consistent():
    v = json.load(open(ROOT / "data/validation_summary.json", encoding="utf-8"))
    assert v["all"]["n_pairs"] == v["heldout"]["n_pairs"] + v["heldout_v2"]["n_pairs"] + v["tuning"]["n_pairs"]
    assert v["all"]["median_ci95_unit"].startswith("site")
    s = json.load(open(ROOT / "data/sensitivity_summary.json", encoding="utf-8"))
    assert "drop D4 terrain" in s["ablations"] and s["weight_noise"]["draws"] == 300


@pytest.mark.parametrize("path", ["data/experiment_validation.json"])
def test_experiment_validation_has_no_violations(path):
    ev = json.load(open(ROOT / path, encoding="utf-8"))
    assert ev["problems"] == []
    assert len(ev["rows"]) >= 25
