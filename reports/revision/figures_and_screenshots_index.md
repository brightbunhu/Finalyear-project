# Figures and Screenshots — index and captions

All figures below are generated from real artefacts by scripts in `src/` and `scripts/`.
Insert each one into the chapter at the indicated location. Replace the paths with the
actual image in your Word document as you paste.

## Chapter 4 figures

Produced by `src/eda.py` (EDA) and `src/figures_chapter4.py` (results). All EDA and
results figures derive from `data_processed/` and `artifacts/`; nothing is hard-coded.
Each image contains **a single plot** with a title, labelled axes and a legend. Figures
are numbered by their placement as `Figure <chapter>.<section>[.<subsection>][.<index>]`,
and the file name mirrors that placement (`fig4.<section>..._<slug>.png`).

| Figure | File | Section | Caption |
|---|---|---|---|
| Figure 4.2.4 | _(placeholder)_ | 4.2.4 | **[Placeholder]** Dashboard screenshot of the scoring prototype (input validation and a sample output). Live screenshots are in Chapter 5. |
| Figure 4.3.1 | `figures/fig4.3.1_monthly_coverage.png` | 4.3 | Monthly data coverage (labelable food cells per month) across the study period. |
| Figure 4.3.2 | `figures/fig4.3.2_class_balance.png` | 4.3 | Label distribution of the two targets (Y1 return-stress, Y2 peer-relative stress). |
| Figure 4.3.3 | `figures/fig4.3.3_prev_by_category.png` | 4.3 | Positive-label prevalence by commodity category. |
| Figure 4.3.4 | `figures/fig4.3.4_median_usd_price.png` | 4.3 | Median monthly food price (USD base, log scale). |
| Figure 4.3.5 | `figures/fig4.3.5_median_nominal_price.png` | 4.3 | Median nominal food price by currency (log scale); nominal series are not comparable across currency regimes. |
| Figure 4.3.6 | `figures/fig4.3.6_rainfall_anomaly_dist.png` | 4.3 | Distribution of the standardised rainfall anomaly (1981–2015 climatology). |
| Figure 4.3.7 | `figures/fig4.3.7_rainfall_anomaly_series.png` | 4.3 | Rainfall anomaly time series for example districts. |
| Figure 4.3.8 | `figures/fig4.3.8_returns_distribution.png` | 4.3 | Distribution of standardised monthly log returns (USD base). |
| Figure 4.3.9 | `figures/fig4.3.9_missingness.png` | 4.3 | Missingness of key derived features (USD panel). |
| Figure 4.4.1.1 | `figures/fig4.4.1.1_cv_vs_holdout_T1_usd_y1.png` | 4.4.1 | ROC-AUC by model: expanding-window CV (pooled) versus forward holdout, T1 (USD, Y1). |
| Figure 4.4.1.2 | `figures/fig4.4.1.2_cv_vs_holdout_T2_usd_y2.png` | 4.4.1 | ROC-AUC by model: CV versus forward holdout, T2 (USD, Y2). |
| Figure 4.4.1.3 | `figures/fig4.4.1.3_cv_vs_holdout_T3_nominal_y1.png` | 4.4.1 | ROC-AUC by model: CV versus forward holdout, T3 (nominal, Y1). |
| Figure 4.4.1.4 | `figures/fig4.4.1.4_cv_vs_holdout_T4_nominal_y2.png` | 4.4.1 | ROC-AUC by model: CV versus forward holdout, T4 (nominal, Y2). |
| Figure 4.4.1.5 | `figures/fig4.4.1.5_roc_T1_usd_y1.png` | 4.4.1 | ROC curve, T1 (USD, Y1), forward holdout. |
| Figure 4.4.1.6 | `figures/fig4.4.1.6_roc_T2_usd_y2.png` | 4.4.1 | ROC curve, T2 (USD, Y2), forward holdout. |
| Figure 4.4.1.7 | `figures/fig4.4.1.7_roc_T3_nominal_y1.png` | 4.4.1 | ROC curve, T3 (nominal, Y1), forward holdout. |
| Figure 4.4.1.8 | `figures/fig4.4.1.8_roc_T4_nominal_y2.png` | 4.4.1 | ROC curve, T4 (nominal, Y2), forward holdout. |
| Figure 4.4.1.9 | `figures/fig4.4.1.9_pr_T1_usd_y1.png` | 4.4.1 | Precision-recall curve, T1 (USD, Y1), forward holdout. |
| Figure 4.4.1.10 | `figures/fig4.4.1.10_pr_T2_usd_y2.png` | 4.4.1 | Precision-recall curve, T2 (USD, Y2), forward holdout. |
| Figure 4.4.1.11 | `figures/fig4.4.1.11_pr_T3_nominal_y1.png` | 4.4.1 | Precision-recall curve, T3 (nominal, Y1), forward holdout. |
| Figure 4.4.1.12 | `figures/fig4.4.1.12_pr_T4_nominal_y2.png` | 4.4.1 | Precision-recall curve, T4 (nominal, Y2), forward holdout. |
| Figure 4.4.2.1 | `figures/fig4.4.2.1_bootstrap_ci.png` | 4.4.2 | Holdout ROC-AUC with 95% market-clustered bootstrap confidence intervals; T1 is near chance. |
| Figure 4.4.3.1 | `figures/fig4.4.3.1_confusion_T1_usd_y1.png` | 4.4.3 | Confusion matrix, T1 (USD, Y1), best model on the forward holdout, at the CV-derived threshold (not tuned on holdout). |
| Figure 4.4.3.2 | `figures/fig4.4.3.2_confusion_T2_usd_y2.png` | 4.4.3 | Confusion matrix, T2 (USD, Y2), best model on the forward holdout. |
| Figure 4.4.3.3 | `figures/fig4.4.3.3_confusion_T3_nominal_y1.png` | 4.4.3 | Confusion matrix, T3 (nominal, Y1), best model on the forward holdout. |
| Figure 4.4.3.4 | `figures/fig4.4.3.4_confusion_T4_nominal_y2.png` | 4.4.3 | Confusion matrix, T4 (nominal, Y2), best model on the forward holdout. |
| Figure 4.4.4.1 | `figures/fig4.4.4.1_calibration_T1_usd_y1.png` | 4.4.4 | Calibration (reliability) curve, T1 (USD, Y1), forward holdout. |
| Figure 4.4.4.2 | `figures/fig4.4.4.2_calibration_T2_usd_y2.png` | 4.4.4 | Calibration (reliability) curve, T2 (USD, Y2), forward holdout. |
| Figure 4.4.4.3 | `figures/fig4.4.4.3_calibration_T3_nominal_y1.png` | 4.4.4 | Calibration (reliability) curve, T3 (nominal, Y1), forward holdout. |
| Figure 4.4.4.4 | `figures/fig4.4.4.4_calibration_T4_nominal_y2.png` | 4.4.4 | Calibration (reliability) curve, T4 (nominal, Y2), forward holdout. |
| Figure 4.5.1 | `figures/fig4.5.1_lead_lag.png` | 4.5 | Rainfall anomaly versus next-month price return by lead lag; the strongest association is at a 1-month lead. |
| Figure 4.6.1 | `figures/fig4.6.1_importance_T1_usd_y1.png` | 4.6 | Permutation importance (mean ROC-AUC decrease ± SD), T1 (USD, Y1), holdout. |
| Figure 4.6.2 | `figures/fig4.6.2_importance_T2_usd_y2.png` | 4.6 | Permutation importance (mean ROC-AUC decrease ± SD), T2 (USD, Y2), holdout. |
| Figure 4.7.1 | `figures/fig4.7.1_threshold_prevalence.png` | 4.7 | Threshold sensitivity: positive-label prevalence versus threshold. |
| Figure 4.7.2 | `figures/fig4.7.2_threshold_holdout_auc.png` | 4.7 | Threshold sensitivity: holdout ROC-AUC versus threshold. |
| Figure 4.7.3 | `figures/fig4.7.3_feature_exclusion.png` | 4.7 | Feature-exclusion sensitivity: change in holdout AUC versus the full model. |
| Figure 4.7.4 | `figures/fig4.7.4_oof_by_year.png` | 4.7 | Out-of-fold AUC by year; Y1 falls below chance during currency-transition years. |
| Figure 4.9.1 | _(placeholder)_ | 4.9 | **[Placeholder]** Dashboard district-risk view. Live screenshots are in Chapter 5. |

