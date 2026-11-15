"""Build data/processed/earth_grid.csv from the REAL downloaded NASA products (reproducible, non-destructive).

Run with the isolated data environment (Python 3.12 + pyhdf + h5py):
    .venv-data/Scripts/python scripts/build_earth_grid.py

Inputs (never modified):
    data/raw/MOD11C3/*.hdf     MODIS Terra monthly 0.05 deg land-surface temperature (HDF4, collection 061)
    data/raw/MOD13C2/*.hdf     MODIS Terra monthly 0.05 deg vegetation indices (HDF4, collection 061)
    data/raw/MOD10CM/*.hdf     MODIS Terra monthly 0.05 deg snow cover (HDF4, collection 061)
    data/raw/GPM_3IMERGM/*.HDF5  GPM IMERG V07B monthly 0.1 deg precipitation (HDF5)
    data/processed/archive/earth_grid_power_only_v1.csv  (auto-created from the previous grid, holds the
                                                          NASA POWER climatology dimensions D1, D2, D7, D8)

Outputs:
    data/processed/earth_grid.csv               contract-compatible grid (cell_id, lat, lon, D1..D8)
    data/processed/earth_grid_features.csv      raw physical per-cell features (traceability)
    data/processed/earth_grid_metadata.json     provenance, temporal coverage, quality rules, cross-checks

Dimension policy (see docs/METHODOLOGY.md):
    D1_cold, D2_aridity, D7_polar_light  NASA POWER climatology (full-year, kept from the validated v1 grid)
    D3_barren          MOD13C2 NDVI, peak monthly NDVI over the available months, inverted, percentile
    D6_ice             MOD10CM snow cover, peak monthly snow cover over available months, percentile (PROXY)
    D8_thermal_swing   MOD11C3 land-surface-temperature day-night range, mean over available months,
                       only where EVERY available month is valid; percentile
    D4_terrain, D5_rock  no data source integrated yet -> left empty (never fabricated)
All 12 monthly granules of 2024 are processed when present (one year, not a multi-year climatology); with fewer months the values are labelled PARTIAL SEASONAL.
"""
from __future__ import annotations

import datetime
import json
import pathlib
import re
import shutil
import sys

import numpy as np
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[1]
RAW = ROOT / "data/raw"
PROC = ROOT / "data/processed"
ARCHIVE = PROC / "archive"
BASE_BACKUP = ARCHIVE / "earth_grid_power_only_v1.csv"
OUT_GRID = PROC / "earth_grid.csv"
OUT_FEAT = PROC / "earth_grid_features.csv"
OUT_META = PROC / "earth_grid_metadata.json"

DIMS = ["D1_cold", "D2_aridity", "D3_barren", "D4_terrain", "D5_rock", "D6_ice", "D7_polar_light", "D8_thermal_swing"]
MIN_VALID_FRACTION = 0.30   # a cell needs valid pixels over >= 30% of its land pixels, else it is left empty


# ----------------------------------------------------------------------------- readers
def read_hdf4(path, name):
    from pyhdf.SD import SD, SDC
    sd = SD(str(path), SDC.READ)
    sds = sd.select(name)
    return sds[:], sds.attributes()


def valid_range(attrs):
    v = attrs["valid_range"]
    if isinstance(v, str):
        v = v.strip("[]").split(",")
    return float(v[0]), float(v[1])


def month_from_name(path: pathlib.Path) -> int:
    n = path.name
    m = re.search(r"\.A(\d{4})(\d{3})\.", n)           # MODIS: AYYYYDDD (first day of month)
    if m:
        d = datetime.date(int(m.group(1)), 1, 1) + datetime.timedelta(days=int(m.group(2)) - 1)
        return d.month
    m = re.search(r"IMERG\.(\d{4})(\d{2})\d{2}-", n)    # GPM: YYYYMMDD start
    if m:
        return int(m.group(2))
    raise ValueError(f"cannot parse month from {n}")


