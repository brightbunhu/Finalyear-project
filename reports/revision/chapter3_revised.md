# Revised Chapter 3 — Methodology

> Revision notes: addresses C3.1–C3.10 (reproducible workflow, auditable preparation,
> panel reconciliation, exact target maths, leakage separation, partition boundaries,
> pipelines/hyperparameters, horizon gap). All counts are from
> `data_processed/panel_build_log.txt`, `reports/phase3_rainfall_summary.json` and
> `artifacts/`. Code: `src/build_rainfall.py`, `src/build_dataset.py`, `src/train.py`,
> `src/robustness.py`. Config: `config/targets.yml` (seed 42).

## 3.1 Introduction

This chapter specifies the methods so that the study can be reproduced
independently. It gives the complete workflow (inputs → transformation → target
construction → chronological partitioning → training → evaluation → scoring), the
exact data-preparation audit trail, the mathematical definition of both targets, and
the leakage controls. Results appear in Chapter 4.

## 3.2 Research Methodology (CRISP-DM)

The project follows CRISP-DM (business/project understanding → data understanding →
data preparation → modelling → evaluation → deployment), mapped as:

| CRISP-DM stage | This project |
|----------------|--------------|
| Project understanding | Define food price stress, primary user, scope (§1.7–1.10) |
| Data understanding | Phase 1 inventory/quality (`reports/phase1_*`) |
| Data preparation | `src/build_rainfall.py`, `src/build_dataset.py` |
| Modelling | `src/train.py` (5 models, 4 tasks) |
| Evaluation | `src/train.py`, `src/robustness.py`; `tests/run_checks.py` |
| Deployment | `src/fit_final_model.py`, `dashboard/app.py` |

## 3.3 Research Design

Quantitative, retrospective, longitudinal and predictive; **not experimental** (no
control over prices, rainfall or currency). Unit of analysis:
`market × commodity × currency × month`, linked to an administrative district. Four
design rules: (1) target refers to month *t+1*; (2) predictors use only information
available at or before *t*; (3) training/testing follow calendar order; (4) the output
is a market early-warning signal, not a household classification.

## 3.4 Data Collection and Preprocessing

### 3.4.1 Sources, versions and periods (audit)

| Source (file) | Version/period | Role |
|---------------|----------------|------|
| WFP food prices (`raw/wfp_food_prices_zwe.csv`) | 2010-01-15 → 2026-05-15, 28,168 rows | Primary price panel |
| WFP markets (`raw/wfp_markets_zwe.csv`) | 486 markets | Market → district crosswalk |
| CHIRPS v3.0 (`raw/yr.nc`) | 1981-01 → 2026-08; 548 months; 0.05° | District rainfall |
| geoBoundaries ADM1/ADM2 | 10 provinces, 91 districts (CC BY 3.0 IGO) | Spatial joins |
| HDX HAPI population | 2023, admin-2 | District context |
| HDX HAPI rainfall | admin-1 only, 2022-01→2026-09 | **Not used** (insufficient resolution) |

### 3.4.2 Record-count reconciliation (replaces the unverifiable 3,571 / 10,459)

> Supervisor C3.4: explain how the panels were built and reconcile them. The
> dissertation's "3,571 primary / 10,459 SPI" figures have no supporting artefact and
> cannot be reproduced; the real derivation is below.

| Step | Rows |
|------|------|
| Raw WFP price rows | 28,168 |
| − removed non-food category | −7,638 |
| = food cells | 20,530 |
| − removed price ≤ 0 | −0 |
| = monthly cells (market×commodity×currency×month) | **20,530** |
| Series (market×commodity×currency) | 3,029 |
| Cells with an observed next month (labelable) | 7,624 (37.1%) |
| — of which Y1 labelable (≥6 prior returns) | **5,429** |
| — of which Y2 labelable (≥5 peers) | **12,635** |

Two panels are saved (`panel_usdprice.parquet`, `panel_nominal_within_currency.parquet`).
The two target panels are **nested within** the same 20,530-cell panel; they differ only
by labelling requirement (Y1 needs a return history; Y2 needs peers).

### 3.4.3 Data-quality assessment

Checks: missing dates/prices/currencies/coordinates; duplicate keys; zero/negative
prices; commodity/name consistency; validity of coordinates; rainfall coverage.
Key findings (must be reported in Ch.4): 8 markets lack coordinates
(`Dulibadzimu Market, Kombai, Mandava, Mucheke, Murombedzi, Plumtree town, Renkini Bus
Terminus, Tshovani`); `usdprice` minimum ≈ 1.5×10⁻⁵ is implausible; `priceflag=aggregate`
covers 78% of rows and is **retained** (documented decision).

### 3.4.4 Cleaning and aggregation

Dates → month. Where several valid prices share a
market×commodity×currency×month, the **monthly median** is taken. A missing future price
is **not** treated as non-stress; such rows are excluded from supervised use only
(`labelable_* = False`). No observation is discarded solely for being large.

### 3.4.5 Integration and currency handling (C3.3)

