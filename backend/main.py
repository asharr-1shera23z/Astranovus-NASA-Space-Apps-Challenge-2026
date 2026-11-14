"""FastAPI backend. Run from repo root:  uvicorn backend.main:app --reload --port 8000"""
import json, pathlib
import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from model.scoring_core import score_grid, explain_cell

ROOT = pathlib.Path(__file__).resolve().parents[1]
real = ROOT / "data/processed/earth_grid.csv"
GRID = pd.read_csv(real if real.exists() else ROOT / "data/sample/earth_grid_sample.csv")
TARGETS = {t["id"]: t for t in json.load(open(ROOT / "data/targets.json"))}
DIMENSIONS = json.load(open(ROOT / "data/dimensions.json"))

app = FastAPI(title="ASTRANOVUS API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


def _target(tid):
    if tid not in TARGETS: raise HTTPException(404, f"unknown target {tid}")
    return TARGETS[tid]


def _clean(df):
    return json.loads(df.replace({np.nan: None}).to_json(orient="records"))


@app.get("/health")
def health(): return {"ok": True, "cells": len(GRID), "targets": len(TARGETS)}

@app.get("/targets")
def targets(): return list(TARGETS.values())

@app.get("/dimensions")
def dimensions(): return DIMENSIONS

@app.get("/score")
def score(target: str, min_score: float = 0, limit: int = 5000):
    s = score_grid(GRID, _target(target)).dropna(subset=["score"])
    s = s[s.score >= min_score].sort_values("score", ascending=False).head(limit)
    return _clean(s)

@app.post("/score_custom")
def score_custom(body: dict, min_score: float = 0, limit: int = 5000):
    t = body.get("target")
    if not t or "rules" not in t: raise HTTPException(422, "body must be {'target': {'rules': {...}}}")
    s = score_grid(GRID, t).dropna(subset=["score"])
    s = s[s.score >= min_score].sort_values("score", ascending=False).head(limit)
    return _clean(s)

def _nearest(lat, lon):
    i = ((GRID.lat - lat) ** 2 + (GRID.lon - lon) ** 2).idxmin()
    return GRID.loc[i]

@app.get("/site")
def site(lat: float, lon: float, target: str):
    t = _target(target); row = _nearest(lat, lon)
    sc = score_grid(GRID.loc[[row.name]], t).iloc[0]
    return {"cell_id": int(row.cell_id), "lat": float(row.lat), "lon": float(row.lon),
            "score": None if pd.isna(sc.score) else float(sc.score), "coverage": float(sc.coverage),
            "breakdown": explain_cell(row, t)}

@app.get("/compare")
def compare(lat: float, lon: float):
    row = _nearest(lat, lon); out = []
    for t in TARGETS.values():
        sc = score_grid(GRID.loc[[row.name]], t).iloc[0]
        out.append({"target": t["id"], "name": t["name"], "score": None if pd.isna(sc.score) else float(sc.score)})
    return {"cell_id": int(row.cell_id), "lat": float(row.lat), "lon": float(row.lon), "scores": out}