def blocks(cells: pd.DataFrame, res: float, step: float, nrows: int, ncols: int):
    """Yield (index, row0, row1, col0, col1) pixel slices for each grid cell on a north-up global array."""
    n = int(round(step / res))
    for i, r in enumerate(cells.itertuples()):
        r0 = int(round((90 - (r.lat + step / 2)) / res))
        c0 = int(round((r.lon - step / 2 + 180) / res))
        yield i, max(r0, 0), min(r0 + n, nrows), max(c0, 0), min(c0 + n, ncols)


def block_mean(values: np.ndarray, land: np.ndarray, cells: pd.DataFrame, res: float, step: float):
    """Mean of valid pixels per cell. `values` has NaN where invalid; `land` is a boolean land-pixel mask.
    Returns (mean, valid_fraction_of_land)."""
    nrows, ncols = values.shape
    mean = np.full(len(cells), np.nan)
    frac = np.zeros(len(cells))
    for i, r0, r1, c0, c1 in blocks(cells, res, step, nrows, ncols):
        v = values[r0:r1, c0:c1]
        lnd = land[r0:r1, c0:c1]
        n_land = int(lnd.sum())
        ok = ~np.isnan(v) & lnd
        n_ok = int(ok.sum())
        if n_land == 0:
            continue
        frac[i] = n_ok / n_land
        if frac[i] >= MIN_VALID_FRACTION and n_ok > 0:
            mean[i] = float(v[ok].mean())
    return mean, frac


# ----------------------------------------------------------------------------- products
def process_lst(cells, step):
    out, files = {}, []
    for f in sorted((RAW / "MOD11C3").glob("*.hdf")):
        m = month_from_name(f)
        day, a = read_hdf4(f, "LST_Day_CMG")
        night, _ = read_hdf4(f, "LST_Night_CMG")
        pland, _ = read_hdf4(f, "Percent_land_in_grid")
        sf = float(a["scale_factor"]); lo, hi = valid_range(a)
        def conv(raw):
            raw = raw.astype(np.float64)
            ok = (raw >= lo) & (raw <= hi) & (raw != float(a["_FillValue"]))
            k = np.where(ok, raw * sf + float(a["add_offset"]), np.nan)       # Kelvin
            return np.where((k >= 150) & (k <= 380), k, np.nan)               # physical plausibility only
        d, n = conv(day), conv(night)
        land = pland > 0
        dm, dfrac = block_mean(d, land, cells, 0.05, step)
        nm, nfrac = block_mean(n, land, cells, 0.05, step)
        both = np.where(np.isnan(d) | np.isnan(n), np.nan, d - n)
        rm, rfrac = block_mean(both, land, cells, 0.05, step)
        out[m] = {"day_K": dm, "night_K": nm, "dtr_K": rm, "valid_frac": rfrac}
        files.append({"file": f.name, "month": m})
    return out, files


def process_ndvi(cells, step):
    out, files = {}, []
    for f in sorted((RAW / "MOD13C2").glob("*.hdf")):
        m = month_from_name(f)
        nd, a = read_hdf4(f, "CMG 0.05 Deg Monthly NDVI")
        rel, _ = read_hdf4(f, "CMG 0.05 Deg Monthly pixel reliability")
        lo, hi = valid_range(a)
        raw = nd.astype(np.float64)
        ok = (raw >= lo) & (raw <= hi) & (raw != float(a["_FillValue"])) & np.isin(rel, [0, 1])  # good / marginal only
        v = np.where(ok, raw / float(a["scale_factor"]), np.nan)        # HDF-EOS convention: value = raw / scale_factor
        land = raw != float(a["_FillValue"])                            # NDVI is only produced over land
        mean, frac = block_mean(v, land, cells, 0.05, step)
        out[m] = {"ndvi": mean, "valid_frac": frac}
        files.append({"file": f.name, "month": m})
    return out, files


def process_snow(cells, step):
    out, files = {}, []
    for f in sorted((RAW / "MOD10CM").glob("*.hdf")):
        m = month_from_name(f)
        sc, a = read_hdf4(f, "Snow_Cover_Monthly_CMG")
        raw = sc.astype(np.float64)
        v = np.where(raw <= 100, raw, np.nan)                            # 0-100 percent; 211/250/253/254/255 are codes
        land = raw != 254                                                # 254 = water mask
        mean, frac = block_mean(v, land, cells, 0.05, step)
        out[m] = {"snow_pct": mean, "valid_frac": frac}
        files.append({"file": f.name, "month": m})
    return out, files


