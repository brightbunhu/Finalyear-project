"""Optuna hyperparameter tuning for the food price stress models.

Tuning is done ONLY on the training period, using the SAME expanding-window folds as
src/train.py. The forward holdout is never touched during tuning. The objective is the
mean validation-block ROC-AUC across folds.

Outputs (artifacts/):
  optuna_trials_<task>_<model>.csv   - every trial (number, value, params, state)
  optuna_best_<task>_<model>.json    - best params, best value, n_trials, timings
  optuna_summary.csv                 - one row per study (n_trials, best value, ...)

Usage:
  python src/tune_optuna.py                 # all tasks, models from config
  python src/tune_optuna.py --n-trials 3    # quick smoke run
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import optuna
import yaml
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score
from sklearn.pipeline import Pipeline

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from train import CAT, NUM, chrono_folds, make_design  # noqa: E402

OUT = ROOT / "data_processed"
ART = ROOT / "artifacts"
ART.mkdir(exist_ok=True)
CFG = yaml.safe_load((ROOT / "config" / "targets.yml").read_text(encoding="utf-8"))
SEED = int(CFG["seed"])
TASKS = [("T1_usd_y1", "usdprice", "y1"),
         ("T2_usd_y2", "usdprice", "y2"),
         ("T3_nominal_y1", "nominal_within_currency", "y1"),
         ("T4_nominal_y2", "nominal_within_currency", "y2")]

optuna.logging.set_verbosity(optuna.logging.WARNING)


def prepare(name, base, ycol):
    df = pd.read_parquet(OUT / f"panel_{base}.parquet")
    df = df[df[f"labelable_{ycol}"]].copy()
    df["month"] = pd.to_datetime(df["month"])
    df = df.sort_values("month").reset_index(drop=True)
    df, pre = make_design(df)
    months = sorted(df["month"].unique())
    folds, holdout = chrono_folds(months, int(CFG["validation"]["n_folds"]),
                                  int(CFG["validation"]["holdout_months"]))
    # tuning uses training months only (excludes the holdout)
    folds = [(tr, va) for (tr, va) in folds if not (set(tr) & holdout) and not (set(va) & holdout)]
    return df, pre, folds, holdout


def cv_score(df, pre, folds, params, model_name, ycol):
    Xf = df[NUM + CAT]
    y = df[ycol].astype(int).to_numpy()
    aucs = []
    for train_m, val_m in folds:
        tr = df["month"].isin(train_m).to_numpy()
        va = df["month"].isin(val_m).to_numpy()
        ytr, yva = y[tr], y[va]
        if len(np.unique(ytr)) < 2 or len(np.unique(yva)) < 2:
            continue
        clf = HistGradientBoostingClassifier(random_state=SEED, **params)
        pipe = Pipeline([("pre", pre), ("clf", clf)])
        pipe.fit(Xf[tr], ytr)
        p = pipe.predict_proba(Xf[va])[:, 1]
        aucs.append(roc_auc_score(yva, p))
    return float(np.mean(aucs)) if aucs else float("nan")


def suggest_hgb(trial):
    return {
        "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.30, log=True),
        "max_iter": trial.suggest_int("max_iter", 100, 500, step=50),
        "max_leaf_nodes": trial.suggest_int("max_leaf_nodes", 7, 63),
        "min_samples_leaf": trial.suggest_int("min_samples_leaf", 10, 60),
        "l2_regularization": trial.suggest_float("l2_regularization", 1e-3, 10.0, log=True),
        "max_bins": trial.suggest_categorical("max_bins", [128, 255]),
    }


def tune_task(name, base, ycol, n_trials, model_name="hist_gradient_boosting"):
    df, pre, folds, _ = prepare(name, base, ycol)
    print(f"[tune] {name}: {len(folds)} training folds x {n_trials} trials ...", flush=True)

    def objective(trial):
        params = suggest_hgb(trial)
        return cv_score(df, pre, folds, params, model_name, ycol)

    sampler = optuna.samplers.TPESampler(seed=int(CFG["optuna"].get("sampler_seed", SEED)))
    study = optuna.create_study(direction="maximize", sampler=sampler)
    t0 = time.time()
    study.optimize(objective, n_trials=n_trials, show_progress_bar=False)
    elapsed = time.time() - t0

    # trials table
    rows = []
    for t in study.trials:
        r = {"number": t.number, "value": t.value, "state": str(t.state),
             "datetime_start": str(t.datetime_start), "datetime_complete": str(t.datetime_complete)}
        r.update({f"param_{k}": v for k, v in t.params.items()})
        rows.append(r)
    trials_df = pd.DataFrame(rows).sort_values("number")
    trials_df.to_csv(ART / f"optuna_trials_{name}_{model_name}.csv", index=False)

    # rank trials by value (completed ones)
    done = trials_df.dropna(subset=["value"]).sort_values("value", ascending=False)
    best_row = done.iloc[0] if len(done) else None

    summary = {
        "task": name, "model": model_name, "n_trials": int(len(study.trials)),
        "n_completed": int(sum(1 for t in study.trials if t.value is not None)),
        "best_value_mean_cv_roc_auc": float(study.best_value),
        "best_params": dict(study.best_params),
        "elapsed_seconds": round(elapsed, 1),
        "sampler": "TPE", "sampler_seed": int(CFG["optuna"].get("sampler_seed", SEED)),
        "objective": "mean validation-block ROC-AUC across expanding-window folds (training period only)",
        "config_version": CFG.get("version"), "seed": SEED,
    }
    (ART / f"optuna_best_{name}_{model_name}.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8")

    print(f"[tune] {name}: best mean CV ROC-AUC = {study.best_value:.4f} "
          f"in {elapsed:.0f}s | best params: {study.best_params}", flush=True)
    return summary


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-trials", type=int, default=None)
    ap.add_argument("--task", type=str, default=None)
    args = ap.parse_args()

    n_trials = args.n_trials if args.n_trials is not None else int(CFG["optuna"]["n_trials"])
    models = CFG["optuna"].get("models", ["hist_gradient_boosting"])
    tasks = [t for t in TASKS if (args.task is None or t[0] == args.task)]
    if not models or not CFG["optuna"].get("enabled", True):
        print("Optuna tuning disabled in config. Nothing to do.")
        return

    summaries = []
    for name, base, ycol in tasks:
        for model_name in models:
            summaries.append(tune_task(name, base, ycol, n_trials, model_name))

    summ = pd.DataFrame(summaries)
    summ.to_csv(ART / "optuna_summary.csv", index=False)
    print("\n=== Optuna summary ===")
    print(summ[["task", "model", "n_trials", "best_value_mean_cv_roc_auc", "elapsed_seconds"]]
          .to_string(index=False))
    print(f"\nTotal studies: {len(summaries)}; trials per study: {n_trials}")


if __name__ == "__main__":
    main()
