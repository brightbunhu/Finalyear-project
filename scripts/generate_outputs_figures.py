"""Generate high-resolution (300 DPI) publication figures and structured metrics into outputs/."""
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix, roc_curve, precision_recall_curve, auc

ROOT = Path(__file__).resolve().parents[1]
OUT_FIG = ROOT / "outputs" / "figures"
OUT_MET = ROOT / "outputs" / "metrics"
OUT_LOG = ROOT / "outputs" / "logs"
ART = ROOT / "artifacts"
REP = ROOT / "reports"
PROC = ROOT / "data_processed"

OUT_FIG.mkdir(parents=True, exist_ok=True)
OUT_MET.mkdir(parents=True, exist_ok=True)
OUT_LOG.mkdir(parents=True, exist_ok=True)

# Set global styles
sns.set_theme(style="whitegrid", font="sans-serif")
plt.rcParams.update({
    "font.size": 11,
    "axes.labelsize": 12,
    "axes.titlesize": 13,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "legend.fontsize": 10,
    "figure.titlesize": 14,
    "figure.dpi": 300,
    "savefig.dpi": 300
})

# Load datasets
panel_usd = pd.read_parquet(PROC / "panel_usdprice.parquet")
panel_nom = pd.read_parquet(PROC / "panel_nominal_within_currency.parquet")
metrics_all = pd.read_csv(ART / "metrics_all_tasks.csv")

# -------------------------------------------------------------
# 1. Figure 4.1: Distribution of Target Y1 and Target Y2 (Class Imbalance)
# -------------------------------------------------------------
fig, axes = plt.subplots(1, 2, figsize=(12, 5), dpi=300)

y1_counts = panel_usd["y1"].dropna().value_counts().sort_index()
y2_counts = panel_usd["y2"].dropna().value_counts().sort_index()

sns.barplot(x=["Normal (0)", "Stress (1)"], y=y1_counts.values, ax=axes[0], palette=["#4a5568", "#e53e3e"])
axes[0].set_title("Target Y1: Standardised Return Stress (SD >= 1.0)\nPrevalence = 14.96% (812 / 5,429)")
axes[0].set_ylabel("Observation Count")
axes[0].set_xlabel("Class Label")
for i, v in enumerate(y1_counts.values):
    axes[0].text(i, v + 80, f"{v:,} ({v/sum(y1_counts.values):.1%})", ha="center", fontweight="bold")

sns.barplot(x=["Normal (0)", "Stress (1)"], y=y2_counts.values, ax=axes[1], palette=["#4a5568", "#dd6b20"])
axes[1].set_title("Target Y2: Peer-Relative Spatial Stress (SPI >= 1.20)\nPrevalence = 16.30% (2,060 / 12,635)")
axes[1].set_ylabel("Observation Count")
axes[1].set_xlabel("Class Label")
for i, v in enumerate(y2_counts.values):
    axes[1].text(i, v + 150, f"{v:,} ({v/sum(y2_counts.values):.1%})", ha="center", fontweight="bold")

plt.suptitle("Figure 4.1: Target Class Imbalance Distribution in Food Price Stress Datasets", y=1.03)
plt.tight_layout()
plt.savefig(OUT_FIG / "fig4_1_class_distribution.png", bbox_inches="tight")
plt.close()
print("Saved fig4_1_class_distribution.png")

# -------------------------------------------------------------
# 2. Figure 4.2a & 4.2b: Currency & Commodity Category Distribution Pie Charts
# -------------------------------------------------------------
# Pie Chart: Currency
fig, ax = plt.subplots(figsize=(7, 7), dpi=300)
cur_counts = panel_usd["currency"].value_counts()
colors = ["#2b6cb0", "#319795", "#d69e2e", "#805ad5"]
wedges, texts, autotexts = ax.pie(
    cur_counts.values,
    labels=cur_counts.index,
    autopct="%1.1f%%",
    startangle=140,
    colors=colors[:len(cur_counts)],
    wedgeprops=dict(width=0.6, edgecolor="w", linewidth=2),
    pctdistance=0.75
)
plt.setp(autotexts, size=11, weight="bold", color="white")
ax.set_title("Figure 4.2a: Currency Breakdown of Market Quotes (USD vs. Local Currency)", pad=20)
ax.legend(cur_counts.index, title="Currency Regime", loc="upper right")
plt.tight_layout()
plt.savefig(OUT_FIG / "fig4_2a_currency_distribution.png", bbox_inches="tight")
plt.close()
print("Saved fig4_2a_currency_distribution.png")

