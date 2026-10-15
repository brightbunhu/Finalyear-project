"""Phase 1 deep dive: WFP price panel structure, currency regimes, dimensions,
duplicates, and a feasibility test of extracting CHIRPS over Zimbabwe."""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import xarray as xr

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "raw"
REPORTS = ROOT / "reports"

L: list[str] = []


def log(*a):
    s = " ".join(str(x) for x in a)
    L.append(s)
    print(s)


def food_deep():
    p = RAW / "wfp_food_prices_zwe.csv"
    df = pd.read_csv(p)
    df["date"] = pd.to_datetime(df["date"])
    log("=" * 100)
    log("WFP FOOD PRICES DEEP DIVE")
    log(f"rows={len(df)}  date range {df['date'].min().date()} .. {df['date'].max().date()}")
    log("rows by year:")
    log(df.groupby(df["date"].dt.year).size().to_string())

    log("\ncurrency counts:", df["currency"].value_counts().to_dict())
    log("currency by year (rows):")
    log(pd.crosstab(df["date"].dt.year, df["currency"]).to_string())

    log("\npriceflag:", df["priceflag"].value_counts(dropna=False).to_dict())
    log("pricetype:", df["pricetype"].value_counts(dropna=False).to_dict())
    log("unit:", df["unit"].value_counts(dropna=False).to_dict())
    log("category:", df["category"].value_counts(dropna=False).to_dict())
    log("n commodities:", df["commodity"].nunique(), "n markets:", df["market"].nunique(),
        "n market_id:", df["market_id"].nunique())

    log("\nadmin1 missing rows:", df["admin1"].isna().sum(), " admin2 missing rows:", df["admin2"].isna().sum())
    log("markets with missing admin2:", df.loc[df["admin2"].isna(), "market"].nunique())

    log("\nprice describe:")
    log(df["price"].describe().to_string())
    log("nonpositive price rows:", int((df["price"] <= 0).sum()))
    log("usdprice describe:")
    log(df["usdprice"].describe().to_string())

    # exact duplicate rows
    dup_all = df.duplicated().sum()
    key = ["date", "market_id", "commodity_id", "currency", "unit", "pricetype", "priceflag"]
    dup_key = df.duplicated(subset=key).sum()
    log(f"\nfull-row duplicates: {dup_all}")
    log(f"key duplicates (date,market,commodity,currency,unit,pricetype,priceflag): {dup_key}")

    # multiplicity per key
    g = df.groupby(key, dropna=False).size()
    log("key group sizes distribution:")
    log(g.value_counts().sort_index().to_string())

    # price units per commodity
    log("\ncommodity x unit combinations:")
    log(df.groupby(["commodity", "unit"]).size().to_string())

    # markets coordinates
    log("\nmarket_id present in markets file?")
    mk = pd.read_csv(RAW / "wfp_markets_zwe.csv")
    log("food markets:", df["market_id"].nunique(), "market ref:", mk["market_id"].nunique())
    log("food market_ids not in market ref:",
        len(set(df["market_id"]) - set(mk["market_id"])))
    log("lat/lon missing in food:", df["latitude"].isna().sum())

    # date-day pattern
    log("\nday-of-month distribution of date:", df["date"].dt.day.value_counts().to_dict())


def chirps_test():
    p = RAW / "yr.nc"
    log("=" * 100)
    log("CHIRPS Zimbabwe extract test")
    ds = xr.open_dataset(p)
    # Zimbabwe bbox approx lat -22.5..-15.5, lon 25..33.5
    sub = ds["precip"].sel(latitude=slice(-23, -15), longitude=slice(25, 33.5))
    log("zimbabwe-shaped slice dims:", dict(sub.sizes))
    # take a 2020-01 slice
    t = pd.Timestamp("2020-01-01")
    sl = sub.sel(time=t, method="nearest")
    vals = sl.values
    log(f"slice {t.date()}: shape={vals.shape} nan_frac={np.isnan(vals).mean():.3f} "
        f"min={np.nanmin(vals):.2f} max={np.nanmax(vals):.2f} mean={np.nanmean(vals):.2f}")
    log("global time coverage:", str(ds['time'].values[0]), "->", str(ds['time'].values[-1]))
    ds.close()


if __name__ == "__main__":
    food_deep()
    chirps_test()
    (ROOT / "reports" / "phase1_food_deep.txt").write_text("\n".join(L), encoding="utf-8")
    print("\nwritten:", ROOT / "reports" / "phase1_food_deep.txt")
