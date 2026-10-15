# Revised Chapter 5 — Conclusion and Recommendations

> Revision notes: addresses C5.1–C5.6. The poor forward-holdout result is made a
> **central finding**; objective achievement is split into three tiers; theory claims are
> softened; limitations are tied to validity; recommendations are re-prioritised.

## 5.1 Introduction

This chapter concludes the project, evaluates objectives in three tiers (technical
implementation / experimental validation / operational readiness), states implications,
ties each limitation to the validity of the conclusions, and prioritises
recommendations. Conclusions are restricted to the evidence in Chapter 4. The model
predicts a **market price stress** condition; it does not predict household food
insecurity, poverty, malnutrition or famine.

## 5.2 Summary of Findings (holdout failure as central)

The project **developed** a complete, reproducible pipeline: 28,168 raw price rows →
20,530 food cells → 5,429 (Y1) / 12,635 (Y2) labelled observations, joined to district
rainfall, with leakage-controlled features and two mathematically defined targets.

The project **validated**, however, only weak-to-moderate and unstable predictive skill:

- **Y1 (standardised-return stress):** forward-holdout ROC-AUC 0.589 (XGBoost),
  95% market-clustered CI **0.456–0.614** — indistinguishable from chance; OOF AUC
  **below 0.5 in 2020, 2022 and 2023**, the currency-change years.
- **Y2 (peer-relative stress):** holdout ROC-AUC 0.886 (USD) / 0.897–0.899 (nominal),
  but largely carried by the persistence of the peer-relative price itself (persistence
  baseline holdout 0.711).
- Rainfall is a **weak and unstable** signal (lead-1 r ≈ −0.11).
- **XGBoost does not dominate** (histogram GBM wins the USD Y2 holdout 0.886 vs 0.842;
  the two are statistically tied on nominal Y2).
- Recalibration and recent-window retraining did **not** improve later-period performance.

**The single most important finding is that a functioning pipeline did not produce a
reliably generalisable predictive model.** This is foregrounded rather than treated as a
qualification.

## 5.3 Achievement of Objectives — three-tier assessment (C5.2)

The dissertation's binary "highly/substantially met" scheme was too favourable. The
revised table separates *implementation*, *validation* and *operational readiness*.

| Objective | Implementation | Experimental validation | Operational readiness | Supporting evidence |
|-----------|:---:|:---:|:---:|---|
| 1. Data integration | **Met** | Met (panel auditable) | Not applicable | 20,530 cells; 327/335 markets matched; build log |
| 2. Feature construction | **Met** | Partial (rainfall weak/unstable) | N/A | Leakage tests pass; feature-exclusion + stability results |
| 3. Model comparison (time-ordered) | **Met** | **Not met** — no reliable prospective discrimination | Not met | Holdout CIs; by-year OOF (<0.5 in transition years) |
| 4. Prospective scoring prototype | **Met (prototype)** | Not validated | **Not met** | `src/fit_final_model.py`, `dashboard/app.py` |
| 5. Commodity/district support | Met (outputs exist) | Not validated for districts | **Not met** | Commodity OOF results; district bands exploratory |

The honest conclusion is that **implementation succeeded** while **validation and
operational readiness did not**.

## 5.4 Implications and Impact (C5.3)

**Theory.** The project does **not** establish new causal relationships between rainfall
and food price stress. Its theoretical value is limited to demonstrating an integrated,
validation-aware applied workflow and to the observation that target definition
(return-based vs peer-relative) massively changes apparent predictability.

**Practice.** A market stress signal, if developed further, could support **prioritising
verification** — not automatic action. The primary user (a market-monitoring analyst)
should treat any high probability as a prompt to check local information and existing
assessments.

**Education 5.0.** The concrete innovation demonstrated here is **not** a working
early-warning model but a **reproducible, leakage-controlled pipeline with an honest
validation protocol** (`src/`, `tests/run_checks.py`, dashboard). The study is a
retrospective, model-development exercise: it develops and packages the workflow and
specifies how a market-monitoring analyst could use a future stress signal, but does not
itself include field deployment or end-user engagement. Translating the workflow into a
community or industry setting is therefore presented as **proposed future work** rather
than a completed outcome, and would require the stakeholder testing and governance steps
set out in §5.6.

**Prototype evidence.** The scoring workflow is packaged as a working research dashboard
(`dashboard/app.py`); screenshots of all ten pages are shown below
(**Figures 5.1–5.10**). The dashboard reads only real pipeline artefacts, labels every
page as a research prototype, and is **not** an operational early-warning system.