# Pie Chart: Commodity Categories
fig, ax = plt.subplots(figsize=(8, 7), dpi=300)
cat_counts = panel_usd["category"].value_counts()
cat_colors = ["#2b6cb0", "#4299e1", "#ed8936", "#48bb78", "#9f7aea"]
wedges, texts, autotexts = ax.pie(
    cat_counts.values,
    labels=[c.title() for c in cat_counts.index],
    autopct="%1.1f%%",
    startangle=90,
    colors=cat_colors[:len(cat_counts)],
    wedgeprops=dict(width=0.6, edgecolor="w", linewidth=2),
    pctdistance=0.75
)
plt.setp(autotexts, size=10, weight="bold", color="white")
ax.set_title("Figure 4.2b: Commodity Category Representation in Cleaned Panel", pad=20)
ax.legend([c.title() for c in cat_counts.index], title="Category", loc="upper right", bbox_to_anchor=(1.15, 1))
plt.tight_layout()
plt.savefig(OUT_FIG / "fig4_2b_category_distribution.png", bbox_inches="tight")
plt.close()
print("Saved fig4_2b_category_distribution.png")

# -------------------------------------------------------------
# 3. Figure 4.3: Data Coverage Over Time
# -------------------------------------------------------------
cov = panel_usd.groupby(panel_usd["month"].dt.to_period("M").dt.to_timestamp()).size()
fig, ax = plt.subplots(figsize=(12, 5), dpi=300)
ax.plot(cov.index, cov.values, color="#2b6cb0", lw=2.2, label="Monthly Food Price Quotes")
ax.fill_between(cov.index, 0, cov.values, color="#2b6cb0", alpha=0.15)
ax.axvline(pd.Timestamp("2024-06-01"), color="#c53030", ls="--", lw=1.8, label="Forward Holdout Split (Final 12 Months)")
ax.set_title("Figure 4.3: Temporal Data Coverage and Sample Size Over Time (2010–2026)")
ax.set_ylabel("Number of Market-Commodity Observations")
ax.set_xlabel("Calendar Month")
ax.legend(loc="upper left")
plt.tight_layout()
plt.savefig(OUT_FIG / "fig4_3_data_coverage_over_time.png", bbox_inches="tight")
plt.close()
print("Saved fig4_3_data_coverage_over_time.png")

# -------------------------------------------------------------
# 4. Figure 4.4: Rainfall Anomaly vs. Price Return Lead-Lag Correlation
# -------------------------------------------------------------
lead_lag_df = pd.read_csv(REP / "phase6_lead_lag.csv")
fig, ax = plt.subplots(figsize=(9, 5), dpi=300)
for base, grp in lead_lag_df.groupby("base"):
    label = "USD Price Base" if base == "usdprice" else "Nominal Within-Currency"
    marker = "o" if base == "usdprice" else "s"
    color = "#2b6cb0" if base == "usdprice" else "#c53030"
    ax.plot(grp["rain_lag_months"], grp["pearson_r"], marker=marker, lw=2, color=color, label=f"{label} (Pearson r)")
    ax.plot(grp["rain_lag_months"], grp["spearman_r"], marker=marker, lw=1.5, ls="--", color=color, alpha=0.7, label=f"{label} (Spearman rho)")

ax.axhline(0, color="gray", ls=":", lw=1)
ax.set_xticks([0, 1, 2, 3])
ax.set_xticklabels(["Lag 0 (Contemporary)", "Lag 1 (1 Month Prior)", "Lag 2 (2 Months Prior)", "Lag 3 (3 Months Prior)"])
ax.set_title("Figure 4.4: Meteorological Lead-Lag Correlation (Rainfall Anomaly vs. Food Price Return)")
ax.set_ylabel("Correlation Coefficient (r / rho)")
ax.set_xlabel("Rainfall Anomaly Lag")
ax.legend(loc="lower right")
plt.tight_layout()
plt.savefig(OUT_FIG / "fig4_4_rainfall_anomaly_vs_price_return.png", bbox_inches="tight")
plt.close()
print("Saved fig4_4_rainfall_anomaly_vs_price_return.png")

# -------------------------------------------------------------
# 5. Figure 4.5: ROC Curves (CV vs. Holdout for All Tasks)
# -------------------------------------------------------------
fig, axes = plt.subplots(2, 2, figsize=(14, 12), dpi=300)
tasks = [("T1_usd_y1", "T1: USD Price, Y1 Return Stress", axes[0, 0]),
         ("T2_usd_y2", "T2: USD Price, Y2 Peer Stress", axes[0, 1]),
         ("T3_nominal_y1", "T3: Nominal Price, Y1 Return Stress", axes[1, 0]),
         ("T4_nominal_y2", "T4: Nominal Price, Y2 Peer Stress", axes[1, 1])]

