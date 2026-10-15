"""Chapter 4 figures - generated from real artefacts.

Reads artifacts/ and reports/ and writes publication-quality PNGs into figures/.
Every plot is derived from real results; no values are hard-coded except axis labels.

Conventions (revised):
  * One plot per image (a single Axes per PNG).
  * Every image carries a title, x label, y label and a legend.
  * File names encode the placement: fig<chapter>.<section>[.<subsection>][.<index>]_<slug>.png
    e.g. fig4.4.1.5_roc_T1_usd_y1.png -> Figure 4.4.1.5.

Usage: python src/figures_chapter4.py
"""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.calibration import calibration_curve
from sklearn.metrics import (precision_recall_curve, roc_curve)

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "artifacts"
REP = ROOT / "reports"
FIG = ROOT / "figures"
FIG.mkdir(exist_ok=True)

TASKS = ["T1_usd_y1", "T2_usd_y2", "T3_nominal_y1", "T4_nominal_y2"]
# Display name and figure-index for each task, used in titles and file names.
DISP = {"T1_usd_y1": "T1 (USD, Y1)", "T2_usd_y2": "T2 (USD, Y2)",
        "T3_nominal_y1": "T3 (nominal, Y1)", "T4_nominal_y2": "T4 (nominal, Y2)"}
TIDX = {"T1_usd_y1": 1, "T2_usd_y2": 2, "T3_nominal_y1": 3, "T4_nominal_y2": 4}
MODELS = ["majority", "persistence", "logistic_elasticnet",
          "hist_gradient_boosting", "xgboost"]
MLABEL = {"majority": "Majority", "persistence": "Persistence",
          "logistic_elasticnet": "Logistic (EN)", "hist_gradient_boosting": "Hist GBM",
          "xgboost": "XGBoost"}
COLORS = {"majority": "#999999", "persistence": "#c9a227",
          "logistic_elasticnet": "#3b7dd8", "hist_gradient_boosting": "#2ca02c",
          "xgboost": "#d62728"}
BEST = {"T1_usd_y1": "xgboost", "T2_usd_y2": "hist_gradient_boosting",
        "T3_nominal_y1": "xgboost", "T4_nominal_y2": "hist_gradient_boosting"}

plt.rcParams.update({"figure.dpi": 150, "savefig.dpi": 150, "font.size": 9,
                     "axes.grid": True, "grid.alpha": 0.3})


def save(fig, name):
    fig.tight_layout()
    fig.savefig(FIG / name)
    plt.close(fig)
    print("figure:", name)


def load_metrics():
    return pd.read_csv(ART / "metrics_all_tasks.csv")


def preds(task):
    return pd.read_parquet(ART / f"preds_{task}.parquet")


def target_col(task):
    return "y1" if task.endswith("y1") else "y2"


# ---------------------------------------------------------------- CV vs holdout bars
def fig_cv_vs_holdout():
    m = load_metrics()
    x = np.arange(len(MODELS)); w = 0.38
    for task in TASKS:
        cv = m[(m.task == task) & (m.split == "cv_pooled")].set_index("model")
        ho = m[(m.task == task) & (m.split == "holdout")].set_index("model")
        cvv = [cv.loc[md, "roc_auc"] if md in cv.index else np.nan for md in MODELS]
        hov = [ho.loc[md, "roc_auc"] if md in ho.index else np.nan for md in MODELS]
        fig, ax = plt.subplots(figsize=(8, 4.5))
        ax.bar(x - w / 2, cvv, w, label="Expanding-window CV (pooled)",
               color="#9ecae1", edgecolor="k", lw=0.4)
        ax.bar(x + w / 2, hov, w, label="Forward holdout",
               color="#3182bd", edgecolor="k", lw=0.4)
        ax.axhline(0.5, color="red", ls="--", lw=1, label="Chance (0.5)")
        ax.set_xticks(x)
        ax.set_xticklabels([MLABEL[md] for md in MODELS], rotation=25, ha="right")
        ax.set_ylim(0, 1)
        ax.set_title(f"Figure 4.4.1.{TIDX[task]}: ROC-AUC, CV versus holdout - {DISP[task]}")
        ax.set_xlabel("Model"); ax.set_ylabel("ROC-AUC")
        ax.legend()
        save(fig, f"fig4.4.1.{TIDX[task]}_cv_vs_holdout_{task}.png")


