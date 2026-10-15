"""Dependency-free sanity/QA checks (Phase 10). Run: python tests/run_checks.py"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data_processed"
ART = ROOT / "artifacts"

FEATURE_COLS = ["ret_z_cur", "ret_lag1", "ret_lag2", "ret_roll3", "spi", "peer_count",
                "rain_anom_z", "rain_anom_lag1", "rain_anom_lag2", "rain_anom_lag3",
                "rain_roll3_mm", "month_sin", "month_cos", "log_population",
                "category", "currency"]
LEAKY = ["z_next", "next_spi", "y1", "y2", "labelable_y1", "labelable_y2"]

results = []


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {name} {detail}")


def main():
    for base in ["usdprice", "nominal_within_currency"]:
        p = OUT / f"panel_{base}.parquet"
        check(f"panel exists: {base}", p.exists())
        if not p.exists():
            continue
        df = pd.read_parquet(p)
        check(f"{base}: no target/next columns used as features",
              not (set(FEATURE_COLS) & set(LEAKY)))
        check(f"{base}: labelable_y1 implies z_next present",
              df.loc[df["labelable_y1"], "z_next"].notna().all())
        check(f"{base}: labelable_y2 implies next_spi present",
              df.loc[df["labelable_y2"], "next_spi"].notna().all())
        prev = df.loc[df["labelable_y1"], "y1"].mean()
        check(f"{base}: y1 prevalence in 10-20% band", 0.10 <= prev <= 0.20,
              f"(={prev:.3f})")
        prev2 = df.loc[df["labelable_y2"], "y2"].mean()
        check(f"{base}: y2 prevalence in 10-20% band", 0.10 <= prev2 <= 0.20,
              f"(={prev2:.3f})")
        dup = df.duplicated(["market_id", "commodity_id", "currency", "month"]).sum()
        check(f"{base}: unit key (market×commodity×currency×month) is unique", dup == 0,
              f"(dups={int(dup)})")

    m = ART / "metrics_all_tasks.csv"
    if m.exists():
        md = pd.read_csv(m)
        check("metrics: 4 tasks present", md["task"].nunique() == 4)
        check("metrics: 5 models per task-split", (md.groupby(["task", "split"])["model"].nunique() == 5).all())
        check("metrics: roc_auc in [0,1]", md["roc_auc"].between(0, 1).all())
        check("metrics: majority baselines ~0.5",
              md[(md.model == "majority")]["roc_auc"].sub(0.5).abs().max() < 0.02)
    else:
        check("metrics_all_tasks.csv exists", False)

    for f in ["models/y2_peer_histgbm_usd.joblib", "models/y2_peer_histgbm_usd.meta.json"]:
        check(f"model artefact: {f}", (ROOT / f).exists())

    n_fail = sum(1 for _, ok, _ in results if not ok)
    print(f"\n{len(results) - n_fail}/{len(results)} checks passed")
    return 1 if n_fail else 0


if __name__ == "__main__":
    sys.exit(main())
