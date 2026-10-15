# Phase 6b — Holdout diagnostics, uncertainty and robustness

Produced by `src/robustness.py`. Every number below is from `reports/phase6b_*.csv`.
Histogram-GBM rows use the **Optuna-tuned** parameters (§3.7); XGBoost uses its fixed,
pre-registered settings. These analyses respond directly to the supervisor's core
concern: the credibility of the predictive claims given weak later-period performance.

## 1. Why the holdout matters: it is small and uncertain (bootstrap CIs)

Holdout = final 12 labelled months. Row bootstrap and **market-clustered** bootstrap
(markets resampled with replacement, accounting for repeated observations from the
same market) give 95% intervals (`phase6b_bootstrap_ci.csv`, 2,000 resamples):

| Task | Model | n (pos) | ROC-AUC | 95% CI (rows) | 95% CI (market-clustered) |
|------|-------|---------|---------|----------------|----------------------------|
| T1 usd / Y1 | XGBoost | 83 (9) | 0.589 | 0.346 – 0.808 | 0.456 – 0.614 |
| T1 usd / Y1 | hist-GBM | 83 (9) | 0.521 | 0.233 – 0.819 | 0.338 – 0.632 |
| T2 usd / Y2 | hist-GBM | 245 (36) | 0.873 | 0.796 – 0.935 | 0.764 – 0.931 |
| T2 usd / Y2 | XGBoost | 245 (36) | 0.846 | 0.759 – 0.919 | 0.726 – 0.914 |
| T3 nominal / Y1 | XGBoost | 83 (9) | 0.632 | 0.414 – 0.825 | 0.544 – 0.644 |
| T4 nominal / Y2 | XGBoost | 245 (26) | 0.898 | 0.831 – 0.952 | 0.864 – 0.960 |

**Interpretation.** The Y1 holdout has only 9 positive events, so its interval spans
almost the whole range. The apparent Y1 "discrimination" is **not distinguishable from
chance at the market level** (lower bound 0.46). The Y2 holdout is larger and its
interval stays comfortably above 0.5, but it remains model/period-specific.

## 2. Temporal drift: performance by year (out-of-fold) — `phase6b_oof_by_year.csv`

Out-of-fold predictions over the whole timeline. Y1 discrimination collapses in the
currency-transition years:

| Year | Y1 OOF AUC (usd) | Y2 OOF AUC (usd) | n |
|------|------------------|------------------|---|
| 2016 | 0.661 | 0.899 | 223 / 191 |
| 2017 | 0.562 | 0.863 | 225 / 752 |
| 2018 | 0.778 | 0.675 | 39 / 259 |
| 2020 | **0.415** | 0.786 | 761 / 4267 |
| 2021 | 0.717 | 0.799 | 1674 / 2601 |
| 2022 | **0.480** | 0.820 | 582 / 791 |
| 2023 | **0.484** | 0.795 | 562 / 1648 |
| 2024 | 0.576 | 0.785 | 206 / 586 |
| 2025 | 0.774 | 0.841 | 66 / 201 |
| 2026 | 0.520 | 0.987 | 35 / 39 |

**This is the mechanism behind the supervisor's concern.** Y1 ranking is *below chance*
in 2020, 2022 and 2023 — exactly the years of currency change (ZWL introduction, then
re-dollarisation). Y2 is comparatively stable (0.68–0.99). Distribution shift tied to
the monetary regime is the most plausible explanation, not an implementation error.

## 3. Performance by currency and commodity — `phase6b_oof_by_currency.csv`, `..._by_commodity.csv`

| Split | Y1 AUC | Y2 AUC |
|-------|--------|--------|
| USD | 0.602 | 0.834 |
| ZWL | 0.586 | 0.789 |

| Commodity | Y1 AUC | Y2 AUC |
|-----------|--------|--------|
| cereals and tubers | 0.565 | 0.788 |
| pulses and nuts | 0.667 | 0.809 |
| oil and fats | 0.577 | 0.856 |
| meat, fish and eggs | 0.548 | 0.729 |
| miscellaneous food | 0.595 | 0.809 |

