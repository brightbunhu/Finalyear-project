# Revised Chapter 4 — Results and Findings

> Revision notes: addresses C4.1–C4.10. Every number is from `artifacts/` and
> `reports/phase6b_*.csv`. The dissertation's fabricated values (3,571/10,459 rows;
> 17.0%/12.43%; 57.3% USD; r=−0.22; per-commodity AUCs; 68.4/21.2/10.4 risk bands;
> named higher-risk districts) are **not reproduced** and are replaced below.

## 4.1 Introduction

Results are organised by the five objectives and reported **separately for each
target** (Y1 = standardised-return stress; Y2 = peer-relative stress). All results
concern market price stress, not household food insecurity. Two price bases
(nominal-within-currency and USD) are never pooled.

## 4.2 Summary of Key Findings (by objective)

### 4.2.1 Objective 1 — Data integration
A market×commodity×currency×month panel of **20,530 food cells** (from 28,168 raw rows)
was linked to district rainfall; 327/335 priced markets were geolocated, 8 flagged as
unmatched. Traceability is preserved via `data_processed/market_admin_crosswalk.csv`.

### 4.2.2 Objective 2 — Feature construction
Features were built with trailing-only windows. The rainfall–price association is
**weak and peaks at a 1-month lead** (§4.5), not at 2 months as the dissertation
claimed. The climate–price interaction is retained but is a model diagnostic, not
evidence of a causal interaction.

### 4.2.3 Objective 3 — Model comparison (see §4.3
for the full tables)
Discrimination is **modest** (Y2) to **weak** (Y1), and XGBoost **does not dominate**
(histogram GBM wins the USD Y2 holdout; the two are tied on nominal Y2). Confidence
intervals and per-year breakdowns show the Y1 result is not distinguishable from chance
at the market level.

### 4.2.4 Objective 4 — Scoring prototype
A scoring artefact exists (`src/fit_final_model.py`, `dashboard/app.py`) that validates
input, reconstructs features, applies a versioned model (with metadata: training period,
seed) and writes a separate output. It is a technical prototype; it has **not** been
operationally validated.

<!-- FIGURE PLACEHOLDER (Chapter 4 only): insert a dashboard screenshot for this section.
     The full dashboard walkthrough lives in Chapter 5 (Figures 5.1–5.10); reserve one
     screen here if the prototype is shown inline in Chapter 4. -->
> **[Figure 4.2.4 — placeholder]** *Dashboard screenshot of the scoring prototype
> (`dashboard/app.py`): input-validation screen and a sample scoring output. Space
> reserved for the Chapter 4 discussion; live screenshots are in Chapter 5.*

### 4.2.5 Objective 5 — Commodity and district support
Commodity-level results are real (§4.6). District risk outputs are **exploratory,
model-generated classifications** and are **not** dependable early-warning predictions.

## 4.3 Descriptive Statistics