![Figure 5.1 | Dashboard overview: data scale, target definitions and headline results.](screenshots/Overview.png)
![Figure 5.2 | Data coverage and quality page, including documented quality flags.](screenshots/Data_coverage___quality.png)
![Figure 5.3 | Median monthly price by category (USD base).](screenshots/Price_trends.png)
![Figure 5.4 | District rainfall anomaly and the real lead-lag result.](screenshots/Rainfall.png)
![Figure 5.5 | Market and commodity explorer.](screenshots/Market___commodity_explorer.png)
![Figure 5.6 | Model performance: CV versus holdout ROC-AUC and permutation importance.](screenshots/Model_performance.png)
![Figure 5.7 | Historical holdout scores with an adjustable decision threshold.](screenshots/Historical_holdout_predictions.png)
![Figure 5.8 | Prediction screen: single-point forecasting for a chosen target (Y1/Y2) using the persisted, Optuna-tuned model.](screenshots/Prediction.png)
![Figure 5.9 | Geographic view: holdout-period mean score / stress share by market.](screenshots/Geographic_view.png)
![Figure 5.10 | Limitations and disclaimers page, including the traceability statement.](screenshots/Limitations___disclaimers.png)

## 5.5 Limitations and their Effect on Validity (C5.4)

| Limitation | Effect on the conclusions |
|------------|---------------------------|
| **Temporal generalisation** (CV ≫ holdout; <0.5 in transition years) | **Directly undermines operational suitability** — later-period predictions cannot be trusted as reliable; this is why the district outputs are exploratory. |
| **Small holdout / few positives** (Y1: 9 positives) | Estimates have wide intervals; Y1 skill cannot be distinguished from chance. |
| **Target validity** (market price ≠ household food insecurity) | Conclusions apply to market prices only; no welfare inference. |
| **Currency/inflation instability** | Structural breaks distort the relationship; historical features do not capture regime change. |
| **Sparse series** (median length 4 months) | Few labels per series; less stable learning. |
| **Geographic matching** (8 markets unmatched; 1 district no rainfall; name vs coordinate) | District outputs have spatial uncertainty; treated as screening only. |
| **Feature omission** (fuel, transport, stocks, informal FX…) | Explains part of the model error; results are lower bounds on achievable skill. |
| **Permutation-importance instability** | Feature rankings must not be read as a fixed importance order or as causal. |
| **No operational testing** | No claim of institutional readiness. |

## 5.6 Recommendations (re-prioritised) (C5.5)

**Immediate (before any operational use):**
1. **Investigate and stabilise the holdout.** Diagnose the currency-regime distribution
   shift (already begun, `phase6b_*`); consider regime-specific or regime-aware models
   and rolling-origin evaluation over longer periods.
2. **Validate and possibly redefine the targets.** Re-examine Y1 (unreliable) and
   justify/refine thresholds with domain users and observed outcomes.
3. **Repeat the model evaluation using the same target, evaluation set and metrics**
   before any superiority claim.

**Subsequent:**
4. Recalibrate and monitor drift once new outcomes are available.
5. Improve data quality and coverage (remote/informal markets; the 8 unmatched markets;
   the missing district; suspicious `usdprice` values; FX basis clarity).
6. Conduct user-centred evaluation and establish governance (model registry, alert-review
   protocol, withdrawal process).

## 5.7 Future Research

Extend features (soil moisture, vegetation, temperature, fuel/transport, stocks, FX);
compare targets against household food-consumption and market-function indicators;
adopt rolling-origin evaluation and richer probabilistic/spatial models; and run
user-centred and governance studies before operational deployment.

## 5.8 Conclusion (defensible contribution) (C5.6)

The project's **strongest demonstrated contribution is the development of an integrated,
reproducible data-processing and experimental-prediction workflow** — including
leakage-controlled feature engineering, two mathematically defined market-stress targets,
time-respecting validation and a working scoring prototype — **together with an honest
diagnosis of why a reliably generalisable early-warning model was not established**. The
results show that food price stress is influenced by compound factors, that the target
definition strongly affects apparent predictability, and that later-period generalisation
is severely constrained by currency-regime change. The system should remain a
supplementary decision-support prototype, used only with human review, until its
calibration, temporal stability, coverage and decision value have been demonstrated over
time.