def process_gpm(cells, step):
    import h5py
    out, files = {}, []
    for f in sorted((RAW / "GPM_3IMERGM").glob("*.HDF5")):
        m = month_from_name(f)
        with h5py.File(f, "r") as h:
            ds = h["Grid/precipitation"]
            fill = float(ds.attrs["_FillValue"])
            arr = ds[0].astype(np.float64)                               # (lon, lat), mm/hr monthly mean rate
        arr = arr.T[::-1]                                                # -> (lat north-up, lon)
        v = np.where(arr == fill, np.nan, arr * 24.0)                    # mm/day
        land = np.ones_like(v, dtype=bool)
        mean, frac = block_mean(v, land, cells, 0.1, step)
        out[m] = {"precip_mm_day": mean, "valid_frac": frac}
        files.append({"file": f.name, "month": m})
    return out, files


def process_dem(cells, step):
    """NASA SRTMGL30 v002 (30 arc-second, ~1 km). Tiles are raw big-endian int16, 4800 x 6000, nodata -9999.
    Tile name = upper-left corner (e.g. w020n90 covers lon -20..20, lat 40..90). Cell edges are multiples of 2.5 deg,
    tile edges are multiples of 10 deg, so every cell lies inside one tile."""
    import io
    import zipfile
    res = 1 / 120.0
    cache, feats, files = {}, [], []

    def tile(lon, lat):
        ul_lon = int(np.floor((lon + 180) / 40.0) * 40 - 180)
        ul_lat = 90 if lat >= 40 else (40 if lat >= -10 else -10)
        name = f"{'w' if ul_lon < 0 else 'e'}{abs(ul_lon):03d}{'n' if ul_lat >= 0 else 's'}{abs(ul_lat):02d}"
        if name not in cache:
            f = RAW / "SRTMGL30" / f"{name}.SRTMGL30.dem.zip"
            if not f.exists():
                cache[name] = None
            else:
                with zipfile.ZipFile(f) as z:
                    raw = z.read(z.namelist()[0])
                cache[name] = np.frombuffer(raw, dtype=">i2").reshape(6000, 4800)
                files.append(f.name)
        return cache[name], ul_lon, ul_lat

    out = {k: np.full(len(cells), np.nan) for k in ("elev_mean_m", "relief_m", "slope_mean_deg", "rough_std_m", "valid_frac")}
    for i, r in enumerate(cells.itertuples()):
        dem, ul_lon, ul_lat = tile(r.lon, r.lat)
        if dem is None or r.lat < -60:
            continue
        r0 = int(round((ul_lat - (r.lat + step / 2)) / res)); r1 = int(round((ul_lat - (r.lat - step / 2)) / res))
        c0 = int(round((r.lon - step / 2 - ul_lon) / res)); c1 = int(round((r.lon + step / 2 - ul_lon) / res))
        w = dem[max(r0, 0):min(r1, 6000), max(c0, 0):min(c1, 4800)].astype(np.float64)
        if w.size == 0:          # e.g. Antarctica: SRTMGL30 has no tile south of 60S -> D4 stays empty there
            continue
        ok = w > -9000
        out["valid_frac"][i] = ok.mean()
        if ok.mean() < MIN_VALID_FRACTION:
            continue
        wv = np.where(ok, w, np.nan)
        v = wv[ok]
        dy = 926.0
        dx = 926.0 * max(np.cos(np.radians(r.lat)), 0.05)
        gy, gx = np.gradient(wv, dy, dx)
        slope = np.degrees(np.arctan(np.hypot(gx, gy)))
        out["elev_mean_m"][i] = v.mean()
        out["relief_m"][i] = np.percentile(v, 95) - np.percentile(v, 5)
        out["rough_std_m"][i] = v.std()
        out["slope_mean_deg"][i] = np.nanmean(slope)
    return out, sorted(files)


def pct(series: pd.Series, invert=False) -> pd.Series:
    s = -series if invert else series
    return s.rank(pct=True, na_option="keep").round(4)