Y2 is consistently more predictable; meat/fish/eggs are hardest. This replaces the
dissertation's fabricated per-commodity AUCs (0.871 for oils, etc.).

## 4. Alternative target thresholds (hist-GBM) — `phase6b_threshold_model_sensitivity.csv`

| Target | threshold | prevalence % | holdout AUC |
|--------|-----------|--------------|-------------|
| Y1 (σ) | 0.75 | 18.2 | 0.482 |
| Y1 (σ) | 1.00 | 14.9 | 0.632 |
| Y1 (σ) | 1.25 | 12.2 | 0.643 |
| Y1 (σ) | 1.50 | 10.2 | 0.571 |
| Y2 (SPI) | 1.10 | 27.2 | 0.822 |
| Y2 (SPI) | 1.20 | 16.3 | 0.873 |
| Y2 (SPI) | 1.30 | 10.2 | 0.890 |
| Y2 (SPI) | 1.50 | 5.3 | 0.788 |

Y1 is insensitive to (and noisy across) thresholds; Y2 peaks around 1.20–1.30.

## 5. Feature exclusion — `phase6b_feature_exclusion.csv`

| Task | full | drop rainfall | drop peer |
|------|------|---------------|-----------|
| T1 usd / Y1 | 0.589 | 0.511 (−0.078) | 0.515 (−0.074) |
| T2 usd / Y2 | 0.846 | 0.847 (+0.001) | 0.681 (−0.165) |

Rainfall adds measurable signal only for Y1, and the holdout is too small to rely on
the size of that change. Peer-market features dominate Y2 (as they must — the target
is peer-relative). Rainfall is **not** the top driver the dissertation claimed.

## 6. Retraining / recalibration attempts — `phase6b_window_recalibration.csv`

| Task | model | ROC-AUC | Brier |
|------|-------|---------|-------|
| T1 usd / Y1 | full history | 0.521 | 0.081 |
| T1 usd / Y1 | recent 24 months | 0.550 | 0.111 |
| T1 usd / Y1 | Platt-recalibrated | 0.521 | 0.092 |
| T2 usd / Y2 | full history | 0.873 | 0.084 |
| T2 usd / Y2 | recent 24 months | 0.768 | 0.099 |
| T2 usd / Y2 | Platt-recalibrated | 0.873 | 0.092 |

Neither strategy improved later-period performance: restricting to recent data
**reduced** discrimination (less training history), and Platt recalibration leaves rank
metrics unchanged and slightly worsened Brier. Recalibration did **not** rescue the
holdout — an honest negative result.

## 7. Outliers — `phase6b_outlier_sensitivity.csv`

Winsorising returns at the 1st/99th percentile changes holdout AUC by −0.017 (nominal
Y1) to +0.002 (usd Y1). Legitimate large returns (1,182–1,191 rows exceed |1.0|) are
therefore not driving performance; extreme values are retained by design.

## 8. Permutation-importance stability across folds — `phase6b_importance_stability.csv`

XGBoost importance computed separately in 3 expanding folds:

- **Y1:** `spi` is rank 1 in every fold (mean +0.075, sd 0.020); the next features
  (`ret_lag1`, `ret_roll3`) are modest and their ranks move. **Rainfall features are
  unstable**, ranking 8–15 with sign changes across folds.
- **Y2:** `spi` dominates (mean +0.258, sd 0.050, rank 1 in all folds); then `category`.

This confirms the supervisor's caution: single-holdout importance rankings (the
dissertation's Table 4.3) are not stable, especially for rainfall, and must not be
presented as a fixed importance order.

## 9. Conclusions for the model claims

1. The Y1 target is **not reliably predictable** with these features; its holdout and
   market-clustered intervals include or approach chance, and it fails in
   currency-transition years.
2. The Y2 target is **moderately predictable** and comparatively stable, but its skill
   is largely carried by the persistence of the peer-relative price itself.
3. Rainfall provides **weak, unstable** incremental signal, only visible for Y1.
4. Neither retraining nor recalibration improved later-period performance.
5. Therefore the district outputs must be labelled **exploratory**, and no operational
   early-warning claim is supported.
