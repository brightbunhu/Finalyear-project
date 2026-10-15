"""Phase 1 feasibility: how big a market x commodity x currency monthly panel
can actually be built, and how many series are long enough for lagged targets."""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "raw"
REPORTS = ROOT / "reports"
L: list[str] = []


def log(*a):
    s = " ".join(str(x) for x in a)
    L.append(s)
    print(s)


def main():
    df = pd.read_csv(RAW / "wfp_food_prices_zwe.csv")
    df["date"] = pd.to_datetime(df["date"])
    df["month"] = df["date"].dt.to_period("M").dt.to_timestamp()

    log("RAW rows:", len(df))
    log("categories:", df["category"].unique().tolist())

    food = df[df["category"] != "non-food"].copy()
    log("food-only rows:", len(food))

    food = food[food["price"] > 0].copy()
    log("food & price>0 rows:", len(food))

    # monthly median per market-commodity-currency
    key = ["market_id", "market", "commodity_id", "commodity", "category", "currency",
           "unit", "admin1", "admin2", "latitude", "longitude", "month"]
    grp = ["market_id", "commodity_id", "currency", "month"]
    panel = (food.groupby(grp, dropna=False)
                 .agg(price=("price", "median"),
                      usdprice=("usdprice", "median"),
                      n_obs=("price", "size"),
                      unit=("unit", lambda s: s.mode().iat[0] if len(s.mode()) else None),
                      category=("category", lambda s: s.mode().iat[0] if len(s.mode()) else None))
                 .reset_index())
    log("MARKET-COMMODITY-CURRENCY-MONTH cells:", len(panel))
    log("currency split of cells:", panel["currency"].value_counts().to_dict())

    # series length distribution
    sl = panel.groupby(["market_id", "commodity_id", "currency"]).size()
    log("\nnumber of series (market,commodity,currency):", len(sl))
    log("series length describe:")
    log(sl.describe().to_string())
    for thr in [6, 12, 24, 36, 60, 120]:
        log(f"  series with >= {thr} months: {(sl >= thr).sum()}")

    # distinct commodities with enough series
    log("\nmonths covered overall:", panel["month"].nunique(),
        panel["month"].min().date(), "->", panel["month"].max().date())
    log("cells per year:")
    log(panel.groupby(panel["month"].dt.year).size().to_string())

    # after building next-month labels within series (needs consecutive months)
    panel = panel.sort_values(["market_id", "commodity_id", "currency", "month"])
    panel["next_month"] = panel.groupby(["market_id", "commodity_id", "currency"])["month"].shift(-1)
    consec = (panel["next_month"] - panel["month"]).dt.days == 31  # approx one month apart
    log("\nrows with an immediately-following monthly observation (labelable):", int(consec.sum()),
        f"({100*consec.mean():.1f}%)")

    # commodities present
    log("\ncommodities:", sorted(food["commodity"].unique().tolist()))
    log("units:", food["unit"].unique().tolist())

    (REPORTS / "phase1_feasibility.txt").write_text("\n".join(L), encoding="utf-8")
    print("\nwritten:", REPORTS / "phase1_feasibility.txt")


if __name__ == "__main__":
    main()
