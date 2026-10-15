"""Phase 6b - robustness, uncertainty and holdout-diagnosis suite.

Answers the supervisor's requirements to:
  * use the same target/eval set per claim (separate tables per task);
  * report uncertainty intervals and treat repeated market observations;
  * investigate why holdout performance deteriorates (by year, currency, commodity);
  * test alternative thresholds, training windows, feature exclusions;
  * attempt recalibration / retraining to improve later-period performance;
  * test permutation-importance stability across folds;
  * quantify outlier handling effects.

Outputs: reports/phase6b_*.csv
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.impute import SimpleImputer
from sklearn.inspection import permutation_importance
from sklearn.metrics import (average_precision_score, brier_score_loss, f1_score,
                             roc_auc_score)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from xgboost import XGBClassifier
import yaml

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data_processed"
REP = ROOT / "reports"
ART = ROOT / "artifacts"
CFG = yaml.safe_load((ROOT / "config" / "targets.yml").read_text(encoding="utf-8"))
SEED = int(CFG["seed"])
RNG = np.random.default_rng(SEED)
HOLDOUT_MONTHS = int(CFG["validation"]["holdout_months"])

NUM = ["ret_z_cur", "ret_lag1", "ret_lag2", "ret_roll3", "spi", "peer_count",
       "rain_anom_z", "rain_anom_lag1", "rain_anom_lag2", "rain_anom_lag3",
       "rain_roll3_mm", "month_sin", "month_cos", "log_population", "interaction"]
CAT = ["category", "currency"]
RAIN = ["rain_anom_z", "rain_anom_lag1", "rain_anom_lag2", "rain_anom_lag3", "rain_roll3_mm"]
PEER = ["spi", "peer_count"]

TASKS = {
    "T1_usd_y1": ("usdprice", "y1"),
    "T2_usd_y2": ("usdprice", "y2"),
    "T3_nominal_y1": ("nominal_within_currency", "y1"),
    "T4_nominal_y2": ("nominal_within_currency", "y2"),
}


def load(base: str) -> pd.DataFrame:
    df = pd.read_parquet(OUT / f"panel_{base}.parquet")
    df["interaction"] = df["ret_z_cur"] * df["rain_anom_z"]
    df[NUM] = df[NUM].replace([np.inf, -np.inf], np.nan)
    df["month"] = pd.to_datetime(df["month"])
    return df


# current task context, so every model matches the Optuna-selected configuration used
# by src/train.py for that same task.
CURRENT_TASK: str | None = None


def set_current_task(task: str | None) -> None:
    global CURRENT_TASK
    CURRENT_TASK = task


def tuned_hist_params(task: str | None) -> dict | None:
    if not task:
        return None
    p = ART / f"optuna_best_{task}_hist_gradient_boosting.json"
    if p.exists():
        d = json.loads(p.read_text(encoding="utf-8"))
        params = d.get("best_params")
        if params:
            return params
    return None


def pre(num=NUM, cat=CAT):
    return ColumnTransformer([
        ("num", Pipeline([("imp", SimpleImputer(strategy="median")), ("sc", StandardScaler())]), num),
        ("cat", Pipeline([("imp", SimpleImputer(strategy="most_frequent")),
                          ("oh", OneHotEncoder(handle_unknown="ignore"))]), cat)])


def make_model(kind="hist", y=None):
    if kind == "hist":
        tuned = tuned_hist_params(CURRENT_TASK)
        if tuned:
            return HistGradientBoostingClassifier(random_state=SEED, **tuned)
        return HistGradientBoostingClassifier(learning_rate=0.05, max_iter=300,
                                              max_leaf_nodes=15, min_samples_leaf=30,
                                              l2_regularization=1.0, random_state=SEED)
    if kind == "xgb":
        w = 1.0
        if y is not None and y.sum() > 0:
            w = len(y[y == 0]) / max(len(y[y == 1]), 1)
        return XGBClassifier(n_estimators=300, learning_rate=0.05, max_depth=4,
                             subsample=0.8, colsample_bytree=0.8, reg_lambda=1.0,
                             scale_pos_weight=w, random_state=SEED, eval_metric="logloss",
                             n_jobs=4)
    raise ValueError(kind)


def fit_pred(df, ycol, num, cat, kind, holdout: set):
    tr = ~df["month"].isin(holdout)
    ho = df["month"].isin(holdout)
    y = df[ycol].astype(int).to_numpy()
    pipe = Pipeline([("pre", pre(num, cat)), ("clf", make_model(kind, y[tr.to_numpy()]))])
    pipe.fit(df.loc[tr, num + cat], y[tr.to_numpy()])
    p = pipe.predict_proba(df.loc[ho, num + cat])[:, 1]
    return y[ho.to_numpy()], p, ho.to_numpy(), tr.to_numpy()


def holdout_set(df, ycol):
    months = sorted(df.loc[df[f"labelable_{ycol}"], "month"].unique())
    return set(months[-HOLDOUT_MONTHS:]), months


def label_mask(df, ycol):
    return df[f"labelable_{ycol}"].to_numpy()


# ------------------------------------------------------------------ bootstrap
def boot_ci(y, p, groups=None, n=2000):
    y = np.asarray(y); p = np.asarray(p)
    rng = np.random.default_rng(SEED)
    if groups is None:
        idxs = [rng.integers(0, len(y), len(y)) for _ in range(n)]
    else:
        g = np.asarray(groups)
        uniq = np.unique(g)
        idxs = []
        for _ in range(n):
            sel = rng.choice(uniq, size=len(uniq), replace=True)
            idxs.append(np.concatenate([np.where(g == s)[0] for s in sel]))
    vals = []
    for ix in idxs:
        yy = y[ix]
        if yy.min() == yy.max():
            continue
        vals.append(roc_auc_score(yy, p[ix]))
    vals = np.array(vals)
    return (float(roc_auc_score(y, p)), float(np.percentile(vals, 2.5)),
            float(np.percentile(vals, 97.5)), len(vals))


def do_bootstrap():
    rows = []
    for task, (base, ycol) in TASKS.items():
        set_current_task(task)
        df = load(base)[label_mask(load(base), ycol)].copy()
        ho, _ = holdout_set(load(base), ycol)
        for kind in ["xgb", "hist"]:
            y, p, _, _ = fit_pred(df, ycol, NUM, CAT, kind, ho)
            auc, lo, hi, nb = boot_ci(y, p)
            _, mlo, mhi, _ = boot_ci(y, p, groups=df.loc[df["month"].isin(ho), "market_id"].to_numpy())
            rows.append({"task": task, "model": kind, "n_holdout": len(y),
                         "pos": int(y.sum()), "roc_auc": round(auc, 4),
                         "ci95_row_lo": round(lo, 4), "ci95_row_hi": round(hi, 4),
                         "ci95_market_lo": round(mlo, 4), "ci95_market_hi": round(mhi, 4),
                         "n_boot": nb})
    out = pd.DataFrame(rows)
    out.to_csv(REP / "phase6b_bootstrap_ci.csv", index=False)
    print("[bootstrap]\n", out.to_string(index=False))
    return out


# ------------------------------------------------------------------ OOF by group
def oof_predictions(df, ycol, kind, blocks=5):
    months = sorted(df.loc[df[f"labelable_{ycol}"], "month"].unique())
    n = len(months)
    start = int(n * 0.4)
    edges = np.linspace(start, n, blocks + 1).astype(int)
    rows = []
    y_all = df[ycol].astype(int)
    for i in range(blocks):
        lo, hi = edges[i], edges[i + 1]
        if hi <= lo:
            continue
        val_months = set(months[lo:hi])
        train_months = set(months[:lo])
        tr = df["month"].isin(train_months)
        va = df["month"].isin(val_months)
        if tr.sum() < 50 or va.sum() == 0 or y_all[tr].nunique() < 2:
            continue
        pipe = Pipeline([("pre", pre()), ("clf", make_model(kind, y_all[tr].to_numpy()))])
        pipe.fit(df.loc[tr, NUM + CAT], y_all[tr])
        p = pipe.predict_proba(df.loc[va, NUM + CAT])[:, 1]
        sub = df.loc[va, ["month", "currency", "category", "market_id", ycol]].copy()
        sub["p"] = p
        sub["fold"] = i
        rows.append(sub)
    return pd.concat(rows, ignore_index=True) if rows else pd.DataFrame()


def group_auc(oof, by):
    out = []
    for key, g in oof.groupby(by, dropna=False):
        if g["_y"].nunique() < 2 or len(g) < 20:
            out.append({"group": key, "n": len(g), "pos": int(g["_y"].sum()), "roc_auc": np.nan})
            continue
        out.append({"group": key, "n": len(g), "pos": int(g["_y"].sum()),
                    "roc_auc": round(roc_auc_score(g["_y"], g["p"]), 4)})
    return pd.DataFrame(out)


def do_oof_by_group():
    all_year, all_curr, all_comm = [], [], []
    for task, (base, ycol) in TASKS.items():
        set_current_task(task)
        df = load(base)
        df = df[df[f"labelable_{ycol}"]].copy()
        oof = oof_predictions(df, ycol, "xgb")
        if oof.empty:
            continue
        oof["_y"] = oof[ycol].astype(int)
        oof["year"] = pd.to_datetime(oof["month"]).dt.year
        for name, by, coll in [("year", "year", all_year), ("currency", "currency", all_curr),
                               ("commodity", "category", all_comm)]:
            g = group_auc(oof, by)
            g.insert(0, "task", task)
            coll.append(g)
    for coll, fname in [(all_year, "phase6b_oof_by_year.csv"),
                        (all_curr, "phase6b_oof_by_currency.csv"),
                        (all_comm, "phase6b_oof_by_commodity.csv")]:
        out = pd.concat(coll, ignore_index=True) if coll else pd.DataFrame()
        out.to_csv(REP / fname, index=False)
        print(f"[oof {fname}]\n", out.to_string(index=False))
    return 0


# ------------------------------------------------------------------ threshold / features / window / calibration
def labeled_at(df, ycol, thr):
    if ycol == "y1":
        z = df["z_next"]
        return (z >= thr).where(z.notna())
    s = df["next_spi"]
    return (s >= thr).where(s.notna())


def do_threshold_sensitivity():
    rows = []
    grid = {"y1": CFG["target_return_stress"]["threshold_grid_sd"][1:-1],
            "y2": CFG["target_peer_stress"]["threshold_grid_spi"]}
    for task, (base, ycol) in TASKS.items():
        set_current_task(task)
        df0 = load(base)
        months = sorted(df0.loc[df0[f"labelable_{ycol}"], "month"].unique())
        ho = set(months[-HOLDOUT_MONTHS:])
        for thr in grid[ycol]:
            df = df0.copy()
            lab = labeled_at(df, ycol, thr)
            df = df[lab.notna()].copy()
            df["_t"] = lab[lab.notna()].astype(int)
            y = df["_t"].astype(int).to_numpy()
            tr_m = (~df["month"].isin(ho)).to_numpy()
            ho_m = df["month"].isin(ho).to_numpy()
            if y[tr_m].sum() < 10 or y[ho_m].sum() < 3:
                continue
            pipe = Pipeline([("pre", pre()), ("clf", make_model("hist", y[tr_m]))])
            pipe.fit(df.loc[tr_m, NUM + CAT], y[tr_m])
            p = pipe.predict_proba(df.loc[ho_m, NUM + CAT])[:, 1]
            auc = round(roc_auc_score(y[ho_m], p), 4) if len(np.unique(y[ho_m])) > 1 else np.nan
            rows.append({"task": task, "threshold": thr,
                         "prevalence_pct": round(100 * y.mean(), 2),
                         "n_holdout": int(ho_m.sum()), "pos_holdout": int(y[ho_m].sum()),
                         "holdout_roc_auc": auc})
    out = pd.DataFrame(rows)
    out.to_csv(REP / "phase6b_threshold_model_sensitivity.csv", index=False)
    print("[threshold model sensitivity]\n", out.to_string(index=False))
    return out


def _auc_holdout(df, ycol, ho, num, cat, kind="xgb"):
    y, p, _, _ = fit_pred(df, ycol, num, cat, kind, ho)
    auc = round(roc_auc_score(y, p), 4) if len(np.unique(y)) > 1 else np.nan
    return auc, round(brier_score_loss(y, p), 4), len(y)


def do_feature_exclusion():
    rows = []
    for task in ["T1_usd_y1", "T2_usd_y2"]:
        set_current_task(task)
        base, ycol = TASKS[task]
        df0 = load(base)
        df0 = df0[df0[f"labelable_{ycol}"]].copy()
        ho, _ = holdout_set(load(base), ycol)
        full_auc, base_brier, n = _auc_holdout(df0, ycol, ho, NUM, CAT)
        no_rain = [f for f in NUM if f not in RAIN]
        no_peer = [f for f in NUM if f not in PEER]
        rain_auc, _, _ = _auc_holdout(df0, ycol, ho, no_rain, CAT)
        peer_auc, _, _ = _auc_holdout(df0, ycol, ho, no_peer, CAT)
        rows.append({"task": task, "variant": "full", "roc_auc": full_auc, "n": n})
        rows.append({"task": task, "variant": "drop_rainfall", "roc_auc": rain_auc,
                     "delta": round(rain_auc - full_auc, 4)})
        rows.append({"task": task, "variant": "drop_peer", "roc_auc": peer_auc,
                     "delta": round(peer_auc - full_auc, 4)})
    out = pd.DataFrame(rows)
    out.to_csv(REP / "phase6b_feature_exclusion.csv", index=False)
    print("[feature exclusion]\n", out.to_string(index=False))
    return out


def do_window_and_recalibration():
    rows = []
    for task in ["T1_usd_y1", "T2_usd_y2"]:
        set_current_task(task)
        base, ycol = TASKS[task]
        df = load(base)
        df = df[df[f"labelable_{ycol}"]].copy()
        ho, months = holdout_set(load(base), ycol)
        tr = ~df["month"].isin(ho)
        ho_m = df["month"].isin(ho)
        y = df[ycol].astype(int).to_numpy()
        # full-history model
        pipe = Pipeline([("pre", pre()), ("clf", make_model("hist", y[tr.to_numpy()]))])
        pipe.fit(df.loc[tr, NUM + CAT], y[tr.to_numpy()])
        p_full = pipe.predict_proba(df.loc[ho_m, NUM + CAT])[:, 1]
        yho = y[ho_m.to_numpy()]
        # recent-window model (last 24 months before holdout)
        trm = pd.to_datetime(df.loc[tr, "month"])
        cut = trm.max() - pd.DateOffset(months=23)
        rec = tr & (df["month"] >= cut)
        pipe2 = Pipeline([("pre", pre()), ("clf", make_model("hist", y[rec.to_numpy()]))])
        pipe2.fit(df.loc[rec, NUM + CAT], y[rec.to_numpy()])
        p_rec = pipe2.predict_proba(df.loc[ho_m, NUM + CAT])[:, 1]
        # recalibration (Platt) fitted on the last pre-holdout block
        val_months = set(sorted(df.loc[tr, "month"].unique())[-HOLDOUT_MONTHS:])
        vmask = df["month"].isin(val_months)
        tmask = tr & ~vmask
        pipe3 = Pipeline([("pre", pre()), ("clf", make_model("hist", y[tmask.to_numpy()]))])
        pipe3.fit(df.loc[tmask, NUM + CAT], y[tmask.to_numpy()])
        pv = pipe3.predict_proba(df.loc[vmask, NUM + CAT])[:, 1].reshape(-1, 1)
        cal = LogisticRegression().fit(pv, y[vmask.to_numpy()])
        p_cal = cal.predict_proba(p_full.reshape(-1, 1))[:, 1]
        rows.append({"task": task, "model": "full_history", "n_holdout": int(ho_m.sum()),
                     "pos": int(yho.sum()),
                     "roc_auc": round(roc_auc_score(yho, p_full), 4),
                     "brier": round(brier_score_loss(yho, p_full), 4)})
        rows.append({"task": task, "model": "recent_24m", "n_holdout": int(ho_m.sum()),
                     "pos": int(yho.sum()),
                     "roc_auc": round(roc_auc_score(yho, p_rec), 4) if len(np.unique(yho)) > 1 else np.nan,
                     "brier": round(brier_score_loss(yho, p_rec), 4)})
        rows.append({"task": task, "model": "platt_recalibrated", "n_holdout": int(ho_m.sum()),
                     "pos": int(yho.sum()),
                     "roc_auc": round(roc_auc_score(yho, p_cal), 4),
                     "brier": round(brier_score_loss(yho, p_cal), 4)})
    out = pd.DataFrame(rows)
    out.to_csv(REP / "phase6b_window_recalibration.csv", index=False)
    print("[window/recalibration]\n", out.to_string(index=False))
    return out


def do_outlier_sensitivity():
    rows = []
    for task in ["T1_usd_y1", "T3_nominal_y1"]:
        set_current_task(task)
        base, ycol = TASKS[task]
        df0 = load(base)
        df0 = df0[df0[f"labelable_{ycol}"]].copy()
        ho, _ = holdout_set(load(base), ycol)
        ret_cols = ["ret", "ret_lag1", "ret_lag2", "ret_roll3", "ret_z_cur"]
        n_out = int((df0[ret_cols].abs() > 1.0).any(axis=1).sum())
        base_auc, _, _ = _auc_holdout(df0, ycol, ho, NUM, CAT)
        d = df0.copy()
        for c in ret_cols:
            lo, hi = d[c].quantile([0.01, 0.99])
            d[c] = d[c].clip(lo, hi)
        w_auc, _, _ = _auc_holdout(d, ycol, ho, NUM, CAT)
        rows.append({"task": task, "variant": "none", "roc_auc": base_auc})
        rows.append({"task": task, "variant": "winsor_1_99", "roc_auc": w_auc,
                     "delta": round(w_auc - base_auc, 4),
                     "n_rows_with_return_gt1": n_out})
    out = pd.DataFrame(rows)
    out.to_csv(REP / "phase6b_outlier_sensitivity.csv", index=False)
    print("[outlier]\n", out.to_string(index=False))
    return out


def do_importance_stability():
    rows = []
    for task in ["T1_usd_y1", "T2_usd_y2"]:
        set_current_task(task)
        base, ycol = TASKS[task]
        df = load(base)
        df = df[df[f"labelable_{ycol}"]].copy()
        months = sorted(df["month"].unique())
        n = len(months)
        edges = np.linspace(int(n * 0.5), n, 4).astype(int)
        y = df[ycol].astype(int).to_numpy()
        per_fold = []
        for i in range(len(edges) - 1):
            val_months = set(months[edges[i]:edges[i + 1]])
            train_months = set(months[:edges[i]])
            tr = df["month"].isin(train_months)
            va = df["month"].isin(val_months)
            if tr.sum() < 50 or va.sum() < 30 or len(np.unique(y[tr.to_numpy()])) < 2:
                continue
            pipe = Pipeline([("pre", pre()), ("clf", make_model("xgb", y[tr.to_numpy()]))])
            pipe.fit(df.loc[tr, NUM + CAT], y[tr])
            r = permutation_importance(pipe, df.loc[va, NUM + CAT], y[va.to_numpy()],
                                       scoring="roc_auc", n_repeats=10, random_state=SEED, n_jobs=4)
            per_fold.append(pd.Series(r.importances_mean, index=NUM + CAT))
        if not per_fold:
            continue
        M = pd.concat(per_fold, axis=1)
        summ = pd.DataFrame({"mean": M.mean(axis=1), "std_across_folds": M.std(axis=1),
                             "n_folds": M.notna().sum(axis=1),
                             "rank_mean": M.rank(ascending=False).mean(axis=1)})
        summ = summ.sort_values("mean", ascending=False)
        summ.insert(0, "task", task)
        rows.append(summ.reset_index().rename(columns={"index": "feature"}))
    out = pd.concat(rows, ignore_index=True) if rows else pd.DataFrame()
    out.to_csv(REP / "phase6b_importance_stability.csv", index=False)
    print("[importance stability]\n", out.round(4).to_string(index=False))
    return out


if __name__ == "__main__":
    do_bootstrap()
    do_oof_by_group()
    do_threshold_sensitivity()
    do_feature_exclusion()
    do_window_and_recalibration()
    do_outlier_sensitivity()
    do_importance_stability()
    print("\nPhase 6b complete.")
