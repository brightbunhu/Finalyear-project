"""Phase 5 - baselines and models with chronological expanding-window validation
and a forward holdout. No random splitting. Thresholds chosen on validation only.

Tasks:
  T1: usdprice  base, Y1 standardised-return stress
  T2: usdprice  base, Y2 peer-relative stress
  T3: nominal   base, Y1
  T4: nominal   base, Y2

Outputs (artifacts/):
  metrics_<task>.csv, folds_<task>.json, preds_<task>.parquet,
  splits.json, run_metadata.json
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (average_precision_score, brier_score_loss,
                             confusion_matrix, f1_score, precision_score,
                             recall_score, roc_auc_score, balanced_accuracy_score)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from xgboost import XGBClassifier

import yaml

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data_processed"
ART = ROOT / "artifacts"
ART.mkdir(exist_ok=True)
CFG = yaml.safe_load((ROOT / "config" / "targets.yml").read_text(encoding="utf-8"))
SEED = int(CFG["seed"])
TUNED_MODELS = list(CFG.get("optuna", {}).get("models", []))


def load_tuned_params(task_name, model_name):
    """Return (best_params, n_trials) from the Optuna artefact, or (None, None)."""
    p = ART / f"optuna_best_{task_name}_{model_name}.json"
    if p.exists():
        d = json.loads(p.read_text(encoding="utf-8"))
        return d.get("best_params"), d.get("n_trials")
    return None, None

NUM = ["ret_z_cur", "ret_lag1", "ret_lag2", "ret_roll3", "spi", "peer_count",
       "rain_anom_z", "rain_anom_lag1", "rain_anom_lag2", "rain_anom_lag3",
       "rain_roll3_mm", "month_sin", "month_cos", "log_population", "interaction"]
CAT = ["category", "currency"]


def make_design(df):
    df = df.copy()
    df["interaction"] = df["ret_z_cur"] * df["rain_anom_z"]
    df[NUM] = df[NUM].replace([np.inf, -np.inf], np.nan)
    pre = ColumnTransformer([
        ("num", Pipeline([("imp", SimpleImputer(strategy="median")),
                          ("sc", StandardScaler())]), NUM),
        ("cat", Pipeline([("imp", SimpleImputer(strategy="most_frequent")),
                          ("oh", OneHotEncoder(handle_unknown="ignore"))]), CAT),
    ])
    return df, pre


def chrono_folds(months, n_folds, holdout_n):
    months = list(months)
    holdout = set(months[-holdout_n:]) if holdout_n > 0 else set()
    pre = months[:-holdout_n] if holdout_n > 0 else months
    n_folds = max(1, min(n_folds, len(pre) - 1))
    # contiguous validation blocks over `pre`
    edges = np.linspace(0, len(pre), n_folds + 1).astype(int)
    folds = []
    for i in range(1, n_folds + 1):
        vstart, vend = edges[i - 1], edges[i]
        val = set(pre[vstart:vend])
        train = set(pre[:vstart])
        if train and val:
            folds.append((train, val))
    return folds, holdout


def metrics_at(y, p, thr):
    pred = (p >= thr).astype(int)
    tn, fp, fn, tp = confusion_matrix(y, pred, labels=[0, 1]).ravel()
    return {
        "roc_auc": roc_auc_score(y, p) if len(np.unique(y)) > 1 else np.nan,
        "pr_auc": average_precision_score(y, p),
        "precision": precision_score(y, pred, zero_division=0),
        "recall": recall_score(y, pred, zero_division=0),
        "specificity": tn / (tn + fp) if (tn + fp) else np.nan,
        "f1": f1_score(y, pred, zero_division=0),
        "balanced_accuracy": balanced_accuracy_score(y, pred),
        "brier": brier_score_loss(y, np.clip(p, 0, 1)),
        "threshold": thr,
        "tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp),
        "n": int(len(y)), "pos": int(y.sum()),
    }


def best_threshold(y, p):
    cands = np.linspace(0.02, 0.98, 97)
    best, bt = -1, 0.5
    for t in cands:
        f = f1_score(y, (p >= t).astype(int), zero_division=0)
        if f > best:
            best, bt = f, t
    return bt


def model_zoo(pos_weight):
    return {
        "majority": DummyClassifier(strategy="prior", random_state=SEED),
        "logistic_elasticnet": LogisticRegression(solver="saga", l1_ratio=0.5, C=1.0,
                                                  max_iter=10000, tol=1e-3,
                                                  class_weight="balanced", random_state=SEED),
        "hist_gradient_boosting": HistGradientBoostingClassifier(
            learning_rate=0.05, max_iter=300, max_leaf_nodes=15, min_samples_leaf=30,
            l2_regularization=1.0, random_state=SEED),
        "xgboost": XGBClassifier(n_estimators=300, learning_rate=0.05, max_depth=4,
                                 subsample=0.8, colsample_bytree=0.8,
                                 reg_lambda=1.0, random_state=SEED,
                                 eval_metric="logloss", scale_pos_weight=pos_weight,
                                 n_jobs=4),
    }


def run_task(name, base, ycol):
    df = pd.read_parquet(OUT / f"panel_{base}.parquet")
    df = df[df[f"labelable_{ycol}"]].copy()
    df["month"] = pd.to_datetime(df["month"])
    df = df.sort_values("month").reset_index(drop=True)
    df, pre = make_design(df)
    months = sorted(df["month"].unique())
    folds, holdout = chrono_folds(months, int(CFG["validation"]["n_folds"]),
                                  int(CFG["validation"]["holdout_months"]))
    pos_weight = (len(df[df[ycol] == 0]) / max(len(df[df[ycol] == 1]), 1))

    models = model_zoo(pos_weight)
    models["persistence"] = None  # special-case

    # apply Optuna-tuned hyperparameters where a study artefact exists
    tuned_info = {}
    for mname in TUNED_MODELS:
        params, n_trials = load_tuned_params(name, mname)
        if params is None:
            continue
        if mname == "hist_gradient_boosting":
            models[mname] = HistGradientBoostingClassifier(random_state=SEED, **params)
        tuned_info[mname] = {
            "params": params, "n_trials": n_trials,
            "source": f"artifacts/optuna_best_{name}_{mname}.json"}

    Xf = df[NUM + CAT]
    y = df[ycol].astype(int).to_numpy()

    # ---------------- CV ----------------
    pooled = {m: {"p": np.zeros(len(df)), "seen": np.zeros(len(df), bool)} for m in models}
    fold_records = []
    for fi, (train_m, val_m) in enumerate(folds):
        tr = df["month"].isin(train_m).to_numpy()
        va = df["month"].isin(val_m).to_numpy()
        Xtr, Xva = Xf[tr], Xf[va]
        ytr, yva = y[tr], y[va]
        for mname, m in models.items():
            if mname == "majority":
                p_va = np.full(int(va.sum()), float(y.mean()))
            elif mname == "persistence":
                p_va = persistence_score(df[va], ycol)
            else:
                pipe = Pipeline([("pre", pre), ("clf", m)])
                pipe.fit(Xtr, ytr)
                p_va = pipe.predict_proba(Xva)[:, 1]
            pooled[mname]["p"][va] = p_va
            pooled[mname]["seen"][va] = True
        fold_records.append({"fold": fi, "n_train": int(tr.sum()), "n_val": int(va.sum()),
                             "train_months": [str(pd.Timestamp(t).date()) for t in sorted(train_m)][:2] +
                                              ["..."] + [str(pd.Timestamp(t).date()) for t in sorted(train_m)][-2:],
                             "val_months": [str(pd.Timestamp(t).date()) for t in sorted(val_m)]})

    # per-model CV metrics at F1-optimal threshold on pooled val
    rows = []
    for mname in models:
        seen = pooled[mname]["seen"]
        p = pooled[mname]["p"][seen]
        yy = y[seen]
        thr = best_threshold(yy, p)
        mt = metrics_at(yy, p, thr)
        mt["model"] = mname
        mt["split"] = "cv_pooled"
        rows.append(mt)

    # ---------------- holdout ----------------
    tr = (~df["month"].isin(holdout)).to_numpy()
    ho = df["month"].isin(holdout).to_numpy()
    Xtr, Xho = Xf[tr], Xf[ho]
    ytr, yho = y[tr], y[ho]
    holdout_preds = {}
    for mname, m in models.items():
        if mname == "majority":
            p_ho = np.full(int(ho.sum()), float(y.mean()))
        elif mname == "persistence":
            p_ho = persistence_score(df[ho], ycol)
        else:
            pipe = Pipeline([("pre", pre), ("clf", m)])
            pipe.fit(Xtr, ytr)
            p_ho = pipe.predict_proba(Xho)[:, 1]
        holdout_preds[mname] = p_ho
        # threshold from that model's own CV
        cvrow = [r for r in rows if r["model"] == mname][0]
        mt = metrics_at(yho, p_ho, cvrow["threshold"])
        mt["model"] = mname
        mt["split"] = "holdout"
        rows.append(mt)

    metrics = pd.DataFrame(rows)
    metrics.insert(0, "task", name)
    metrics.insert(1, "base", base)
    metrics.insert(2, "target", ycol)
    metrics.to_csv(ART / f"metrics_{name}.csv", index=False)

    # save predictions (holdout)
    pred_df = df.loc[ho, ["market_id", "commodity_id", "currency", "month", "district",
                          "category", ycol]].copy()
    for mname, p in holdout_preds.items():
        pred_df[f"p_{mname}"] = p
    pred_df.to_parquet(ART / f"preds_{name}.parquet", index=False)

    (ART / f"folds_{name}.json").write_text(json.dumps(
        {"folds": fold_records, "holdout_months": [str(pd.Timestamp(t).date()) for t in sorted(holdout)],
         "cv_months": [str(pd.Timestamp(t).date()) for t in months if t not in holdout]}, indent=2), encoding="utf-8")

    print(f"== {name} ({base}, {ycol}) ==")
    print(metrics[["model", "split", "n", "roc_auc", "pr_auc", "f1", "balanced_accuracy"]]
          .round(3).to_string(index=False))
    return metrics, tuned_info


def persistence_score(sub, ycol):
    """Rule score: current condition carries forward. Scaled to [0,1] for comparability."""
    if ycol == "y1":
        s = sub["ret_z_cur"].to_numpy()
    else:
        s = sub["spi"].to_numpy()
    s = np.nan_to_num(s, nan=0.0)
    lo, hi = np.nanmin(s), np.nanmax(s)
    if hi - lo < 1e-9:
        return np.zeros_like(s)
    return (s - lo) / (hi - lo)


if __name__ == "__main__":
    tasks = [("T1_usd_y1", "usdprice", "y1"),
             ("T2_usd_y2", "usdprice", "y2"),
             ("T3_nominal_y1", "nominal_within_currency", "y1"),
             ("T4_nominal_y2", "nominal_within_currency", "y2")]
    allm = []
    tuning = {}
    for name, base, ycol in tasks:
        mt, tuned = run_task(name, base, ycol)
        allm.append(mt)
        if tuned:
            tuning[name] = tuned
    pd.concat(allm).to_csv(ART / "metrics_all_tasks.csv", index=False)

    meta = {"seed": SEED, "config": CFG, "tasks": [t[0] for t in tasks],
            "features_numeric": NUM, "features_categorical": CAT,
            "tuning": tuning,
            "tuning_objective": "mean validation-block ROC-AUC across expanding-window folds (training period only)"}
    (ART / "run_metadata.json").write_text(json.dumps(meta, indent=2, default=str), encoding="utf-8")
    print("written artifacts/")
    if tuning:
        print("Optuna-tuned models (trials per task):")
        for task, info in tuning.items():
            for m, d in info.items():
                print(f"  {task} / {m}: {d['n_trials']} trials")