for task_name, title, ax in tasks:
    pred_path = ART / f"preds_{task_name}.parquet"
    if pred_path.exists():
        pdf = pd.read_parquet(pred_path)
        ycol = "y1" if "y1" in task_name else "y2"
        y_true = pdf[ycol].to_numpy()
        models = [("p_majority", "Majority", "#718096", ":"),
                  ("p_persistence", "Persistence", "#d69e2e", "--"),
                  ("p_logistic_elasticnet", "Logistic ElasticNet", "#3182ce", "-."),
                  ("p_hist_gradient_boosting", "Hist Gradient Boosting", "#38a169", "-"),
                  ("p_xgboost", "XGBoost", "#e53e3e", "-")]
        for pcol, mname, color, ls in models:
            if pcol in pdf.columns:
                p_score = pdf[pcol].to_numpy()
                fpr, tpr, _ = roc_curve(y_true, p_score)
                roc_score = auc(fpr, tpr)
                ax.plot(fpr, tpr, label=f"{mname} (AUC={roc_score:.3f})", color=color, ls=ls, lw=2)
    ax.plot([0, 1], [0, 1], "k--", lw=1, alpha=0.5, label="Chance (0.50)")
    ax.set_title(title, fontweight="bold")
    ax.set_xlabel("False Positive Rate (1 - Specificity)")
    ax.set_ylabel("True Positive Rate (Recall)")
    ax.legend(loc="lower right")

plt.suptitle("Figure 4.5: Out-of-Sample ROC Curves Across Forward Holdout (Tasks T1–T4)", y=1.02)
plt.tight_layout()
plt.savefig(OUT_FIG / "fig4_5_roc_curves.png", bbox_inches="tight")
plt.close()
print("Saved fig4_5_roc_curves.png")

# -------------------------------------------------------------
# 6. Figure 4.6: Precision-Recall Curves
# -------------------------------------------------------------
fig, axes = plt.subplots(2, 2, figsize=(14, 12), dpi=300)
for task_name, title, ax in tasks:
    pred_path = ART / f"preds_{task_name}.parquet"
    if pred_path.exists():
        pdf = pd.read_parquet(pred_path)
        ycol = "y1" if "y1" in task_name else "y2"
        y_true = pdf[ycol].to_numpy()
        models = [("p_persistence", "Persistence", "#d69e2e", "--"),
                  ("p_logistic_elasticnet", "Logistic ElasticNet", "#3182ce", "-."),
                  ("p_hist_gradient_boosting", "Hist Gradient Boosting", "#38a169", "-"),
                  ("p_xgboost", "XGBoost", "#e53e3e", "-")]
        for pcol, mname, color, ls in models:
            if pcol in pdf.columns:
                p_score = pdf[pcol].to_numpy()
                precision, recall, _ = precision_recall_curve(y_true, p_score)
                pr_auc = auc(recall, precision)
                ax.plot(recall, precision, label=f"{mname} (PR-AUC={pr_auc:.3f})", color=color, ls=ls, lw=2)
    baseline_prev = y_true.mean()
    ax.axhline(baseline_prev, color="k", ls=":", lw=1.2, label=f"No-skill Baseline ({baseline_prev:.1%})")
    ax.set_title(title, fontweight="bold")
    ax.set_xlabel("Recall")
    ax.set_ylabel("Precision")
    ax.legend(loc="upper right")

plt.suptitle("Figure 4.6: Precision-Recall Curves on Unseen Forward Holdout (Tasks T1–T4)", y=1.02)
plt.tight_layout()
plt.savefig(OUT_FIG / "fig4_6_pr_curves.png", bbox_inches="tight")
plt.close()
print("Saved fig4_6_pr_curves.png")

# -------------------------------------------------------------
# 7. Figure 4.7: Confusion Matrix Heatmaps for Best Models
# -------------------------------------------------------------
fig, axes = plt.subplots(2, 2, figsize=(12, 10), dpi=300)
best_models = [("T1_usd_y1", "xgboost", "T1 (USD Y1) - XGBoost (Holdout)", axes[0, 0]),
                ("T2_usd_y2", "hist_gradient_boosting", "T2 (USD Y2) - HistGBM (Holdout)", axes[0, 1]),
                ("T3_nominal_y1", "xgboost", "T3 (Nominal Y1) - XGBoost (Holdout)", axes[1, 0]),
                ("T4_nominal_y2", "hist_gradient_boosting", "T4 (Nominal Y2) - HistGBM (Holdout)", axes[1, 1])]

