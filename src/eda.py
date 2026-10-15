"""Phase 4 - exploratory data analysis on the real processed panel.

Produces labelled descriptive tables (CSV) and figures (PNG). Descriptive only:
no claim of causation or predictive usefulness is made here.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data_processed"
FIG = ROOT / "figures"
REP = ROOT / "reports"
FIG.mkdir(exist_ok=True)

BASE = "usdprice"
panel = pd.read_parquet(OUT / f"panel_{BASE}.parquet")
nom = pd.read_parquet(OUT / "panel_nominal_within_currency.parquet")
figs: list[str] = []


def savefig(name):
    p = FIG / name
    plt.tight_layout()
    plt.savefig(p, dpi=150)
    plt.close()
    figs.append(name)
    print("figure:", name)


# ---------------------------------------------------------------- coverage
cov = panel.groupby(panel["month"].dt.to_period("M").dt.to_timestamp()).size()
cov.to_csv(REP / "phase4_monthly_coverage.csv")
fig, ax = plt.subplots(figsize=(9, 4.5))
cov.plot(ax=ax, color="#2b6cb0", label="Labelable food cells")
ax.set_title("Figure 4.3.1: Monthly data coverage")
ax.set_ylabel("Number of food cells"); ax.set_xlabel("Month")
ax.legend()
savefig("fig4.3.1_monthly_coverage.png")

# ---------------------------------------------------------------- class balance
bal = pd.DataFrame({
    "target": ["y1_return_stress", "y2_peer_stress"],
    "labelable": [int(panel["labelable_y1"].sum()), int(panel["labelable_y2"].sum())],
    "positive": [int((panel["y1"] == 1).sum()), int((panel["y2"] == 1).sum())],
})
bal["prevalence_pct"] = 100 * bal["positive"] / bal["labelable"].clip(lower=1)
bal.to_csv(REP / "phase4_class_balance.csv", index=False)
print(bal.to_string(index=False))

groups = ["Y1 standardised\nreturn stress", "Y2 peer-relative\nstress"]
non = [int((panel["y1"] == 0).sum()), int((panel["y2"] == 0).sum())]
pos = [int((panel["y1"] == 1).sum()), int((panel["y2"] == 1).sum())]
x = np.arange(len(groups)); w = 0.38
fig, ax = plt.subplots(figsize=(8, 4.5))
ax.bar(x - w / 2, non, w, label="Non-stress", color="#94a3b8", edgecolor="k", lw=0.4)
ax.bar(x + w / 2, pos, w, label="Stress", color="#c0392b", edgecolor="k", lw=0.4)
ax.set_xticks(x); ax.set_xticklabels(groups)
ax.set_title("Figure 4.3.2: Label distribution of the two targets")
ax.set_ylabel("Number of labelable cells"); ax.set_xlabel("Target")
ax.legend(title="Class")
savefig("fig4.3.2_class_balance.png")

# ---------------------------------------------------------------- by category / currency
by_cat = (panel.groupby("category")
          .apply(lambda g: pd.Series({
              "n_labelable_y1": g["labelable_y1"].sum(),
              "prev_y1_pct": 100 * g["y1"].sum() / max(g["labelable_y1"].sum(), 1),
              "n_labelable_y2": g["labelable_y2"].sum(),
              "prev_y2_pct": 100 * g["y2"].sum() / max(g["labelable_y2"].sum(), 1)}))
          .reset_index())
by_cat.to_csv(REP / "phase4_by_category.csv", index=False)

by_cur = (panel.groupby("currency")
          .apply(lambda g: pd.Series({
              "n": len(g),
              "prev_y1_pct": 100 * g["y1"].sum() / max(g["labelable_y1"].sum(), 1),
              "prev_y2_pct": 100 * g["y2"].sum() / max(g["labelable_y2"].sum(), 1)}))
          .reset_index())
by_cur.to_csv(REP / "phase4_by_currency.csv", index=False)

fig, ax = plt.subplots(figsize=(9, 4.5))
ax.bar(by_cat["category"], by_cat["prev_y1_pct"], color="#2b6cb0", label="Y1 prevalence")
ax.set_ylabel("Y1 prevalence (%)"); ax.set_xlabel("Commodity category")
ax.set_title("Figure 4.3.3: Positive-label prevalence by commodity category")
plt.xticks(rotation=20, ha="right"); ax.legend()
savefig("fig4.3.3_prev_by_category.png")

# ---------------------------------------------------------------- price trends
# USD-based (comparable) median price over time, and ZWL nominal (log), each as
# its own single-plot figure (nominal series are not comparable across regimes).
ts = panel.groupby("month")["price"].median()
fig, ax = plt.subplots(figsize=(9, 4.5))
ax.plot(ts.index, ts.values, color="#2b6cb0", label="Median USD price")
ax.set_yscale("log")
ax.set_title("Figure 4.3.4: Median monthly food price (USD base)")
ax.set_ylabel("Median price (USD, log scale)"); ax.set_xlabel("Month"); ax.legend()
savefig("fig4.3.4_median_usd_price.png")

fig, ax = plt.subplots(figsize=(9, 4.5))
for cur, g in nom.groupby("currency"):
    g2 = g.groupby("month")["price"].median()
    ax.plot(g2.index, g2.values, label=cur)
ax.set_yscale("log")
ax.set_title("Figure 4.3.5: Median nominal food price by currency")
ax.set_ylabel("Median nominal price (log scale)"); ax.set_xlabel("Month")
ax.legend(title="Currency")
savefig("fig4.3.5_median_nominal_price.png")

# ---------------------------------------------------------------- returns distribution
fig, ax = plt.subplots(figsize=(8, 4.5))
r = panel["ret"].replace([np.inf, -np.inf], np.nan).dropna()
ax.hist(r.clip(-2, 2), bins=80, color="#4a5568", label="Monthly log returns")
ax.axvline(0, color="k", lw=1, label="Zero return")
ax.set_title("Figure 4.3.8: Distribution of monthly log returns (USD base)")
ax.set_xlabel("Log return (clipped to [-2, 2])"); ax.set_ylabel("Frequency")
ax.legend()
savefig("fig4.3.8_returns_distribution.png")

# ---------------------------------------------------------------- rainfall
rain = pd.read_parquet(OUT / "rainfall_district_month_anom.parquet")
fig, ax = plt.subplots(figsize=(8, 4.5))
ax.hist(rain["rainfall_anom_z"].dropna().clip(-4, 4), bins=60, color="#2f855a",
        label="District-month observations")
ax.set_title("Figure 4.3.6: Standardised rainfall anomaly distribution")
ax.set_xlabel("Rainfall anomaly (z, 1981-2015 climatology)"); ax.set_ylabel("Frequency")
ax.legend()
savefig("fig4.3.6_rainfall_anomaly_dist.png")

fig, ax = plt.subplots(figsize=(9, 4.5))
for d in ["Beitbridge", "Chiredzi", "Harare", "Buhera"]:
    s = rain[rain["district"] == d].set_index("month")["rainfall_anom_z"]
    ax.plot(s.index, s.values, label=d, lw=0.9)
ax.set_title("Figure 4.3.7: Rainfall anomaly time series (example districts)")
ax.set_xlabel("Month"); ax.set_ylabel("Rainfall anomaly (z)")
ax.legend(title="District", fontsize=8)
savefig("fig4.3.7_rainfall_anomaly_series.png")

# ---------------------------------------------------------------- missingness
cols = ["ret", "ret_lag1", "ret_roll3", "spi", "rain_anom_z", "rain_anom_lag1",
        "rain_roll3_mm", "log_population", "y1", "y2"]
miss = pd.DataFrame({"missing_pct": [100 * panel[c].isna().mean() for c in cols]}, index=cols)
miss.to_csv(REP / "phase4_missingness.csv")
fig, ax = plt.subplots(figsize=(8, 4.5))
ax.barh(miss.index, miss["missing_pct"], color="#718096", label="Missing share")
ax.set_xlabel("Missing (%)"); ax.set_ylabel("Feature")
ax.set_title(f"Figure 4.3.9: Missingness in key features (USD panel, n={len(panel)})")
ax.legend()
savefig("fig4.3.9_missingness.png")

# ---------------------------------------------------------------- descriptive stats table
desc_cols = ["price", "ret", "ret_lag1", "ret_lag2", "ret_roll3", "ret_z_cur",
             "spi", "rain_anom_z", "rain_anom_lag1", "rain_roll3_mm", "log_population"]
desc = panel[desc_cols].describe().T[["count", "mean", "std", "min", "50%", "max"]]
desc.columns = ["n", "mean", "std", "min", "median", "max"]
desc.to_csv(REP / "phase4_descriptive_stats.csv")

summary = {
    "panel_rows": int(len(panel)),
    "month_min": str(panel["month"].min().date()),
    "month_max": str(panel["month"].max().date()),
    "markets": int(panel["market_id"].nunique()),
    "districts": int(panel["district"].nunique()),
    "y1_prevalence_pct": round(100 * (panel["y1"] == 1).sum() / max(panel["labelable_y1"].sum(), 1), 2),
    "y2_prevalence_pct": round(100 * (panel["y2"] == 1).sum() / max(panel["labelable_y2"].sum(), 1), 2),
    "figures": figs,
}
import json
(REP / "phase4_eda_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
print("done", summary)
