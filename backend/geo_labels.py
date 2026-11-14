"""Approximate, human-readable geographic labels for a lat/lon.

This is DISPLAY metadata only (never used in scoring). Labels come from coarse bounding boxes of
well-known land regions; when several boxes contain a point the smallest box wins. Anything not
covered falls back to a plain coordinate label. Boxes are approximate and are reported to the
client with label_basis="approximate named region (bounding box)".
"""
from __future__ import annotations

# (lat_min, lat_max, lon_min, lon_max, name)
_BOXES: list[tuple[float, float, float, float, str]] = [
    (15, 32, -17, 35, "Sahara Desert"),
    (-30, -17, 11, 17, "Namib Desert"),
    (-28, -18, 18, 26, "Kalahari Desert"),
    (-31, -17, -71.5, -67, "Atacama Desert"),
    (-27, -15, -70, -64, "Andean Altiplano"),
    (-55, -39, -74, -65, "Patagonia"),
    (-22, -3, -45, -34, "Northeast Brazil (Caatinga)"),
    (-15, 5, -75, -50, "Amazon Basin"),
    (-5, 5, 10, 30, "Congo Basin"),
    (10, 17, -17, 35, "Sahel"),
    (7, 15, 38, 44, "Afar / Horn of Africa"),
    (-10, 15, 28, 42, "East African Rift region"),
    (14, 30, 35, 60, "Arabian Peninsula"),
    (28, 36, 50, 60, "Iranian Plateau"),
    (36, 46, 53, 70, "Karakum / Kyzylkum Desert"),
    (24, 30, 69, 76, "Thar Desert"),
    (30, 37, 72, 80, "Karakoram / western Himalaya"),
    (28, 37, 78, 100, "Tibetan Plateau"),
    (36, 41, 77, 90, "Taklamakan Desert"),
    (38, 47, 90, 120, "Gobi Desert"),
    (50, 75, 60, 140, "Siberia"),
    (-32, -18, 115, 141, "Australian Outback"),
    (36, 42, -120, -112, "Great Basin (USA)"),
    (30, 37, -118, -109, "Southwest USA deserts"),
    (62, 84, -73, -12, "Greenland"),
    (65, 83, -125, -60, "Canadian Arctic"),
    (55, 72, -168, -141, "Alaska"),
    (76, 81, 10, 28, "Svalbard"),
    (63, 66.6, -24.5, -13, "Iceland"),
    (-90, -60, -180, 180, "Antarctica"),
    (18.5, 22.5, -160.5, -154.5, "Hawaii"),
    (38, 45, 38, 50, "Caucasus / Caspian region"),
    (36, 42, 26, 45, "Anatolian Plateau"),
    (55, 71, 5, 30, "Scandinavia"),
    (35, 55, -10, 30, "Europe"),
    (24, 50, -125, -66, "Contiguous United States"),
    (14, 32, -118, -86, "Mexico"),
    (8, 36, 68, 90, "Indian subcontinent"),
    (-26, -12, 43, 51, "Madagascar"),
    (50, 70, -140, -60, "Northern Canada"),
]


def label_for(lat: float, lon: float) -> dict:
    best = None
    best_area = None
    for la0, la1, lo0, lo1, name in _BOXES:
        if la0 <= lat <= la1 and lo0 <= lon <= lo1:
            area = (la1 - la0) * (lo1 - lo0)
            if best_area is None or area < best_area:
                best, best_area = name, area
    ns = "N" if lat >= 0 else "S"
    ew = "E" if lon >= 0 else "W"
    coords = f"{abs(lat):.1f}°{ns}, {abs(lon):.1f}°{ew}"
    if best:
        return {"label": f"{best} ({coords})", "region_name": best,
                "basis": "approximate named region (bounding box)"}
    return {"label": f"Land region near {coords}", "region_name": None,
            "basis": "coordinates only (no named-region match)"}