for task_name, model_name, title, ax in best_models:
    sub = metrics_all[(metrics_all["task"] == task_name) & (metrics_all["model"] == model_name) & (metrics_all["split"] == "holdout")]
    if not sub.empty:
        r = sub.iloc[0]
        cm = np.array([[r["tn"], r["fp"]], [r["fn"], r["tp"]]])
        sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", cbar=False, ax=ax,
                    annot_kws={"size": 14, "weight": "bold"})
        ax.set_title(f"{title}\nThreshold={r['threshold']:.2f} | F1={r['f1']:.3f} | BAcc={r['balanced_accuracy']:.3f}")
        ax.set_xticklabels(["Pred Normal (0)", "Pred Stress (1)"])
        ax.set_yticklabels(["True Normal (0)", "True Stress (1)"])
        ax.set_ylabel("True Status")
        ax.set_xlabel("Predicted Status")

plt.suptitle("Figure 4.7: Out-of-Sample Confusion Matrices at F1-Calibrated Thresholds", y=1.02)
plt.tight_layout()
plt.savefig(OUT_FIG / "fig4_7_confusion_matrices.png", bbox_inches="tight")
plt.close()
print("Saved fig4_7_confusion_matrices.png")

# -------------------------------------------------------------
# 8. Figure 4.8: Permutation Feature Importance Bar Charts
# -------------------------------------------------------------
imp1 = pd.read_csv(ART / "perm_importance_T1_usd_y1.csv").sort_values("mean", ascending=True)
imp2 = pd.read_csv(ART / "perm_importance_T2_usd_y2.csv").sort_values("mean", ascending=True)

fig, axes = plt.subplots(1, 2, figsize=(14, 8), dpi=300)

axes[0].barh(imp1["feature"], imp1["mean"], xerr=imp1["std"], color="#3182ce", capsize=3, edgecolor="k", lw=0.5)
axes[0].set_title("Task T1: Standardised Return (XGBoost)\nOut-of-Sample Holdout Importance")
axes[0].set_xlabel("Mean Drop in ROC-AUC When Permuted (+/- 1 SD)")
axes[0].axvline(0, color="gray", ls="--", lw=1)

axes[1].barh(imp2["feature"], imp2["mean"], xerr=imp2["std"], color="#38a169", capsize=3, edgecolor="k", lw=0.5)
axes[1].set_title("Task T2: Peer-Relative SPI (HistGBM)\nOut-of-Sample Holdout Importance")
axes[1].set_xlabel("Mean Drop in ROC-AUC When Permuted (+/- 1 SD)")
axes[1].axvline(0, color="gray", ls="--", lw=1)

plt.suptitle("Figure 4.8: Empirical Permutation Feature Importance on Forward Holdout (20 Repeats)", y=1.02)
plt.tight_layout()
plt.savefig(OUT_FIG / "fig4_8_feature_importance.png", bbox_inches="tight")
plt.close()
print("Saved fig4_8_feature_importance.png")

# -------------------------------------------------------------
# 9. Figure 4.9: Robustness Across Years and Currency Regimes
# -------------------------------------------------------------
oof_year = pd.read_csv(REP / "phase6b_oof_by_year.csv")
oof_cur = pd.read_csv(REP / "phase6b_oof_by_currency.csv")

fig, axes = plt.subplots(1, 2, figsize=(14, 5), dpi=300)

for task_name, grp in oof_year.groupby("task"):
    label = "T1 (USD Y1)" if task_name == "T1_usd_y1" else ("T2 (USD Y2)" if task_name == "T2_usd_y2" else task_name)
    grp_sorted = grp.sort_values("group")
    axes[0].plot(grp_sorted["group"].astype(str), grp_sorted["roc_auc"], marker="o", lw=2, label=label)

axes[0].axhline(0.5, color="gray", ls="--", lw=1, label="Chance Level (0.50)")
axes[0].set_title("Out-of-Fold ROC-AUC Across Calendar Years (2016–2026)")
axes[0].set_xlabel("Year")
axes[0].set_ylabel("ROC-AUC")
axes[0].set_ylim(0.3, 1.05)
axes[0].legend(loc="lower left", fontsize=9)

# Currency breakdown bar plot
sns.barplot(data=oof_cur, x="task", y="roc_auc", hue="group", ax=axes[1], palette=["#2b6cb0", "#e53e3e"])
axes[1].axhline(0.5, color="gray", ls="--", lw=1)
axes[1].set_title("Out-of-Fold ROC-AUC by Currency Regime (USD vs. ZWL)")
axes[1].set_xlabel("Task")
axes[1].set_ylabel("ROC-AUC")
axes[1].legend(title="Currency", loc="lower right")

plt.suptitle("Figure 4.9: Model Generalisation and Robustness Stability Across Regimes", y=1.03)
plt.tight_layout()
plt.savefig(OUT_FIG / "fig4_9_robustness_years_regimes.png", bbox_inches="tight")
plt.close()
print("Saved fig4_9_robustness_years_regimes.png")

print("All requested publication figures generated successfully in outputs/figures/")