# ---------------------------------------------------------------- ROC curves (one per task)
def fig_roc():
    for task in TASKS:
        d = preds(task); y = d[target_col(task)].to_numpy()
        fig, ax = plt.subplots(figsize=(6.5, 5))
        for mdl in MODELS:
            col = f"p_{mdl}"
            if col not in d or len(np.unique(y)) < 2:
                continue
            fpr, tpr, _ = roc_curve(y, d[col].to_numpy())
            ax.plot(fpr, tpr, color=COLORS[mdl], label=MLABEL[mdl], lw=1.6)
        ax.plot([0, 1], [0, 1], "k--", lw=0.9, label="Chance")
        ax.set_title(f"Figure 4.4.1.{4 + TIDX[task]}: ROC curve - {DISP[task]} (holdout)")
        ax.set_xlabel("False positive rate"); ax.set_ylabel("True positive rate")
        ax.legend(loc="lower right")
        save(fig, f"fig4.4.1.{4 + TIDX[task]}_roc_{task}.png")


# ---------------------------------------------------------------- PR curves (one per task)
def fig_pr():
    for task in TASKS:
        d = preds(task); y = d[target_col(task)].to_numpy()
        fig, ax = plt.subplots(figsize=(6.5, 5))
        for mdl in MODELS:
            col = f"p_{mdl}"
            if col not in d or len(np.unique(y)) < 2:
                continue
            pr, rc, _ = precision_recall_curve(y, d[col].to_numpy())
            ax.plot(rc, pr, color=COLORS[mdl], label=MLABEL[mdl], lw=1.6)
        base = float(y.mean())
        ax.axhline(base, color="grey", ls="--", lw=1, label=f"Baseline prevalence ({base:.2f})")
        ax.set_title(f"Figure 4.4.1.{8 + TIDX[task]}: Precision-Recall curve - {DISP[task]} (holdout)")
        ax.set_xlabel("Recall"); ax.set_ylabel("Precision")
        ax.legend(loc="upper right")
        save(fig, f"fig4.4.1.{8 + TIDX[task]}_pr_{task}.png")


# ---------------------------------------------------------------- bootstrap CIs
def fig_bootstrap():
    b = pd.read_csv(REP / "phase6b_bootstrap_ci.csv")
    b = b[b.model.isin(["xgb", "hist"])].copy()
    b["lab"] = b.apply(
        lambda r: f"{DISP[r.task]}\n{MLABEL['xgboost' if r.model == 'xgb' else 'hist_gradient_boosting']}",
        axis=1)
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ypos = np.arange(len(b))
    ax.errorbar(b.roc_auc, ypos,
                xerr=[b.roc_auc - b.ci95_market_lo, b.ci95_market_hi - b.roc_auc],
                fmt="o", color="#3182bd", ecolor="#08519c", capsize=4, lw=1.5,
                label="Holdout AUC (95% CI)")
    ax.axvline(0.5, color="red", ls="--", lw=1, label="Chance (0.5)")
    ax.set_yticks(ypos); ax.set_yticklabels(b.lab, fontsize=8)
    ax.set_title("Figure 4.4.2.1: Holdout AUC with market-clustered bootstrap CIs")
    ax.set_xlabel("ROC-AUC (forward holdout)"); ax.set_ylabel("Task and best model")
    ax.legend(); ax.invert_yaxis()
    save(fig, "fig4.4.2.1_bootstrap_ci.png")


