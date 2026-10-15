"""Phase 1: inspect the large NetCDF (yr.nc) and GeoJSON boundaries."""
from __future__ import annotations

import json
from pathlib import Path

import xarray as xr

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "raw"
REPORTS = ROOT / "reports"

LINES: list[str] = []


def log(*a):
    s = " ".join(str(x) for x in a)
    LINES.append(s)
    print(s)


def inspect_nc():
    p = RAW / "yr.nc"
    log("=" * 100)
    log(f"NETCDF: {p.name} ({p.stat().st_size/1e9:.2f} GB)")
    ds = xr.open_dataset(p, decode_times=True)
    log("dimensions:", dict(ds.dims))
    log("coordinates:", list(ds.coords))
    log("data_vars:")
    for v in ds.data_vars:
        da = ds[v]
        log(f"   - {v}: dims={da.dims} shape={da.shape} dtype={da.dtype} attrs={dict(da.attrs)}")
    log("global attrs:", dict(ds.attrs))
    for c in ds.coords:
        da = ds[c]
        try:
            log(f"   coord {c}: shape={da.shape} first={da.values.flat[0]} last={da.values.flat[-1]}")
        except Exception as e:  # noqa: BLE001
            log(f"   coord {c}: {e!r}")
    # preview a small slice
    for v in ds.data_vars:
        da = ds[v]
        try:
            sl = da.isel({d: slice(0, 2) for d in da.dims})
            log(f"   sample {v}: {sl.values.ravel()[:8]}")
        except Exception as e:  # noqa: BLE001
            log(f"   sample {v} error {e!r}")
    ds.close()


def inspect_geojson():
    for fn in ["zwe_adm1_geoboundaries.geojson", "zwe_adm2_geoboundaries.geojson"]:
        p = RAW / "geo" / fn
        log("=" * 100)
        log(f"GEOJSON: {fn} ({p.stat().st_size/1e6:.2f} MB)")
        with p.open(encoding="utf-8") as f:
            gj = json.load(f)
        feats = gj.get("features", [])
        log(f"type={gj.get('type')} n_features={len(feats)}")
        if feats:
            log("feature[0] properties:", json.dumps(feats[0].get("properties", {}), indent=2)[:1500])
            names = [f["properties"].get("shapeName") or f["properties"].get("name") for f in feats]
            log("names:", names)
            geoms = {f.get("geometry", {}).get("type") for f in feats}
            log("geometry types:", geoms)


if __name__ == "__main__":
    try:
        inspect_nc()
    except Exception as e:  # noqa: BLE001
        log("NC ERROR:", repr(e))
    inspect_geojson()
    (REPORTS / "phase1_nc_geo_profile.txt").write_text("\n".join(LINES), encoding="utf-8")
    print("\nwritten:", REPORTS / "phase1_nc_geo_profile.txt")
