# Revised Chapter 2 — Literature Review (Revision Protocol)

> Status: **structural revision only.** The user supplied no literature sources and the
> dissertation bibliography is empty, so no citations are invented. This file rebuilds
> Chapter 2 as a *protocol*: it maps each research question to a measurable
> objective/procedure/output (C2.1), and provides PRISMA-style search and
> quality-assessment templates to be filled once sources are supplied (C2.2–C2.5).
> All `[CITE: …]` / `[TO RUN]` markers are placeholders, not evidence.

## 2.1 Purpose

The original Chapter 2 asserted themes (PCA, MaxEnt, random forest, XGBoost; rainfall &
NDVI drivers; SHAP; "no system combines these") **without verified sources or
systematic-selection evidence**. It is rebuilt to (a) tie the literature to the research
questions, and (b) make the search systematic, reproducible and transparent.

## 2.2 Research Questions → Objective / Procedure / Output (C2.1)

| RQ | Measurable objective | Procedure | Output artefact |
|----|----------------------|-----------|-----------------|
| RQ1 How can WFP prices + CHIRPS rainfall be integrated into a market-level unit? | Build a market×commodity×currency×month panel linked to district rainfall with an audit trail | Filter food; monthly median; point-in-polygon join; currency split | `src/build_dataset.py`; 20,530 cells; `market_admin_crosswalk.csv` |
| RQ2 Which features predict price stress without leakage? | Construct trailing-only predictors; prove no future info in `X` | Trailing returns/rollups; peer stats in-month; 1981–2015 climate baseline | `config/targets.yml`; `tests/run_checks.py` |
| RQ3 How do baselines and XGBoost compare under time-ordered validation? | Compare 5 models per target on identical holdout rows | Expanding-window CV + 12-month holdout | `artifacts/metrics_all_tasks.csv`; Ch.4.4 |
| RQ4 Does a rainfall–price signal exist, and at what lag? | Estimate association with n/p/CI at leads 0–3m | Pearson + Spearman; Fisher-z CI | `reports/phase6_lead_lag.csv` |
| RQ5 What are the key drivers and how stable are they? | Rank permutation importance and test stability across folds | OOF permutation importance | `phase6b_importance_stability.csv` |
| RQ6 How robust are results to design choices? | Test thresholds, windows, currency samples, commodity groups, feature exclusions, recalibration | Sensitivity battery | `phase6b_*.csv` |
| RQ7 Can a reproducible scoring prototype be delivered? | Versioned model + validating dashboard | Fit, persist, serve | `src/fit_final_model.py`; `dashboard/app.py` |

## 2.3 Comparative Capability Gap (replaces "no system combines these") (C1.2)

The gap is stated as a **comparison**, not an absence. Fill each cell from verified
sources; do **not** claim "no comparable capability" without checking.

| System / study | Market price | Rainfall | ML model | Prospective holdout | [CITE] |
|----------------|:---:|:---:|:---:|:---:|---|
| WFP price monitoring | Yes | No | No | N/A | `[CITE: WFP]` |
| FEWS NET | Yes | Yes | Partial | Partial | `[CITE: FEWS NET]` |
| ZimVAC | Survey-based | Context | No | N/A | `[CITE: ZimVAC]` |
| Prior ZW price-ML studies | `[TO RUN]` | `[TO RUN]` | `[TO RUN]` | `[TO RUN]` | `[CITE: …]` |
| **This study** | Yes | Yes | Yes (candidate) | Yes | This thesis |

## 2.4 Systematic Search Protocol — PRISMA-style (C2.2, C2.3)

**Databases:** Scopus, Web of Science, IEEE Xplore, ScienceDirect, Google Scholar.
**Search dates:** `[TO RUN: record the exact date each database was searched]`.
**Search strings (record exactly, per database):**

- `food AND (price OR market) AND (forecast* OR predict* OR "early warning") AND (Zimbabwe OR "Southern Africa")`
- `("machine learning" OR XGBoost OR "random forest") AND (rainfall OR climate) AND "food price"`
- `"food price" AND (anomaly OR stress OR spike) AND (ML OR "machine learning")`

**Screening counts (PRISMA flow) — `[TO RUN]` per stream:**

| Stage | Count |
|-------|-------|
| Records identified (all databases) | `[TO RUN]` |
| Duplicates removed | `[TO RUN]` |
| Records screened (title/abstract) | `[TO RUN]` |
| Full-text assessed | `[TO RUN]` |
| **Studies retained (refereed articles)** | `[TO RUN]` (target ≥ 20) |
| Reports/grey literature (separate) | `[TO RUN]` |

**Eligibility:** peer-reviewed articles (plus clearly separated grey literature/reports);
human food prices; market or household; predictive or driver-study focus; English.
Exclude purely macro/inflation studies with no market unit.

## 2.5 Source Quality Assessment (C2.4)

Score each retained study; report a table so quality is transparent.

| Study `[CITE]` | Refereed? | Data described? | Method reproducible? | Prospective validation? | ZW/SADC relevant? | Quality (H/M/L) |
|----------------|:---:|:---:|:---:|:---:|:---:|:---:|
| `[CITE]` | | | | | | |

## 2.6 Application of the 5Cs (C2.5)

For each retained source, extract: **Citation** (full reference), **Category** (driver /
method / system / context), **Contribution** (what it establishes), **Critique**
(limitations, especially validation), **Connection** (how it informs a specific objective
above). Report as one row per source.

## 2.7 Critical Synthesis (to be written once sources exist)

Themes to synthesise **with citations only** (no fabrication):

1. **Price-stress drivers** — rainfall/climate, seasonality, currency/FX, trade/transport
   costs, conflict, policy. `[CITE: …]`
2. **Methods** — classical time series vs tree ensembles; imbalance handling; importance/
   explainability; the recurring weakness of *prospective* validation. `[CITE: …]`
3. **Early-warning systems** — coverage of markets vs households; data latency; the
   distinction between *monitoring* and *forecasting*. `[CITE: …]`
4. **Gap justified by comparison** (§2.3): an integrated, leakage-controlled,
   time-validated market price-stress pipeline for Zimbabwe, evaluated honestly.

## 2.8 Justifying XGBoost as a Candidate, not a Given (C2.5, C3.8)

The revised review positions XGBoost as **one candidate among several** (with regularised
logistic regression and histogram GBM), selected for regularisation and non-linearity —
not assumed superior. Chapter 4 confirms it does **not** dominate, reinforcing that model
choice must be empirical.

## 2.9 Chapter Summary

Chapter 2 is rebuilt as a reproducible protocol: RQs mapped to measurable
objectives/procedures/outputs, a comparison-based gap, and PRISMA/quality/5Cs templates.
It can be completed to publication standard **as soon as verified literature is
supplied**.