# ---------------------------------------------------------------- confusion matrices (one per task)
def fig_confusion_matrices():
    m = load_metrics()
    ho = m[m.split == "holdout"]
    for task in TASKS:
        row = ho[(ho.task == task) & (ho.model == BEST[task])].iloc[0]
        cm = np.array([[row.tn, row.fp], [row.fn, row.tp]], dtype=float)
        fig, ax = plt.subplots(figsize=(5.2, 4.8))
        im = ax.imshow(cm, cmap="Blues")
        for i in range(2):
            for j in range(2):
                ax.text(j, i, f"{int(cm[i, j])}", ha="center", va="center",
                        color="white" if cm[i, j] > cm.max() / 2 else "black",
                        fontsize=14, fontweight="bold")
        ax.set_xticks([0, 1]); ax.set_yticks([0, 1])
        ax.set_xticklabels(["Predicted negative", "Predicted positive"])
        ax.set_yticklabels(["Actual negative", "Actual positive"])
        ax.set_title(f"Figure 4.4.3.{TIDX[task]}: Confusion matrix - {DISP[task]}\n"
                     f"{MLABEL[BEST[task]]} (holdout, threshold={row.threshold:.2f})")
        ax.set_xlabel("Predicted class"); ax.set_ylabel("Actual class")
        ax.grid(False)
        cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
        cbar.set_label("Cell count (legend)")
        save(fig, f"fig4.4.3.{TIDX[task]}_confusion_{task}.png")


# ---------------------------------------------------------------- calibration (one per task)
def fig_calibration():
    for task in TASKS:
        d = preds(task); y = d[target_col(task)].to_numpy()
        fig, ax = plt.subplots(figsize=(6.5, 5))
        for mdl in ["logistic_elasticnet", "hist_gradient_boosting", "xgboost"]:
            col = f"p_{mdl}"
            if col not in d or len(np.unique(y)) < 2:
                continue
            try:
                frac, mean = calibration_curve(y, d[col].to_numpy(), n_bins=6,
                                               strategy="quantile")
            except Exception:
                continue
            ax.plot(mean, frac, "o-", color=COLORS[mdl], label=MLABEL[mdl], lw=1.2, ms=4)
        ax.plot([0, 1], [0, 1], "k--", lw=0.9, label="Perfect calibration")
        ax.set_title(f"Figure 4.4.4.{TIDX[task]}: Calibration - {DISP[task]} (holdout)")
        ax.set_xlabel("Mean predicted probability"); ax.set_ylabel("Observed frequency")
        ax.legend(loc="upper left")
        save(fig, f"fig4.4.4.{TIDX[task]}_calibration_{task}.png")


# ---------------------------------------------------------------- lead-lag
def fig_lead_lag():
    d = pd.read_csv(REP / "phase6_lead_lag.csv")
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    for base, col in [("usdprice", "#3182bd"), ("nominal", "#e6550d")]:
        s = d[d.base == base].sort_values("rain_lag_months")
        ax.plot(s.rain_lag_months, s.pearson_r, "o-", color=col, label=f"{base} (Pearson)")
        ax.plot(s.rain_lag_months, s.spearman_r, "s--", color=col, alpha=0.6,
                label=f"{base} (Spearman)")
    ax.axhline(0, color="black", lw=0.8)
    ax.set_xticks([0, 1, 2, 3])
    ax.set_title("Figure 4.5.1: Rainfall anomaly versus price return by lead lag")
    ax.set_xlabel("Rainfall lead (months)"); ax.set_ylabel("Correlation with next-month return")
    ax.legend(fontsize=8)
    save(fig, "fig4.5.1_lead_lag.png")


# ---------------------------------------------------------------- permutation importance (one per task)
def fig_importance():
    for task in ["T1_usd_y1", "T2_usd_y2"]:
        d = pd.read_csv(ART / f"perm_importance_{task}.csv").head(10).sort_values("mean")
        fig, ax = plt.subplots(figsize=(7, 5))
        ax.barh(d.feature, d["mean"], xerr=d["std"], color="#3182bd",
                edgecolor="k", lw=0.4, error_kw=dict(lw=0.8, ecolor="#555555"),
                label="Permutation importance (mean +/- SD)")
        ax.axvline(0, color="black", lw=0.8)
        ax.set_title(f"Figure 4.6.{TIDX[task]}: Permutation importance - {DISP[task]} (holdout)")
        ax.set_xlabel("Mean ROC-AUC decrease"); ax.set_ylabel("Feature")
        ax.legend(loc="lower right", fontsize=8)
        save(fig, f"fig4.6.{TIDX[task]}_importance_{task}.png")