# ----------------------------------------------------------------------------- main
def main():
    PROC.mkdir(parents=True, exist_ok=True)
    ARCHIVE.mkdir(parents=True, exist_ok=True)
    global BASE_BACKUP
    if len(sys.argv) > 1 and float(sys.argv[1]) != 5.0:
        BASE_BACKUP = ARCHIVE / f"earth_grid_power_only_{float(sys.argv[1]):g}deg.csv"
        if not BASE_BACKUP.exists():
            sys.exit(f"{BASE_BACKUP.name} not found: run scripts/fetch_power_grid.py {sys.argv[1]} first.")
    if not BASE_BACKUP.exists():
        cur = pd.read_csv(OUT_GRID)
        if cur[["D3_barren", "D6_ice"]].notna().any().any():
            sys.exit("Refusing to archive a grid that already has MODIS-derived columns as the POWER base.")
        shutil.copy2(OUT_GRID, BASE_BACKUP)
        print("backed up previous grid ->", BASE_BACKUP)
    # keep the previous MODIS/GPM build (e.g. Jan+Jul) before overwriting it
    cur = pd.read_csv(OUT_GRID)
    if cur[["D3_barren", "D6_ice"]].notna().any().any():
        n_prev = len(json.load(open(OUT_META))["temporal_coverage"]["MODIS_GPM_months"]) if OUT_META.exists() else 0
        snap = ARCHIVE / f"earth_grid_modis_{n_prev}months_{len(cur)}cells_prev.csv"
        if not snap.exists():
            shutil.copy2(OUT_GRID, snap)
            print("archived previous MODIS build ->", snap)
    base = pd.read_csv(BASE_BACKUP)
    cells = base[["cell_id", "lat", "lon"]].copy()
    lats = np.sort(cells.lat.unique())
    step = float(np.min(np.diff(lats)))
    print(f"{len(cells)} cells at {step} deg")

    dem, dem_files = process_dem(cells, step)
    lst, lst_files = process_lst(cells, step)
    ndvi, ndvi_files = process_ndvi(cells, step)
    snow, snow_files = process_snow(cells, step)
    gpm, gpm_files = process_gpm(cells, step)

    feat = cells.copy()
    for tag, d, key in [("lst_day_K", lst, "day_K"), ("lst_night_K", lst, "night_K"), ("lst_dtr_K", lst, "dtr_K"),
                        ("ndvi", ndvi, "ndvi"), ("snow_pct", snow, "snow_pct"), ("precip_mm_day", gpm, "precip_mm_day")]:
        for m in sorted(d):
            feat[f"{tag}_m{m:02d}"] = d[m][key]

    def cols(prefix):
        return [c for c in feat.columns if c.startswith(prefix + "_m")]

    for k, v in dem.items():
        feat[f"dem_{k}"] = v

    # --- derived physical features
    n_months = len(lst)
    min_months = int(np.ceil(0.75 * n_months))                                  # 2 of 2 months, or 9 of 12
    dtr_cols = cols("lst_dtr_K")
    feat["lst_dtr_K_mean"] = feat[dtr_cols].mean(axis=1).where(feat[dtr_cols].notna().sum(axis=1) >= min_months)
    feat["ndvi_peak"] = feat[cols("ndvi")].max(axis=1)                          # >= 1 valid month
    feat["ndvi_valid_months"] = feat[cols("ndvi")].notna().sum(axis=1)
    feat["snow_peak_pct"] = feat[cols("snow_pct")].max(axis=1)
    feat["snow_valid_months"] = feat[cols("snow_pct")].notna().sum(axis=1)
    _lm = pd.concat([feat[cols("lst_day_K")], feat[cols("lst_night_K")]], axis=1)
    feat["lst_mean_K"] = _lm.mean(axis=1).where(_lm.notna().sum(axis=1) >= 2 * min_months)
    feat["precip_mm_day_mean"] = feat[cols("precip_mm_day")].mean(axis=1).where(feat[cols("precip_mm_day")].notna().sum(axis=1) >= min_months)

    # --- dimensions
    out = base.copy()
    out["D3_barren"] = pct(feat["ndvi_peak"], invert=True).values
    out["D6_ice"] = pct(feat["snow_peak_pct"]).values
    power_d8 = base["D8_thermal_swing"].copy()
    out["D8_thermal_swing"] = pct(feat["lst_dtr_K_mean"]).values
    out["D4_terrain"] = pct(feat["dem_relief_m"]).values       # landscape relief within the cell (P95-P5 of 1 km elevation)
    out["D5_rock"] = np.nan
    out = out[["cell_id", "lat", "lon"] + DIMS]

    feat["D8_power_air_dtr_pct_v1"] = power_d8.values   # previous POWER air-temperature-range dimension, kept for traceability
    for d in ("D1_cold", "D2_aridity", "D7_polar_light"):
        feat[f"{d}_power_pct"] = base[d].values

    # --- cross-checks between independent sources (Spearman rank correlation)
    def sp(a, b):
        df = pd.concat([a, b], axis=1).dropna()
        return {"n": int(len(df)), "spearman": round(float(df.corr(method="spearman").iloc[0, 1]), 3)} if len(df) > 10 else None
    cross = {
        "D1_cold (POWER air temp) vs MODIS mean LST over available months (inverted)": sp(base["D1_cold"], pct(feat["lst_mean_K"], invert=True)),
        "D2_aridity (POWER annual precip) vs GPM IMERG mean precip over available months (inverted)": sp(base["D2_aridity"], pct(feat["precip_mm_day_mean"], invert=True)),
        "D8 MODIS LST day-night range vs POWER air-temperature range (v1 D8)": sp(out["D8_thermal_swing"], power_d8),
        "D6 MODIS snow peak vs POWER months-below-0C proxy (v1 D6, if any)": None,
    }

    s2p = ROOT / "data/processed/stage2.json"
    if s2p.exists():
        s2 = [e for e in json.load(open(s2p)) if e.get("covered") and e.get("slope_mean_deg") is not None]
        pairs = []
        for e in s2:
            j = ((cells.lat - e["lat"]).abs() + (cells.lon - e["lon"]).abs()).idxmin()
            if abs(cells.lat[j] - e["lat"]) < 0.01 and not np.isnan(feat["dem_slope_mean_deg"][j]):
                pairs.append((feat["dem_relief_m"][j], e["relief_m"]))
        if len(pairs) >= 4:
            a = pd.DataFrame(pairs)
            cross["D4 1-km cell relief (SRTMGL30) vs 30-m 1-degree-tile relief (SRTM 1 arc-sec, top regions only)"] = {"n": len(a), "spearman": round(float(a.corr(method="spearman").iloc[0, 1]), 3)}
    months = sorted(set(lst) | set(ndvi) | set(snow) | set(gpm))
    full = len(months) == 12 and all(len(d) == 12 for d in (lst, ndvi, snow, gpm))
    span = (f"calendar year 2024, all 12 monthly granules (a single year, not a multi-year climatology)" if full
            else f"partial seasonal ({', '.join(f'2024-{m:02d}' for m in months)} only)")
    tshort = "full year 2024 (12 months)" if full else f"partial seasonal ({len(months)} months of 2024)"
    n = len(out)
    cov = {d: round(float(out[d].notna().mean()), 3) for d in DIMS}
    meta = {
        "built_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "script": "scripts/build_earth_grid.py",
        "grid": {"cells": n, "step_deg": step, "lat_range": [float(out.lat.min()), float(out.lat.max())],
                 "cell_definition": f"{step:g}-degree boxes centred on the land cells of the NASA POWER grid"},
        "values_are": "percentile ranks (0-1) among the valid cells of this grid; empty = no data",
        "temporal_coverage": {"MODIS_GPM_months": [f"2024-{m:02d}" for m in months],
                              "complete_year": full, "span": span,
                              "note": ("All 12 monthly granules of 2024 were processed. This is one year, not a multi-year climatology." if full else
                                       "Only these months were downloaded. MODIS/GPM-derived dimensions are PARTIAL SEASONAL (not annual).")},
        "quality_rules": {"min_valid_fraction_of_land_pixels": MIN_VALID_FRACTION,
                          "LST": "valid_range + fill removed, 150-380 K plausibility; QC bit flags NOT applied (legend not present in file metadata)",
                          "NDVI": "valid_range, fill and pixel_reliability in {0 good, 1 marginal}; value = raw/scale_factor(10000)",
                          "snow": "only 0-100 percent kept; 211 night, 250 cloud, 253 no decision, 254 water, 255 fill excluded",
                          "GPM": "fill -9999.9 removed; mm/hr monthly mean rate x 24 = mm/day"},
        "products": {
            "SRTMGL30": {"version": "002", "doi": "10.5067/MEaSUREs/SRTM/SRTMGL30.002", "files": dem_files, "variables": ["elevation (int16, m)"], "note": "~1 km; GTOPO30-filled outside 60N-56S"},
            "MOD11C3": {"version": "061", "doi": "10.5067/MODIS/MOD11C3.061", "files": lst_files, "variables": ["LST_Day_CMG", "LST_Night_CMG", "Percent_land_in_grid"], "scale": "0.02 K"},
            "MOD13C2": {"version": "061", "doi": "10.5067/MODIS/MOD13C2.061", "files": ndvi_files, "variables": ["CMG 0.05 Deg Monthly NDVI", "CMG 0.05 Deg Monthly pixel reliability"], "scale": "1/10000"},
            "MOD10CM": {"version": "061", "doi": "10.5067/MODIS/MOD10CM.061", "files": snow_files, "variables": ["Snow_Cover_Monthly_CMG"], "scale": "percent"},
            "GPM_3IMERGM": {"version": "V07B", "doi": "10.5067/GPM/IMERG/3B-MONTH/07", "files": gpm_files, "variables": ["Grid/precipitation"], "scale": "mm/hr"},
            "NASA_POWER": {"source": "climatology point API cache data/raw/power_cache.json", "parameters": "T2M, T2M_MAX, T2M_MIN, PRECTOTCORR, ALLSKY_SFC_SW_DWN"},
        },
        "dimensions": {
            "D1_cold": {"status": "derived", "temporal": "annual climatology", "source": "NASA POWER T2M (2 m AIR temperature, not land-surface temperature), inverted percentile"},
            "D2_aridity": {"status": "derived", "temporal": "annual climatology", "source": "NASA POWER PRECTOTCORR, inverted percentile"},
            "D3_barren": {"status": "derived", "temporal": tshort, "source": "MODIS MOD13C2 v061 NDVI, peak monthly NDVI (inverted percentile). Low NDVI also occurs over snow/ice and does not by itself characterise geology."},
            "D4_terrain": {"status": "derived", "temporal": "static (SRTM, 2000)", "source": "NASA SRTMGL30 v002 (~1 km; GTOPO30-filled outside 60N-56S): relief = P95 minus P5 of 1-km elevation inside the cell, percentile. Landscape-scale relief only, not rover-scale slope."},
            "D5_rock": {"status": "missing", "source": "No lithology/mineral dataset integrated (a categorical rock type will not be turned into a percentile without a documented method)"},
            "D6_ice": {"status": "proxy", "temporal": tshort, "source": "MODIS MOD10CM v061 snow cover extent, peak of monthly cell means. A snow-cover proxy; NOT permafrost, ground ice or subsurface ice."},
            "D7_polar_light": {"status": "derived", "temporal": "annual climatology", "source": "NASA POWER ALLSKY_SFC_SW_DWN seasonal swing. A terrestrial seasonal-insolation proxy; does not reproduce lunar illumination."},
            "D8_thermal_swing": {"status": "derived", "temporal": tshort, "source": f"MODIS MOD11C3 v061 land-surface-temperature day minus night, mean over valid months, requiring at least {min_months} of {n_months} valid months."},
        },
        "coverage_by_dimension": cov,
        "cross_checks": {k: v for k, v in cross.items() if v is not None},
        "preserved": {"previous_grid_backup": str(BASE_BACKUP.relative_to(ROOT)).replace("\\", "/")},
    }

    out.to_csv(OUT_GRID, index=False)
    feat.round(5).to_csv(OUT_FEAT, index=False)
    json.dump(meta, open(OUT_META, "w", encoding="utf-8"), indent=2)
    print("coverage:", cov)
    print("cross-checks:", meta["cross_checks"])
    print("wrote", OUT_GRID, OUT_FEAT, OUT_META)


if __name__ == "__main__":
    main()