Markets are matched to districts by **point-in-polygon** on coordinates (not by name),
in WGS84: 327/335 priced markets matched; 8 flagged. Currency changes are handled by
analysing two price bases **in parallel and never pooled**:
- **nominal-within-currency** (`price`), where a series is scoped to a single currency;
- **usdprice**, a currency-comparable series.

Unit (`KG`, `L`, `100 ML`, `250 G`) is retained in the crosswalk; commodity definitions
are taken from WFP `commodity_id`/`category`. Verified regimes: USD-only 2010–2018;
ZWL-only 2019–2022; mixed 2023–2026.

### 3.4.6 Feature engineering and leakage control (C3.9)

Features: `ret_z_cur`, `ret_lag1`, `ret_lag2`, `ret_roll3` (price momentum);
`spi`, `peer_count` (peer markets); `rain_anom_z`, `rain_anom_lag1..3`, `rain_roll3_mm`
(rainfall); `month_sin`, `month_cos` (seasonality); `log_population`; `category`,
`currency` (categorical); `interaction = ret_z_cur × rain_anom_z`.

Leakage controls: all rolling windows are **trailing**; peer statistics are computed
**within a single month**; rainfall is standardised against a **1981–2015** climatology
(available before every modelled month); scaling/imputation are fitted **inside** the
training fold. The predictor matrix `X` never contains `z_next`, `next_spi`, `y1`, `y2`
or any `labelable_*` column — enforced by `tests/run_checks.py`.

### 3.4.12 Target-variable construction (C3.5, C3.6)

**Log return.** For market *i*, commodity *c*, currency *u*, month *t*:
`r_{i,c,u,t} = ln(P_{i,c,u,t}) − ln(P_{i,c,u,t−1})`.

**Target Y1 (standardised-return stress).** Using a **trailing** 12-month window and
requiring ≥ 6 prior returns, with mean μ and SD σ of the *trailing* returns:
`z_{i,c,u,t+1} = (r_{i,c,u,t+1} − μ) / σ`;
`Y1 = 1` if `z_{i,c,u,t+1} ≥ 1.0`, else 0. Standardisation uses only returns up to
*t+1*'s window start (trailing), never future statistics.

**Target Y2 (peer-relative stress / SPI).** Within peer group G = (same `commodity_id`,
same `currency`, same `month`), with ≥ 5 peer markets, peer median `m`:
`SPI_{i,c,u,t+1} = P_{i,c,u,t+1} / m(G)`; `Y2 = 1` if `SPI_{i,c,u,t+1} ≥ 1.20`.

**Threshold justification.** Thresholds are set on prevalence grounds, not tuned on the
holdout (`reports/phase6_threshold_sensitivity.csv`):

| Y1 threshold (σ) | 0.50 | 0.75 | 1.00 | 1.25 | 1.50 | 2.00 |
|---|---|---|---|---|---|---|
| prevalence % | 22.5 | 18.1 | **14.8** (chosen) | 12.1 | 10.1 | 7.1 |

| Y2 threshold (SPI) | 1.10 | 1.20 | 1.30 | 1.50 |
|---|---|---|---|---|
| prevalence % | 27.2 | **16.3** (chosen) | 10.2 | 5.3 |

**Label-with-future vs predictor-leakage (explicit).** Using *t+1* prices to **create the
training label** is intended and permitted — the label is the thing being predicted. Using
*t+1* information to **construct predictors** is prohibited and is prevented (above). The
two are distinct and are separated throughout.

## 3.5 Model Selection

Five models per task: **majority** baseline, **persistence** baseline (predict next =
current state), **elastic-net logistic regression** (interpretable, handles correlated
lagged returns), **histogram gradient boosting** (non-linear), **XGBoost** (regularised
boosting). XGBoost is a *candidate*, not an assumed winner; the results (Ch.4) show it
does not dominate.

Hyperparameter treatment is deliberately unequal and stated: **histogram gradient
boosting is tuned by Optuna (§3.7)**, while the baselines and XGBoost use fixed,
pre-registered configurations recorded in `src/train.py`. This keeps the tuned search
scoped to the model under study and does not confound the model comparison.

## 3.6 Model Training and Evaluation

Identification of the evaluation set: each task uses the **same holdout rows** for all
its models. Metrics: ROC-AUC, PR-AUC, precision, recall, specificity, F1, balanced
accuracy, Brier loss, and a confusion matrix at a **single operating threshold taken
from pooled cross-validation validation (the F1-optimal value), applied unchanged to the
holdout** — the holdout is never used to choose the threshold. Comparisons are reported
**per target**; models from different targets (Y1 vs Y2) are never placed in a single
ranking (C4.2).

## 3.7 Model Tuning

Histogram gradient boosting is tuned with **Optuna (TPE sampler, seed 42)** **inside the
training period**; the forward holdout is excluded from tuning. The search ran **40 trials
per task (4 tasks, 160 trials in total)**, with each trial scored by the **mean
validation-block ROC-AUC across the expanding-window folds**. Search space:

- `learning_rate` ∈ [0.01, 0.30] (log)
- `max_iter` ∈ {100, 150, …, 500}
- `max_leaf_nodes` ∈ [7, 63]
- `min_samples_leaf` ∈ [10, 60]
- `l2_regularization` ∈ [10⁻³, 10] (log)
- `max_bins` ∈ {128, 255}

Selection rule: highest mean validation ROC-AUC; the chosen configuration is reported as
"selected under this design", not as permanently optimal. The full trial log
(`artifacts/optuna_trials_<task>_hist_gradient_boosting.csv`), the selected parameters
(`artifacts/optuna_best_<task>_hist_gradient_boosting.json`) and a summary
(`artifacts/optuna_summary.csv`) are retained. `src/train.py` and `src/fit_final_model.py`
load these selected parameters, so the reported models are exactly the tuned ones.

**Selected configurations (best of 40 trials per task):**

| Task | mean CV ROC-AUC | learning_rate | max_iter | max_leaf_nodes | min_samples_leaf | l2_regularization | max_bins |
|------|-----------------|---------------|----------|----------------|------------------|-------------------|----------|
| T1 (usd, Y1) | 0.611 | 0.0775 | 200 | 40 | 15 | 0.0135 | 255 |
| T2 (usd, Y2) | 0.827 | 0.0236 | 150 | 13 | 53 | 0.0015 | 255 |
| T3 (nominal, Y1) | 0.610 | 0.2189 | 450 | 37 | 12 | 0.0030 | 255 |
| T4 (nominal, Y2) | 0.831 | 0.0197 | 150 | 10 | 52 | 0.0027 | 255 |

## 3.8 Model Validation — exact partitions and horizon gap (C3.7, C3.10)

**Scheme:** expanding-window CV (earliest history → next period, window grows) plus a
12-month forward holdout. Exact boundaries are recorded in `artifacts/folds_*.json`.
Representative labels (Y1, usd), validation windows:

| Fold | Train ends | Validation months | n_train | n_val |
|------|-----------|-------------------|---------|-------|
| 0 | 2012-12 | 2013-01 → 2015-09 | 535 | 424 |
| 1 | 2015-09 | 2015-10 → 2018-06 | 959 | 558 |
| 2 | 2018-06 | 2018-07 → 2022-09 | 1,517 | 2,843 |
| 3 | 2022-09 | 2022-10 → 2025-04 | 4,360 | 986 |
| Holdout | (all CV months) | 2025-05 → 2026-04 | — | 83 |

Y2 (usd) holdout: 2024-12 → 2026-04 (n=245). Windows are irregular because the price
panel itself has gap months (no data in parts of 2019/2022).

**Forecast-horizon gap.** Because the horizon is 1 month and labels require an observed
*t+1*, the holdout begins the first month **after** the last training month; training
labels never extend into the validation block. A longer lead (e.g. 2 months) would
require dropping boundary observations, which was tested implicitly via the lead-lag
analysis (Ch.4.5) and was not needed for a 1-month horizon.

**Leakage verification.** `tests/run_checks.py` asserts (a) no `t+1`/label column in `X`;
(b) `labelable_y1 ⇒ z_next` present and `labelable_y2 ⇒ next_spi` present; (c) unit-key
uniqueness; (d) prevalence within expected bands. All pass (20/20).

## 3.9 Statistical Analysis

Descriptive statistics precede modelling. Rainfall–price timing is examined with
**Pearson and Spearman** correlations at leads 0–3 months, with **n**, p-values and 95%
CIs via Fisher's z (Ch.4.5). Because the same market contributes repeated observations,
inference treats observations as **not independent**; consequently bootstrap confidence
intervals are reported both at row level and **clustered by market**
(`reports/phase6b_bootstrap_ci.csv`). Permutation importance is computed out-of-sample
and, additionally, **across folds** to test stability (`phase6b_importance_stability.csv`).
No causal claim is made.

## 3.10 Software and Tools

Python 3.12; pandas, NumPy (tabular/numeric); GeoPandas + Shapely (spatial joins);
xarray + netCDF4 (CHIRPS); scikit-learn (pipelines, metrics); XGBoost; Optuna (tuning);
Matplotlib (figures); joblib (model persistence); Streamlit (dashboard). No
`live_prediction.py`/`map_stress.py` are claimed; the working scoring artefact is
`src/fit_final_model.py` + `dashboard/app.py`.

## 3.11 Ethical Considerations

Secondary market/climate/population data only; no personal data; district outputs are
market signals, not household assessments; human verification required; poorly covered
areas remain visible as a fairness concern.

## 3.12 Chapter Summary

A reproducible, leakage-controlled workflow is specified: 28,168 raw rows → 20,530 food
cells → 5,429 (Y1) / 12,635 (Y2) labelled observations; two targets defined
mathematically; expanding-window CV with a 12-month forward holdout whose boundaries are
recorded; per-target model comparison with uncertainty intervals. Chapter 4 reports the
results produced by exactly this workflow.