# ---------------------------------------------------------------- threshold sensitivity - prevalence
def fig_threshold_prevalence():
    prev = pd.read_csv(REP / "phase6_threshold_sensitivity.csv")
    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    for base, col in [("usdprice", "#3182bd"), ("nominal", "#e6550d")]:
        for tgt, ls in [("y1", "-"), ("y2", "--")]:
            s = prev[(prev.base == base) & (prev.target == tgt)]
            ax.plot(s.threshold, s.prevalence_pct, ls, color=col, marker="o", ms=3,
                    label=f"{base} {tgt}")
    ax.set_title("Figure 4.7.1: Label prevalence versus threshold")
    ax.set_xlabel("Stress threshold"); ax.set_ylabel("Positive prevalence (%)")
    ax.legend(fontsize=8)
    save(fig, "fig4.7.1_threshold_prevalence.png")


# ---------------------------------------------------------------- threshold sensitivity - holdout AUC
def fig_threshold_auc():
    mdl = pd.read_csv(REP / "phase6b_threshold_model_sensitivity.csv")
    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    for task, col in [("T1_usd_y1", "#d62728"), ("T2_usd_y2", "#2ca02c"),
                      ("T3_nominal_y1", "#9467bd"), ("T4_nominal_y2", "#8c564b")]:
        s = mdl[mdl.task == task]
        ax.plot(s.threshold, s.holdout_roc_auc, "o-", color=col, label=DISP[task], ms=3)
    ax.axhline(0.5, color="red", ls="--", lw=1, label="Chance (0.5)")
    ax.set_title("Figure 4.7.2: Holdout ROC-AUC versus threshold")
    ax.set_xlabel("Stress threshold"); ax.set_ylabel("Holdout ROC-AUC")
    ax.legend(fontsize=8)
    save(fig, "fig4.7.2_threshold_holdout_auc.png")


# ---------------------------------------------------------------- feature exclusion
def fig_feature_exclusion():
    d = pd.read_csv(REP / "phase6b_feature_exclusion.csv").dropna(subset=["delta"])
    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    labels = [f"{DISP[r.task]}\n{r.variant}" for r in d.itertuples()]
    colors = ["#d62728" if v < 0 else "#2ca02c" for v in d.delta]
    ax.barh(labels, d.delta, color=colors, edgecolor="k", lw=0.4,
            label="AUC change (red = decrease)")
    ax.axvline(0, color="black", lw=0.8)
    ax.set_title("Figure 4.7.3: Feature-exclusion sensitivity")
    ax.set_xlabel("Change in holdout ROC-AUC versus full model"); ax.set_ylabel("Task and variant")
    ax.legend(fontsize=8)
    save(fig, "fig4.7.3_feature_exclusion.png")


# ---------------------------------------------------------------- OOF by year
def fig_oof_by_year():
    d = pd.read_csv(REP / "phase6b_oof_by_year.csv")
    fig, ax = plt.subplots(figsize=(8, 4.5))
    for task, col in [("T1_usd_y1", "#d62728"), ("T2_usd_y2", "#2ca02c")]:
        s = d[d.task == task].sort_values("group")
        ax.plot(s.group.astype(str), s.roc_auc, "o-", color=col, label=DISP[task], ms=4)
    ax.axhline(0.5, color="red", ls="--", lw=1, label="Chance (0.5)")
    ax.set_title("Figure 4.7.4: Out-of-fold AUC by year")
    ax.set_xlabel("Year"); ax.set_ylabel("Out-of-fold ROC-AUC")
    ax.legend(fontsize=8)
    save(fig, "fig4.7.4_oof_by_year.png")


def main():
    print("CV vs holdout..."); fig_cv_vs_holdout()
    print("ROC curves..."); fig_roc()
    print("PR curves..."); fig_pr()
    print("bootstrap..."); fig_bootstrap()
    print("confusion matrices..."); fig_confusion_matrices()
    print("calibration..."); fig_calibration()
    print("lead-lag..."); fig_lead_lag()
    print("importance..."); fig_importance()
    print("threshold prevalence..."); fig_threshold_prevalence()
    print("threshold AUC..."); fig_threshold_auc()
    print("feature exclusion..."); fig_feature_exclusion()
    print("OOF by year..."); fig_oof_by_year()
    print("All Chapter 4 figures written to figures/")


if __name__ == "__main__":
    main()