## Chapter 5 / Appendix screenshots

The dashboard is a working research prototype: `dashboard/app.py`. Screenshots are
produced automatically by `scripts/capture_dashboard.py` into `screenshots/`. Insert
them where evidence of the prototype is needed (Chapter 5, §5.4 Implications, or an
appendix). Each screenshot is captioned with the disclaimer that this is a research
prototype, not an operational early-warning system.

| Figure | File | Caption |
|---|---|---|
| Figure 5.1 | `screenshots/Overview.png` | Dashboard overview: data scale, target definitions and headline (honest) results. |
| Figure 5.2 | `screenshots/Data_coverage___quality.png` | Data coverage and quality page, including documented quality flags. |
| Figure 5.3 | `screenshots/Price_trends.png` | Median monthly price by category (USD base). |
| Figure 5.4 | `screenshots/Rainfall.png` | District rainfall anomaly and the real lead-lag result. |
| Figure 5.5 | `screenshots/Market___commodity_explorer.png` | Market and commodity explorer. |
| Figure 5.6 | `screenshots/Model_performance.png` | Model performance page: CV versus holdout ROC-AUC and permutation importance. |
| Figure 5.7 | `screenshots/Historical_holdout_predictions.png` | Historical holdout scores with an adjustable decision threshold (historical scores, not live forecasts). |
| Figure 5.8 | `screenshots/Prediction.png` | Prediction screen: single-point forecasting for a chosen target (Y1/Y2) using the persisted, Optuna-tuned model, with a risk band and model provenance. |
| Figure 5.9 | `screenshots/Geographic_view.png` | Geographic view: holdout-period mean score / stress share by market. |
| Figure 5.10 | `screenshots/Limitations___disclaimers.png` | Limitations and disclaimers page, including the traceability statement. |

## Reproducing

```
python src/eda.py                     # Chapter 4 EDA figures (Figures 4.3.1-4.3.9)
python src/analysis.py                # ROC-AUC + Y2 diagnostics (supports 4.4.x)
python src/figures_chapter4.py        # Chapter 4 results figures (Figures 4.4.1.1-4.7.4)
python scripts/capture_dashboard.py   # Chapter 5 dashboard screenshots (Figures 5.1-5.10)
```
