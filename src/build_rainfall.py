"""Phase 3 - build district-month rainfall from CHIRPS (yr.nc).

Method: take the Zimbabwe window of the global 0.05 deg CHIRPS grid, assign each
pixel to an admin-2 district by point-in-polygon, then average precip over each
district's pixels for every month. Compute a fixed 1981-2015 climatology by
district x calendar month and derive standardised anomalies.

Outputs:
  data_processed/rainfall_district_month.parquet
  data_processed/rainfall_climatology.parquet
  reports/phase3_rainfall_log.txt
"""
from __future__ import annotations

import json
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import xarray as xr
from shapely.geometry import Point

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "raw"
OUT = ROOT / "data_processed"
REP = ROOT / "reports"
OUT.mkdir(exist_ok=True)
L: list[str] = []


def log(*a):
    s = " ".join(str(x) for x in a)
    L.append(s)
    print(s)


LAT_SLICE = (-23.0, -15.0)
LON_SLICE = (24.5, 33.5)
CLIM_START = "1981-01-01"
CLIM_END = "2015-12-31"


def main():
    log("Phase 3 rainfall build")
    adm2 = gpd.read_file(RAW / "geo" / "zwe_adm2_geoboundaries.geojson")[["shapeName", "geometry"]]
    adm2 = adm2.rename(columns={"shapeName": "district"}).set_crs(4326, allow_override=True)
    log("adm2 districts:", len(adm2))

    ds = xr.open_dataset(RAW / "yr.nc")
    sub = ds["precip"].sel(latitude=slice(*LAT_SLICE), longitude=slice(*LON_SLICE))
    log("zw window dims:", dict(sub.sizes))
    lats = sub["latitude"].values
    lons = sub["longitude"].values
    nlat, nlon = len(lats), len(lons)
    log(f"pixels: {nlat} x {nlon} = {nlat*nlon}")

    lon2d, lat2d = np.meshgrid(lons, lats)
    pts = gpd.GeoDataFrame(
        {"flat": np.arange(nlat * nlon)},
        geometry=[Point(x, y) for x, y in zip(lon2d.ravel(), lat2d.ravel())],
        crs=4326,
    )
    joined = gpd.sjoin(pts, adm2, how="left", predicate="within")[["flat", "district"]]
    joined = joined.drop_duplicates("flat")
    pix_district = joined["district"].to_numpy()  # object array, None outside
    n_in = pd.notna(pix_district).sum()
    log(f"pixels inside a district: {n_in} ({100*n_in/(nlat*nlon):.1f}%)")

    # precip array: (time, nlat, nlon) -> (time, npix)
    arr = sub.values.reshape(sub.sizes["time"], nlat * nlon).astype("float64")
    times = pd.to_datetime(sub["time"].values)
    log("time coverage:", times.min().date(), "->", times.max().date(), "n=", len(times))

    districts = sorted(pd.unique(pix_district[pd.notna(pix_district)]))
    out = np.full((len(times), len(districts)), np.nan)
    for j, d in enumerate(districts):
        mask = pix_district == d
        block = arr[:, mask]
        with np.errstate(invalid="ignore"):
            out[:, j] = np.nanmean(block, axis=1)
    rain = pd.DataFrame(out, columns=districts)
    rain.insert(0, "month", times)
    long = rain.melt(id_vars="month", var_name="district", value_name="rainfall_mm").dropna()
    long["month"] = pd.to_datetime(long["month"])
    long = long.sort_values(["district", "month"]).reset_index(drop=True)
    long.to_parquet(OUT / "rainfall_district_month.parquet", index=False)
    log("rainfall rows:", len(long), "districts:", long['district'].nunique())

    # fixed climatology 1981-2015 by district x calendar month
    cl = long[(long["month"] >= CLIM_START) & (long["month"] <= CLIM_END)].copy()
    cl["cal_month"] = cl["month"].dt.month
    clim = cl.groupby(["district", "cal_month"])["rainfall_mm"].agg(["mean", "std", "count"]).reset_index()
    clim.columns = ["district", "cal_month", "clim_mean_mm", "clim_sd_mm", "clim_n"]
    clim.to_parquet(OUT / "rainfall_climatology.parquet", index=False)
    log("climatology rows:", len(clim))

    # anomalies over the full record using the fixed climatology
    full = long.copy()
    full["cal_month"] = full["month"].dt.month
    full = full.merge(clim[["district", "cal_month", "clim_mean_mm", "clim_sd_mm"]],
                      on=["district", "cal_month"], how="left")
    full["rainfall_anom_z"] = (full["rainfall_mm"] - full["clim_mean_mm"]) / full["clim_sd_mm"]
    full.to_parquet(OUT / "rainfall_district_month_anom.parquet", index=False)

    summary = {
        "zw_window_dims": [nlat, nlon],
        "pixels_inside_district_pct": round(100 * n_in / (nlat * nlon), 1),
        "districts": int(long["district"].nunique()),
        "months": int(long["month"].nunique()),
        "time_min": str(long["month"].min().date()),
        "time_max": str(long["month"].max().date()),
        "climatology_period": [CLIM_START, CLIM_END],
    }
    (REP / "phase3_rainfall_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    log("summary:", summary)
    (REP / "phase3_rainfall_log.txt").write_text("\n".join(L), encoding="utf-8")
    print("done")


if __name__ == "__main__":
    main()
