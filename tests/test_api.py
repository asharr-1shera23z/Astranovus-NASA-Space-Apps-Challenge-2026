"""API integration tests against the REAL processed grid (no network, no server needed)."""
import pytest
from fastapi.testclient import TestClient

import backend.main as m

client = TestClient(m.app)


def test_health_reports_real_grid():
    h = client.get("/health").json()
    assert h["ok"] and h["is_synthetic_sample"] is False and h["cells"] > 100


def test_data_status_matches_grid():
    ds = client.get("/data_status").json()
    by = {d["id"]: d for d in ds["dimensions"]}
    for d, status in by.items():
        has = m.GRID[d].notna().any()
        assert (status["status"] != "missing") == bool(has)
    assert by["D6_ice"]["status"] == "proxy"          # snow cover is a proxy, never labelled as measured ice
    assert by["D5_rock"]["status"] == "missing"       # no defensible lithology data: must stay missing
    assert by["D4_terrain"]["status"] == "derived" and by["D4_terrain"]["cell_coverage"] > 0.5


def test_experiments_only_offer_compatible_targets():
    ex = client.get("/experiments").json()["experiments"]
    assert len(ex) == 12
    for e in ex:
        allowed = set(m.PURPOSES[e["purpose_id"]]["targets"])
        assert e["allowed_targets"] and all(t["id"] in allowed and t["body"] == e["body"] for t in e["allowed_targets"])
        assert e["nasa_documented"]["sources"] and all(s["url"].startswith("https://") for s in e["nasa_documented"]["sources"])


def test_recommend_uses_engine_and_target_changes_results():
    a = client.get("/mission/recommend", params={"experiment": "MARS_GEOLOGY_SAMPLING", "target": "MARS_JEZERO", "top": 5}).json()
    b = client.get("/mission/recommend", params={"experiment": "MARS_GEOLOGY_SAMPLING", "target": "MARS_CHLORIDE", "top": 5}).json()
    assert a["regions"] and b["regions"]
    assert [r["best_score"] for r in a["regions"]] != [r["best_score"] for r in b["regions"]]
    for r in a["regions"]:
        assert 0 <= r["best_score"] <= 100 and 0 <= r["coverage"] <= 1
        assert any(d["similarity"] is None for d in r["dimensions"])   # missing dims preserved as null


def test_experiment_changes_results_for_same_target():
    x = client.get("/mission/recommend", params={"experiment": "MOON_ROVER_MOBILITY", "target": "MOON_SP_RIDGE", "allow_unverified": True}).json()
    y = client.get("/mission/recommend", params={"experiment": "MOON_POWER_THERMAL", "target": "MOON_SP_RIDGE", "allow_unverified": True}).json()
    assert x["weights_used"] != y["weights_used"]


def test_invalid_requests():
    assert client.get("/mission/recommend", params={"experiment": "NOPE"}).status_code == 404
    assert client.get("/mission/recommend", params={"experiment": "MOON_WATER_ICE", "target": "MARS_ICE"}).status_code == 422


def test_existing_endpoints_still_work():
    assert client.get("/targets").status_code == 200
    assert client.get("/score", params={"target": "MARS_ICE", "limit": 5}).status_code == 200
    assert client.get("/compare", params={"lat": 20, "lon": 10}).status_code == 200
    assert client.get("/recommend", params={"body": "moon", "purpose": "ISRU_WATER"}).status_code == 200


def test_custom_weights_change_result_and_validate():
    base = client.get("/mission/recommend", params={"experiment": "MARS_GEOLOGY_SAMPLING", "target": "MARS_JEZERO", "top": 3}).json()
    tuned = client.get("/mission/recommend", params={"experiment": "MARS_GEOLOGY_SAMPLING", "target": "MARS_JEZERO", "top": 3,
                                                    "weights": "D2_aridity:0,D8_thermal_swing:3"}).json()
    assert tuned["custom_weights"] == {"D2_aridity": 0.0, "D8_thermal_swing": 3.0}
    assert tuned["weights_used"] != base["weights_used"]
    assert client.get("/mission/recommend", params={"experiment": "MARS_GEOLOGY_SAMPLING", "weights": "D2_aridity:9"}).status_code == 422
    assert client.get("/mission/recommend", params={"experiment": "MARS_GEOLOGY_SAMPLING", "weights": "nonsense"}).status_code == 422
