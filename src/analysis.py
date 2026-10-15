"""Phase 6 - statistical/robustness analysis + Phase 7 figures.

- rainfall-price lead-lag correlations with sample sizes and p-values
- target-threshold sensitivity (prevalence)
- holdout permutation importance for the tree models
- model-comparison and calibration figures
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats
from sklearn.calibration import calibration_curve
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.inspection import permutation_importance
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.metrics import roc_auc_score, roc_curve, precision_recall_curve, average_precision_score
from xgboost import XGBClassifier
import yaml

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data_processed"
ART = ROOT / "artifacts"
REP = ROOT / "reports"
FIG = ROOT / "figures"
CFG = yaml.safe_load((ROOT / "config" / "targets.yml").read_text(encoding="utf-8"))
SEED = int(CFG["seed"])
NUM = ["ret_z_cur", "ret_lag1", "ret_lag2", "ret_roll3", "spi", "peer_count",
       "rain_anom_z", "rain_anom_lag1", "rain_anom_lag2", "rain_anom_lag3",
       "rain_roll3_mm", "month_sin", "month_cos", "log_population", "interaction"]
CAT = ["category", "currency"]


def pre():
    return ColumnTransformer([
        ("num", Pipeline([("imp", SimpleImputer(strategy="median")), ("sc", StandardScaler())]), NUM),
        ("cat", Pipeline([("imp", SimpleImputer(strategy="most_frequent")),
                          ("oh", OneHotEncoder(handle_unknown="ignore"))]), CAT)])


def prep(df):
    df = df.copy()
    df["interaction"] = df["ret_z_cur"] * df["rain_anom_z"]
    df[NUM] = df[NUM].replace([np.inf, -np.inf], np.nan)
    return df


# ------------------------------------------------------------ lead-lag
def lead_lag():
    rows = []
    for base in ["usdprice", "nominal_within_currency"]:
        df = prep(pd.read_parquet(OUT / f"panel_{base}.parquet"))
        for lag, col in [(0, "rain_anom_z"), (1, "rain_anom_lag1"),
                         (2, "rain_anom_lag2"), (3, "rain_anom_lag3")]:
            sub = df[[col, "ret"]].replace([np.inf, -np.inf], np.nan).dropna()
            if len(sub) > 10 and sub[col].std() > 0:
                r, p = stats.pearsonr(sub[col], sub["ret"])
                rs, ps = stats.spearmanr(sub[col], sub["ret"])
            else:
                r = p = rs = ps = np.nan
            rows.append({"base": base, "rain_lag_months": lag, "n": len(sub),
                         "pearson_r": r, "p_value": p, "spearman_r": rs})
    out = pd.DataFrame(rows)
    out.to_csv(REP / "phase6_lead_lag.csv", index=False)
    print(out.round(4).to_string(index=False))
    return out


# ------------------------------------------------------------ threshold sensitivity
def threshold_sensitivity():
    rows = []
    for base in ["usdprice", "nominal_within_currency"]:
        df = pd.read_parquet(OUT / f"panel_{base}.parquet")
        z = df["z_next"].replace([np.inf, -np.inf], np.nan)
        for thr in CFG["target_return_stress"]["threshold_grid_sd"]:
            ok = z.notna()
            rows.append({"base": base, "target": "y1", "threshold": thr,
                         "n_labelable": int(ok.sum()),
                         "prevalence_pct": round(100 * (z[ok] >= thr).mean(), 3)})
        spi = df["next_spi"].replace([np.inf, -np.inf], np.nan)
        for d in CFG["target_peer_stress"]["threshold_grid_spi"]:
            ok = spi.notna()
            rows.append({"base": base, "target": "y2", "threshold": d,
                         "n_labelable": int(ok.sum()),
                         "prevalence_pct": round(100 * (spi[ok] >= d).mean(), 3)})
    out = pd.DataFrame(rows)
    out.to_csv(REP / "phase6_threshold_sensitivity.csv", index=False)
    print(out.to_string(index=False))
    return out


# ------------------------------------------------------------ permutation importance
def permutation_importance_holdout(task, base, ycol, model_name="xgboost"):
    df = prep(pd.read_parquet(OUT / f"panel_{base}.parquet"))
    df = df[df[f"labelable_{ycol}"]].copy()
    df["month"] = pd.to_datetime(df["month"])
    months = sorted(df["month"].unique())
    holdout = set(months[-int(CFG["validation"]["holdout_months"]):])
    tr = (~df["month"].isin(holdout)).to_numpy()
    ho = df["month"].isin(holdout).to_numpy()
    Xf, yv = df[NUM + CAT], df[ycol].astype(int).to_numpy()
    pos_w = len(yv[tr][yv[tr] == 0]) / max(len(yv[tr][yv[tr] == 1]), 1)
    if model_name == "xgboost":
        clf = XGBClassifier(n_estimators=300, learning_rate=0.05, max_depth=4, subsample=0.8,
                            colsample_bytree=0.8, reg_lambda=1.0, random_state=SEED,
                            eval_metric="logloss", scale_pos_weight=pos_w, n_jobs=4)
    else:
        clf = HistGradientBoostingClassifier(learning_rate=0.05, max_iter=300, max_leaf_nodes=15,
                                             min_samples_leaf=30, l2_regularization=1.0, random_state=SEED)
    pipe = Pipeline([("pre", pre()), ("clf", clf)])
    pipe.fit(Xf[tr], yv[tr])
    r = permutation_importance(pipe, Xf[ho], yv[ho], scoring="roc_auc",
                               n_repeats=20, random_state=SEED, n_jobs=4)
    imp = pd.DataFrame({"feature": NUM + CAT, "mean": r.importances_mean, "std": r.importances_std})
    imp = imp.sort_values("mean", ascending=False)
    imp.to_csv(ART / f"perm_importance_{task}.csv", index=False)
    print(f"\nperm importance {task} ({model_name}):")
    print(imp.round(4).to_string(index=False))
    return imp


# ------------------------------------------------------------ figures
def figures():
    m = pd.read_csv(ART / "metrics_all_tasks.csv")
    for task in m["task"].unique():
        sub = m[m["task"] == task]
        piv = sub.pivot_table(index="model", columns="split", values="roc_auc")
        piv = piv.reindex(["majority", "persistence", "logistic_elasticnet",
                           "hist_gradient_boosting", "xgboost"])
        ax = piv.plot(kind="bar", figsize=(9, 4.2), color=["#2b6cb0", "#c05621"])
        ax.set_title(f"ROC-AUC by model - {task}"); ax.set_ylabel("ROC-AUC")
        ax.axhline(0.5, color="grey", ls="--", lw=1)
        plt.xticks(rotation=20, ha="right"); plt.tight_layout()
        plt.savefig(FIG / f"phase7_rocauc_{task}.png", dpi=150); plt.close()

    # calibration + ROC/PR for the best Y2 (usd) model on holdout
    df = prep(pd.read_parquet(OUT / "panel_usdprice.parquet"))
    df = df[df["labelable_y2"]].copy()
    df["month"] = pd.to_datetime(df["month"])
    months = sorted(df["month"].unique())
    ho = df["month"].isin(set(months[-12:])).to_numpy()
    tr = ~ho
    Xf, yv = df[NUM + CAT], df["y2"].astype(int).to_numpy()
    pipe = Pipeline([("pre", pre()), ("clf", HistGradientBoostingClassifier(
        learning_rate=0.05, max_iter=300, max_leaf_nodes=15, min_samples_leaf=30,
        l2_regularization=1.0, random_state=SEED))])
    pipe.fit(Xf[tr], yv[tr])
    p = pipe.predict_proba(Xf[ho])[:, 1]
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.3))
    fpr, tpr, _ = roc_curve(yv[ho], p)
    axes[0].plot(fpr, tpr, color="#2b6cb0"); axes[0].plot([0, 1], [0, 1], "grey", ls="--")
    axes[0].set_title(f"ROC (hist-GBM, Y2 holdout)\nAUC={roc_auc_score(yv[ho], p):.3f}")
    axes[0].set_xlabel("FPR"); axes[0].set_ylabel("TPR")
    pr, rc, _ = precision_recall_curve(yv[ho], p)
    axes[1].plot(rc, pr, color="#2f855a")
    axes[1].set_title(f"Precision-Recall\nAP={average_precision_score(yv[ho], p):.3f}")
    axes[1].set_xlabel("recall"); axes[1].set_ylabel("precision")
    frac, meanp = calibration_curve(yv[ho], p, n_bins=8, strategy="quantile")
    axes[2].plot(meanp, frac, "o-", color="#c05621"); axes[2].plot([0, 1], [0, 1], "grey", ls="--")
    axes[2].set_title("Calibration (hist-GBM, Y2 holdout)")
    axes[2].set_xlabel("predicted probability"); axes[2].set_ylabel("observed frequency")
    plt.tight_layout(); plt.savefig(FIG / "phase7_y2_diagnostics.png", dpi=150); plt.close()
    print("figures written")


if __name__ == "__main__":
    lead_lag()
    threshold_sensitivity()
    permutation_importance_holdout("T1_usd_y1", "usdprice", "y1", "xgboost")
    permutation_importance_holdout("T2_usd_y2", "usdprice", "y2", "hist_gradient_boosting")
    figures()
