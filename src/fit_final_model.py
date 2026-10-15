"""Fit and persist the final models used by the dashboard, plus their metadata.

The model is fitted on all data before the forward holdout, so the dashboard's
scenario scorer is consistent with the reported validation. The holdout is never
used in fitting.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

import yaml

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data_processed"
ART = ROOT / "artifacts"
CFG = yaml.safe_load((ROOT / "config" / "targets.yml").read_text(encoding="utf-8"))
SEED = int(CFG["seed"])
NUM = ["ret_z_cur", "ret_lag1", "ret_lag2", "ret_roll3", "spi", "peer_count",
       "rain_anom_z", "rain_anom_lag1", "rain_anom_lag2", "rain_anom_lag3",
       "rain_roll3_mm", "month_sin", "month_cos", "log_population", "interaction"]
CAT = ["category", "currency"]
MODELS_DIR = ROOT / "models"
MODELS_DIR.mkdir(exist_ok=True)


def prep(df):
    df = df.copy()
    df["interaction"] = df["ret_z_cur"] * df["rain_anom_z"]
    df[NUM] = df[NUM].replace([np.inf, -np.inf], np.nan)
    return df


def fit_one(base, ycol, name):
    df = prep(pd.read_parquet(OUT / f"panel_{base}.parquet"))
    df = df[df[f"labelable_{ycol}"]].copy()
    df["month"] = pd.to_datetime(df["month"])
    months = sorted(df["month"].unique())
    holdout = set(months[-int(CFG["validation"]["holdout_months"]):])
    tr = ~df["month"].isin(holdout)
    pre = ColumnTransformer([
        ("num", Pipeline([("imp", SimpleImputer(strategy="median")), ("sc", StandardScaler())]), NUM),
        ("cat", Pipeline([("imp", SimpleImputer(strategy="most_frequent")),
                          ("oh", OneHotEncoder(handle_unknown="ignore"))]), CAT)])
    clf = HistGradientBoostingClassifier(learning_rate=0.05, max_iter=300, max_leaf_nodes=15,
                                         min_samples_leaf=30, l2_regularization=1.0, random_state=SEED)
    # use the Optuna-selected configuration when the study artefact exists
    task = {"usdprice": {"y1": "T1_usd_y1", "y2": "T2_usd_y2"},
            "nominal_within_currency": {"y1": "T3_nominal_y1", "y2": "T4_nominal_y2"}}[base][ycol]
    tuned = None
    tp = ART / f"optuna_best_{task}_hist_gradient_boosting.json"
    if tp.exists():
        d = json.loads(tp.read_text(encoding="utf-8"))
        tuned = {"params": d.get("best_params"), "n_trials": d.get("n_trials"),
                 "best_mean_cv_roc_auc": d.get("best_value_mean_cv_roc_auc")}
        if tuned["params"]:
            clf = HistGradientBoostingClassifier(random_state=SEED, **tuned["params"])
    pipe = Pipeline([("pre", pre), ("clf", clf)])
    pipe.fit(df.loc[tr, NUM + CAT], df.loc[tr, ycol].astype(int))
    joblib.dump(pipe, MODELS_DIR / f"{name}.joblib")
    meta = {
        "name": name, "base": base, "target": ycol, "model": "HistGradientBoostingClassifier",
        "features_numeric": NUM, "features_categorical": CAT,
        "trained_through": str(df.loc[tr, "month"].max().date()),
        "holdout_from": str(min(holdout).date()),
        "n_train": int(tr.sum()),
        "prevalence_train": float(df.loc[tr, ycol].astype(int).mean()),
        "threshold_y1_sd": float(CFG["target_return_stress"]["threshold_sd"]),
        "threshold_y2_spi": float(CFG["target_peer_stress"]["threshold_spi"]),
        "fitted_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "seed": SEED, "config_version": CFG["version"],
        "tuning": tuned,
    }
    (MODELS_DIR / f"{name}.meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(f"saved {name}: n_train={meta['n_train']} prev={meta['prevalence_train']:.3f} "
          f"through {meta['trained_through']}")


if __name__ == "__main__":
    fit_one("usdprice", "y2", "y2_peer_histgbm_usd")
    fit_one("usdprice", "y1", "y1_return_histgbm_usd")
    print("models saved to", MODELS_DIR)