| Item | Value |
|------|-------|
| Food cells | 20,530 |
| Series (market×commodity×currency) | 3,029 (median length 4 months; 108 ≥ 24) |
| Y1 labelable / positives | 5,429 / 812 (usd, 14.96%); 819 (nominal, 15.09%) |
| Y2 labelable / positives | 12,635 / 2,060 (usd, 16.30%); 2,028 (nominal, 16.05%) |
| Currency split of food cells | ZWL ≈ 73%; USD ≈ 27% (dissertation's 57.3% USD is wrong) |
| Districts with rainfall | 90/91 (1 district has no CHIRPS pixel) |

Class imbalance (~15–16% positive) motivates PR-AUC, balanced accuracy and Brier in
addition to ROC-AUC.

**Figures 4.3.1–4.3.9** (`figures/fig4.3.*.png`). Each figure is a single plot with a
title, labelled axes and a legend.

![Figure 4.3.1 | Monthly data coverage (labelable food cells per month).](figures/fig4.3.1_monthly_coverage.png)
![Figure 4.3.2 | Label distribution of the two targets (Y1 return-stress, Y2 peer-relative stress).](figures/fig4.3.2_class_balance.png)
![Figure 4.3.3 | Positive-label prevalence by commodity category.](figures/fig4.3.3_prev_by_category.png)
![Figure 4.3.4 | Median monthly food price (USD base, log scale).](figures/fig4.3.4_median_usd_price.png)
![Figure 4.3.5 | Median nominal food price by currency (log scale); nominal series are not comparable across currency regimes.](figures/fig4.3.5_median_nominal_price.png)
![Figure 4.3.6 | Distribution of the standardised rainfall anomaly (1981–2015 climatology).](figures/fig4.3.6_rainfall_anomaly_dist.png)
![Figure 4.3.7 | Rainfall anomaly time series for example districts.](figures/fig4.3.7_rainfall_anomaly_series.png)
![Figure 4.3.8 | Distribution of standardised monthly log returns (USD base).](figures/fig4.3.8_returns_distribution.png)
![Figure 4.3.9 | Missingness of key derived features (USD panel).](figures/fig4.3.9_missingness.png)

## 4.4 Model Performance and Evaluation

> Per-target tables (C4.2). Metrics are computed on the **identical holdout rows** for
> all models of a given task. The confusion matrix uses the **F1-optimal threshold
> derived from pooled CV validation, applied unchanged to the holdout** — the holdout is
> never used to choose the threshold (C4.3).

### 4.4.1 Mean CV (expanding-window) vs forward holdout — ROC-AUC / PR-AUC

**T1 — usdprice, Y1**
| Model | CV ROC-AUC | CV PR-AUC | Holdout ROC-AUC | Holdout PR-AUC |
|-------|-----------|-----------|-----------------|----------------|
| majority | 0.500 | 0.146 | 0.500 | 0.108 |
| persistence | 0.494 | 0.148 | 0.233 | 0.079 |
| logistic (elastic-net) | 0.544 | 0.181 | 0.607 | 0.162 |
| hist GBM | 0.625 | 0.208 | 0.539 | 0.354 |
| **XGBoost** | 0.612 | 0.199 | **0.641** | 0.295 |

**T2 — usdprice, Y2**
| Model | CV ROC-AUC | CV PR-AUC | Holdout ROC-AUC | Holdout PR-AUC |
|-------|-----------|-----------|-----------------|----------------|
| majority | 0.500 | 0.165 | 0.500 | 0.147 |
| persistence | 0.569 | 0.253 | 0.711 | 0.476 |
| logistic (elastic-net) | 0.777 | 0.485 | 0.809 | 0.524 |
| **hist GBM** | 0.816 | 0.525 | **0.886** | 0.597 |
| XGBoost | 0.809 | 0.506 | 0.842 | **0.624** |

Nominal-base tasks (T3/T4) are in `artifacts/metrics_all_tasks.csv` (T3 holdout XGB
ROC-AUC 0.671; T4 holdout XGB 0.899 and hist GBM 0.897 — effectively tied). **Key honest
result:** the peer-relative target (Y2) is much more predictable than the return target
(Y1), and **XGBoost does not dominate**: hist GBM wins the USD (T2) holdout 0.886 vs
0.842, while on the nominal (T4) holdout the two are statistically indistinguishable.
The extra tuning effort on hist GBM (Optuna, §3.7) therefore does not manufacture an
XGBoost win — nor a hist-GBM one.

**Figures 4.4.1.1–4.4.1.12:** CV-versus-holdout ROC-AUC by model for T1–T4
(4.4.1.1–4.4.1.4), ROC curves (4.4.1.5–4.4.1.8) and precision-recall curves
(4.4.1.9–4.4.1.12). Each task has its own single-plot image.

![Figure 4.4.1.1 | ROC-AUC by model: expanding-window CV (pooled) versus forward holdout — T1 (USD, Y1).](figures/fig4.4.1.1_cv_vs_holdout_T1_usd_y1.png)
![Figure 4.4.1.2 | ROC-AUC by model: CV versus forward holdout — T2 (USD, Y2).](figures/fig4.4.1.2_cv_vs_holdout_T2_usd_y2.png)
![Figure 4.4.1.3 | ROC-AUC by model: CV versus forward holdout — T3 (nominal, Y1).](figures/fig4.4.1.3_cv_vs_holdout_T3_nominal_y1.png)
![Figure 4.4.1.4 | ROC-AUC by model: CV versus forward holdout — T4 (nominal, Y2).](figures/fig4.4.1.4_cv_vs_holdout_T4_nominal_y2.png)
![Figure 4.4.1.5 | ROC curve — T1 (USD, Y1), forward holdout.](figures/fig4.4.1.5_roc_T1_usd_y1.png)
![Figure 4.4.1.6 | ROC curve — T2 (USD, Y2), forward holdout.](figures/fig4.4.1.6_roc_T2_usd_y2.png)
![Figure 4.4.1.7 | ROC curve — T3 (nominal, Y1), forward holdout.](figures/fig4.4.1.7_roc_T3_nominal_y1.png)
![Figure 4.4.1.8 | ROC curve — T4 (nominal, Y2), forward holdout.](figures/fig4.4.1.8_roc_T4_nominal_y2.png)
![Figure 4.4.1.9 | Precision-recall curve — T1 (USD, Y1), forward holdout.](figures/fig4.4.1.9_pr_T1_usd_y1.png)
![Figure 4.4.1.10 | Precision-recall curve — T2 (USD, Y2), forward holdout.](figures/fig4.4.1.10_pr_T2_usd_y2.png)
![Figure 4.4.1.11 | Precision-recall curve — T3 (nominal, Y1), forward holdout.](figures/fig4.4.1.11_pr_T3_nominal_y1.png)
![Figure 4.4.1.12 | Precision-recall curve — T4 (nominal, Y2), forward holdout.](figures/fig4.4.1.12_pr_T4_nominal_y2.png)

### 4.4.2 Uncertainty (95% bootstrap CIs) — `phase6b_bootstrap_ci.csv`

| Task | Model | n (pos) | ROC-AUC | 95% CI rows | 95% CI market-clustered |
|------|-------|---------|---------|-------------|--------------------------|
| T1 Y1 | XGBoost | 83 (9) | 0.589 | 0.346–0.808 | **0.456–0.614** |
| T2 Y2 | hist GBM | 245 (36) | 0.873 | 0.796–0.935 | 0.764–0.931 |
| T3 Y1 | XGBoost | 83 (9) | 0.632 | 0.414–0.825 | 0.544–0.644 |
| T4 Y2 | XGBoost | 245 (26) | 0.898 | 0.831–0.952 | 0.864–0.960 |

The Y1 interval (market-clustered) **includes values near chance**; the Y1 holdout is
underpowered (9 positives). Y2 remains above chance but model/period-specific.

**Figure 4.4.2.1** (`figures/fig4.4.2.1_bootstrap_ci.png`): holdout AUC with 95%
market-clustered bootstrap CIs.

![Figure 4.4.2.1 | Holdout ROC-AUC with 95% market-clustered bootstrap CIs; T1 is near chance.](figures/fig4.4.2.1_bootstrap_ci.png)

### 4.4.3 Confusion matrices and threshold-derived measures

**T2 — usdprice, Y2, forward holdout (n=245, 36 positives):**
| Model | thr | TN | FP | FN | TP | Precision | Recall | Specificity | F1 | Bal.acc |
|-------|-----|----|----|----|----|-----------|--------|-------------|----|---------|
| logistic | 0.52 | 194 | 15 | 16 | 20 | 0.571 | 0.556 | 0.928 | 0.563 | 0.742 |
| hist GBM | 0.25 | 197 | 12 | 15 | 21 | 0.636 | 0.583 | 0.943 | 0.609 | 0.763 |
| XGBoost | 0.25 | 136 | 73 | 4 | 32 | 0.305 | 0.889 | 0.651 | 0.454 | 0.770 |
| persistence | 0.19 | 48 | 161 | 10 | 26 | 0.139 | 0.722 | 0.230 | 0.233 | 0.476 |

**T1 — usdprice, Y1, forward holdout (n=83, 9 positives):** XGBoost (thr 0.06) TN 3 / FP
71 / FN 1 / TP 8; logistic (thr 0.43) TN 33 / FP 41 / FN 2 / TP 7. These show that a
CV-derived threshold **does not transfer** to the holdout for Y1 — further evidence the
Y1 model is not reliable. (Note: the dissertation's "XGBoost identified 306 / missed 382"
counts do not correspond to any artefact.)

**Figures 4.4.3.1–4.4.3.4** (`figures/fig4.4.3.*.png`): one confusion matrix per task for
the best model on the forward holdout, at the CV-derived threshold.

![Figure 4.4.3.1 | Confusion matrix — T1 (USD, Y1), best model, forward holdout.](figures/fig4.4.3.1_confusion_T1_usd_y1.png)
![Figure 4.4.3.2 | Confusion matrix — T2 (USD, Y2), best model, forward holdout.](figures/fig4.4.3.2_confusion_T2_usd_y2.png)
![Figure 4.4.3.3 | Confusion matrix — T3 (nominal, Y1), best model, forward holdout.](figures/fig4.4.3.3_confusion_T3_nominal_y1.png)
![Figure 4.4.3.4 | Confusion matrix — T4 (nominal, Y2), best model, forward holdout.](figures/fig4.4.3.4_confusion_T4_nominal_y2.png)

### 4.4.4 Calibration
Per-task Brier scores (holdout) are reported in `artifacts/metrics_*.csv` (e.g. T2 hist
GBM 0.084; T1 hist GBM 0.085). Calibration and ROC/PR curves are in
`figures/phase7_y2_diagnostics.png`. Brier is **never** compared across different
targets (C4.4). Recalibration (Platt) did not improve the holdout (§4.7).

**Figures 4.4.4.1–4.4.4.4** (`figures/fig4.4.4.*.png`): reliability diagrams, one per task
on the forward holdout.

![Figure 4.4.4.1 | Calibration (reliability) curve — T1 (USD, Y1), forward holdout.](figures/fig4.4.4.1_calibration_T1_usd_y1.png)
![Figure 4.4.4.2 | Calibration (reliability) curve — T2 (USD, Y2), forward holdout.](figures/fig4.4.4.2_calibration_T2_usd_y2.png)
![Figure 4.4.4.3 | Calibration (reliability) curve — T3 (nominal, Y1), forward holdout.](figures/fig4.4.4.3_calibration_T3_nominal_y1.png)
![Figure 4.4.4.4 | Calibration (reliability) curve — T4 (nominal, Y2), forward holdout.](figures/fig4.4.4.4_calibration_T4_nominal_y2.png)

## 4.5 Inferential Statistics — Rainfall and price (C4.5)

Pearson **and** Spearman correlations between rainfall anomaly and the current return,
at leads 0–3 months (`reports/phase6_lead_lag.csv`):

| Lead (months) | Base | n | Pearson r | 95% CI (Fisher z) | p | Spearman r |
|---------------|------|---|-----------|-------------------|---|-----------|
| **1** | usdprice | 12,520 | **−0.112** | [−0.129, −0.094] | <0.001 | −0.134 |
| 1 | nominal | 12,520 | −0.124 | [−0.142, −0.107] | <0.001 | −0.135 |
| 2 | usdprice | 12,520 | −0.066 | — | <0.001 | −0.076 |
| 3 | usdprice | 12,520 | −0.084 | — | <0.001 | −0.084 |

Lower rainfall anomalies are *weakly* associated with *higher* next-month returns; the
association is strongest at **1 month**, not 2 as the dissertation reported, and is about
**half the size** of the claimed −0.22. Observations are repeated by market, so the true
uncertainty is wider than the parametric CI; the effect is statistically detectable but
**not** of obvious predictive value on its own.

**Figure 4.5.1** (`figures/fig4.5.1_lead_lag.png`): rainfall–return correlation by lead
lag, showing the 1-month peak.

![Figure 4.5.1 | Rainfall anomaly versus next-month price return by lead lag.](figures/fig4.5.1_lead_lag.png)

## 4.6 Statistical Analysis and Feature Importance (C4.6, C4.7)

- **Tuning:** histogram GBM tuned by Optuna (TPE, seed 42) inside the training period
  only — **40 trials per task (160 total)**; objective = mean validation-block ROC-AUC
  across the expanding-window folds. Search space and the four selected configurations
  are in §3.7; every parameter value is quoted from the real run
  (`artifacts/optuna_best_*.json`, `artifacts/optuna_trials_*.csv`), not fabricated.
  XGBoost and the baselines use fixed, pre-registered settings (§3.5).
- **Permutation importance (holdout):** Y1 — `spi` (+0.088), `ret_lag1` (+0.038),
  `rain_anom_lag3` (+0.033), `rain_anom_z` (+0.014). Y2 — `spi` dominates (+0.244), then
  `category`, `peer_count`. This replaces the dissertation's fabricated Table 4.3.
- **Importance stability across folds** (`phase6b_importance_stability.csv`): `spi` is
  rank 1 in every fold for both targets, but **rainfall-importance is unstable**
  (ranks 8–15, sign changes). Single-holdout importance rankings must therefore not be
   presented as fixed (C4.7).

**Figures 4.6.1–4.6.2** (`figures/fig4.6.*.png`): permutation importance with SD, one image
per target.

![Figure 4.6.1 | Permutation importance (mean ROC-AUC decrease ± SD) — T1 (USD, Y1), holdout.](figures/fig4.6.1_importance_T1_usd_y1.png)
![Figure 4.6.2 | Permutation importance (mean ROC-AUC decrease ± SD) — T2 (USD, Y2), holdout.](figures/fig4.6.2_importance_T2_usd_y2.png)

## 4.7 Robustness and Sensitivity (C4.9, C4.8)

| Check | Result |
|-------|--------|
| **By year** (OOF) | Y1 AUC falls **below 0.5** in 2020 (0.415), 2022 (0.480), 2023 (0.484) — the currency-change years; Y2 stable 0.68–0.99 |
| **By currency** (OOF) | Y1: USD 0.602 / ZWL 0.586; Y2: USD 0.834 / ZWL 0.789 |
| **By commodity** (OOF) | Y1 best pulses 0.667, worst meat 0.548; Y2 best oils 0.856, worst meat 0.729 |
| **Alternative thresholds** | Y1 noisy (0.52–0.66); Y2 peaks at 1.20–1.30 (0.85–0.88) |
| **Feature exclusion** | Drop rainfall: T1 −0.078, T2 +0.001; Drop peer: T1 −0.074, T2 −0.165 |
| **Recalibration (Platt)** | AUC unchanged (monotone); Brier slightly worse (T1 0.081→0.092; T2 0.084→0.092) |
| **Recent-window retrain (24m)** | Worse: T2 0.873→0.768; T1 0.521→0.550 |
| **Outlier winsorisation (1/99)** | Negligible (−0.017 to +0.002) |

**Interpretation:** the deterioration between CV and holdout is best explained by
**temporal distribution shift tied to currency-regime change**, not by a single
implementation error. Neither retraining nor recalibration rescued the holdout.

**Figures 4.7.1–4.7.4:** threshold sensitivity (prevalence, 4.7.1; holdout AUC, 4.7.2),
feature-exclusion sensitivity (4.7.3) and out-of-fold AUC by year (4.7.4).

![Figure 4.7.1 | Threshold sensitivity: positive-label prevalence versus threshold.](figures/fig4.7.1_threshold_prevalence.png)
![Figure 4.7.2 | Threshold sensitivity: holdout ROC-AUC versus threshold.](figures/fig4.7.2_threshold_holdout_auc.png)
![Figure 4.7.3 | Feature-exclusion sensitivity: change in holdout AUC versus the full model.](figures/fig4.7.3_feature_exclusion.png)
![Figure 4.7.4 | Out-of-fold AUC by year; Y1 falls below chance in currency-transition years.](figures/fig4.7.4_oof_by_year.png)

## 4.8 Outliers and Anomalies

Large positive returns are genuine price shocks, not errors; 1,182–1,191 rows exceed
|1.0| in the return features. Winsorising them changed Y1 holdout AUC by at most 0.017,
so they are not driving the results; they are retained by design.

## 4.9 District Risk Outputs (exploratory)

Any district-level bands derived from these scores are **exploratory, model-generated
classifications**. Given the Y1 instability and the small holdout, they are **not**
dependable early-warning predictions. The dissertation's specific "higher-risk"
districts (Beitbridge, Chiredzi, Bikita, Buhera) and the 68.4/21.2/10.4 band split have
no supporting artefact and must be withdrawn.

<!-- FIGURE PLACEHOLDER (Chapter 4 only): insert the dashboard district-risk view here
     if district outputs are shown inline in Chapter 4. The live screenshots are in
     Chapter 5 (Figures 5.1–5.10). -->
> **[Figure 4.9.1 — placeholder]** *Dashboard screenshot of the district-risk view
> (`dashboard/app.py`). Space reserved for the Chapter 4 discussion; live screenshots
> are in Chapter 5.*

## 4.10 Discussion

The results support a **compound** view of food price stress (price momentum + peer
position + weak rainfall signal), consistent with storage- and market-transmission
theory. But the dominant conclusion is methodological: **historical (CV) performance does
not transfer reliably to later periods**, and the target definition strongly affects
apparent predictability (Y2 ≫ Y1). This reframes the contribution from "a working
early-warning model" to "a reproducible workflow plus an honest diagnosis of why reliable
prediction is not yet demonstrated".

## 4.11 Chapter Summary

Real results: ~15–16% positive prevalence; Y1 weak and unstable (holdout CI reaches
chance; fails in currency-change years); Y2 moderate (~0.85 AUC) but persistence-driven;
rainfall weak and unstable; XGBoost not dominant; recalibration/retraining unhelpful.
