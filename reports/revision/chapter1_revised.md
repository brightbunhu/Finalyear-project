# Revised Chapter 1 — Introduction

> Revision notes: addresses supervisor comments C1.1–C1.5. Citations are drawn from the
> author-supplied reference list (`reports/revision/references.md`). Numbers marked
> "verified" come from the rebuild (`reports/phase1_report.md`,
> `data_processed/panel_build_log.txt`).

## 1.1 Introduction

Food prices determine whether households can afford an adequate diet. When prices rise
quickly, low- and irregular-income households are affected first: they buy less,
substitute cheaper foods, borrow, or cut other spending. Food-price change is therefore
not only an economic issue but one connected to livelihoods, health, agriculture and
social welfare. Zimbabwe is a suitable case because food prices are shaped
simultaneously by rainfall, agricultural production, currency conditions, transport
costs and local market differences. This project applies data-science methods to
combine market price records, rainfall information and administrative geography in
order to estimate the probability of a defined **food price stress** condition at
market and district level in the following month.

## 1.2 Background and Context

### 1.2.1 Current state of knowledge

Zimbabwe depends heavily on rain-fed agriculture, so rainfall deficits can affect
production, incomes, livestock, availability and prices. Zimbabwe-specific evidence links
ENSO and seasonal rainfall to maize-yield variability (Phillips et al., 1998) and to
agricultural and anticipatory-action outcomes (Mano & Nhemachena, 2007; Sazib et al.,
2020; Mugiyo et al., 2023). The relationship is not immediate: traders and consumers
change expectations during the growing season before the harvest outcome is known, and a
rainfall deficit may combine with weak market supply, transport costs or foreign-currency
shortages to push prices higher (Wright, 2011; Deaton & Laroque, 1992).

The country's monetary history makes price measurement difficult. Records are expressed
variously in Zimbabwean dollars and US dollars, and the meaning of a nominal price
changes with depreciation and exchange-rate regime (Kramarenko et al., 2010; World Bank,
2021). A nominal increase may reflect general inflation, conversion, transport costs, or a
genuine local shortage. Prices also differ across districts: a market near a surplus area
restocks more easily than a remote market in a dry region, so a national average can hide
local stress (Fackler & Goodwin, 2001; Burke & Myers, 2014; Porteous, 2019).

These mechanisms are documented by specific, referenced evidence: actual food-price
behaviour and volatility (Deaton & Laroque, 1992; Wright, 2011; Symeonidis et al., 2012;
Gilbert et al., 2017), spatial price transmission in Southern Africa and Zimbabwe (Burke &
Myers, 2014; Davids et al., 2017; Mahdi & Bonato, 2015), rainfall shocks (Funk et al.,
2015; Shukla et al., 2020), and Zimbabwe's inflation and currency episodes (Kramarenko et
al., 2010; World Bank, 2021; Moyo, 2024). Household-level insecurity is separately
documented (Tawodzera, 2011; Mango et al., 2014; Bhalla et al., 2018). This revision
distinguishes **observed national challenges** (documented by the sources above) from the
**assumptions** that motivate the proposed system (stated in §1.9).

### 1.2.2 Gap identification

Existing systems already monitor food markets and food security. The gap must therefore
be stated as a **specific missing capability**, not as the absence of an identical
system. The comparison below sets out what each system provides and what this project
adds.

| System | Geographic unit | Frequency | Target | Provides a machine-readable market–commodity probability of next-month price stress? |
|--------|-----------------|-----------|--------|--------------------------------------------------------------------------------------|
| WFP market monitoring (WFP, 2025a, 2025b) | Market / national | Monthly | Price levels, availability | No — descriptive, indicators not probabilities |
| FEWS NET / IPC (FEWS NET, n.d.) | Livelihood zone / district | Monthly–quarterly | Food-security phase (IPC) via scenario analysis + expert judgement | No — expert-based outlooks |
| ZimVAC / ZimLAC (ZimLAC, 2024) | District / ward | Annual | Household livelihoods & vulnerability | No — household assessment |
| CHIRPS (Funk et al., 2015) | Pixel → district | Dekadal–monthly | Rainfall | N/A (input, not a forecast of prices) |
| Food-security ML crisis models (Busker et al., 2024; Westerveld et al., 2021) | Region / household | Variable | Crisis / household state | Partial — not a market–commodity monthly price model |

**Missing capability:** none of these provides a single, reproducible, monthly,
market–commodity–district **probability** of a pre-defined next-month *price* stress
event, with currency-regime handling, leakage-controlled chronological validation and a
re-runnable scoring artefact. The project addresses this applied data-science gap. It
does **not** claim that WFP/FEWS NET lack predictive capability; it claims a specific,
narrow, reproducible output is absent.

## 1.3 Problem Statement

Food price stress in Zimbabwe develops through the combined effects of rainfall
deficits, agricultural losses, currency change, transport costs and local market
conditions, but the timing and location of the next event are difficult to identify
from separate market and climate reports. A national average hides district and
commodity differences. The problem is the **lack of an integrated, reproducible
data-science system** that (i) combines price, rainfall and geographic data at market
and district level, (ii) uses only information available at the prediction date, and
(iii) reports honestly how well the resulting probabilities generalise to later
periods.

## 1.4 Project Aim

To **develop and evaluate** a machine-learning system that uses food-price data,
rainfall anomalies and market information to estimate the probability of a defined food
price stress condition in Zimbabwean markets and districts in the following month, and
to report the reliability of those estimates under time-respecting validation.

## 1.5 Project Objectives (measurable, with acceptance criteria)

> Supervisor C1.3: objectives must specify expected outputs and acceptance criteria.
> Verified data facts used below are from `reports/phase1_report.md`.

**Objective 1 — Data integration.**
*Output:* a monthly `market × commodity × currency × month` panel joined to district
rainfall. *Acceptance:* ≥ 20,000 food cells retained from 28,168 raw rows; ≥ 95% of
priced markets assigned to a district via coordinates; a written build log.
**Result: met** (20,530 cells; 327/335 markets geolocated; 8 flagged; see Ch.3.4).

**Objective 2 — Feature construction.**
*Output:* price-momentum, peer-market, rainfall-anomaly, seasonal, currency and
interaction features, all computed only from data available at time *t*.
*Acceptance:* leakage tests pass (no `t+1` field in the predictor matrix); feature set
documented in a data dictionary.
**Result: met** (`tests/run_checks.py`; Ch.3.4.6).

**Objective 3 — Model comparison under time-ordered validation.**
*Output:* at least two learning models (elastic-net logistic, XGBoost, histogram GBM)
and two baselines (majority, persistence) compared on an **identical** holdout per
target, with ROC-AUC, PR-AUC, F1, balanced accuracy and Brier score, plus uncertainty
intervals.
*Acceptance:* comparison reported separately for each target (no cross-target ranking);
baselines reported; 95% bootstrap intervals reported.
**Result: met with an honest negative finding** — discrimination is modest/weak and
XGBoost does *not* dominate (Ch.4.4; `reports/phase6b_diagnostics.md`).

**Objective 4 — Prospective scoring prototype.**
*Output:* a scoring artefact that validates new input, reconstructs features, applies a
versioned model and writes a separate output without altering historical data.
*Acceptance:* artefact runs on a held-out input; model + metadata saved with version,
training period and seed.
**Result: met as a technical prototype** (`src/fit_final_model.py`, `dashboard/app.py`);
not operationally validated.

**Objective 5 — Commodity/district decision support.**
*Output:* commodity-level performance and district-level exploratory risk scores.
*Acceptance:* every output traceable to an artefact; labelled "exploratory".
**Result: partially met** — commodity results real; district bands must be labelled
exploratory because temporal validation is insufficient (Ch.4).

**How success is assessed (C1.3).** Each objective is judged against an explicit,
checkable criterion rather than a narrative claim:

| Objective | Success is assessed by | Acceptance criterion |
|-----------|------------------------|----------------------|
| 1 Data integration | Panel row count, geolocation match rate, build log | ≥ 20,000 food cells; ≥ 95% of markets matched to a district; log written |
| 2 Feature construction | Automated leakage tests; data dictionary | Predictor matrix contains no `t+1` field; every feature documented |
| 3 Model comparison | Holdout ROC-AUC on an **identical** holdout per target, with a 95% bootstrap CI, versus baselines | A model demonstrates *reliable prospective discrimination only if* holdout ROC-AUC > 0.50 **and** its 95% CI excludes 0.50 **and** it beats the majority baseline on the same observations |
| 4 Scoring reliability | Re-running the versioned artefact on fixed input reproduces recorded scores | Deterministic given the saved model, metadata and seed; separate output file |
| 5 Geographic presentation | Traceability of district scores to market scores; labelling | Every district score traceable to an artefact and labelled "exploratory, model-generated" |

Applying the Objective-3 criterion honestly, the Y1 target **fails** it (holdout ROC-AUC
near 0.50 with an interval spanning chance) while Y2 partially passes — this is reported
as a finding, not concealed (Ch.4.4, Ch.5.3).

## 1.6 Motivation

Earlier information about market pressure gives government and humanitarian actors more
time to verify conditions before they worsen. The project is also an exercise in honest
applied data science: combining heterogeneous real data (prices, CHIRPS rainfall,
boundaries, population), engineering leakage-safe features, and evaluating models on
*later* observations rather than a random split. The project explicitly treats
validation design and the limits of the available data as core, not incidental.

## 1.7 Stakeholders and intended primary users

The **primary user is a national market-monitoring analyst** (e.g. within WFP market
monitoring or a government food-security unit) who reviews monthly market data and
decides where to prioritise verification. Secondary users: FEWS NET/ZimVAC/ZimLAC
analysts (cross-checking), humanitarian programme staff (screening for market
assessments), district officers (local verification), and researchers.

The system is **decision support only**: a high probability should trigger verification
against local information, existing assessments and household data — never an automatic
decision about districts or households.

## 1.8 Project Scope

**Geographic:** Zimbabwe; market, commodity and administrative-district level (10
admin-1 provinces; 91 admin-2 districts).
**Temporal coverage (verified):** food prices 2010-01 → 2026-05; CHIRPS rainfall
1981-01 → 2026-08 (climatology baseline 1981–2015).
**Includes:** data cleaning and harmonisation, geographic matching, leakage-safe feature
engineering, construction of two stress targets, model comparison with time-ordered
validation, probability scoring and geospatial presentation.
**Excludes:** prediction of household food consumption, poverty, malnutrition, famine or
individual vulnerability; long-term (seasonal/annual) forecasting; temperature, soil
moisture, vegetation/NDVI, crop yield, conflict, fuel-price, border and informal-FX data
(not available).

## 1.9 Project Assumptions (each linked to a validation procedure)

| Assumption | How it is tested in this project |
|------------|----------------------------------|
| Price and rainfall data are usable after cleaning | Data-quality report; zero/negative prices removed; log returns finite (`tests/run_checks.py`) |
| Datasets can be linked | 327/335 markets matched to districts; unmatched 8 flagged, not silently assigned |
| Time order is respected | Only trailing windows/expanding peer statistics; holdout begins the month after training ends |
| Future information can be excluded | Leakage tests: the predictor matrix contains no `t+1` field; rolling features verified |
| Price/rainfall features contain signal | Feature-exclusion experiments (`phase6b_feature_exclusion.csv`) |
| Patterns may transfer to later periods | Forward holdout + by-year/by-currency analysis; transfer is **not** assumed (Ch.4) |
| A prediction is an early-warning signal, not household insecurity | Explicit scope boundary and interpretation statement |

Where an assumption is not supported (e.g. transferability), it is recorded as a
limitation rather than hidden.

## 1.10 Definition of key terms (supervisor C1.4)

- **Prediction unit:** one `market × commodity × currency × month` observation.
- **Forecast horizon:** the **following** calendar month (1 month ahead).
- **Food price stress (this project):** a *market price* event — either (Y1) a
  standardised next-month log return ≥ +1.0 SD of the series' trailing distribution, or
  (Y2) a next-month price ≥ 1.20 × the peer-market median for the same commodity and
  currency. See Chapter 3.4.12.
- **Not the same as price inflation:** inflation is a general, sustained change in the
  price level; stress here is a *relative, local, one-month* price movement.
- **Not the same as household food insecurity:** insecurity depends on income, assets,
  labour, remittances, own production and social protection, none of which are in the
  feature set. A market signal is not a household classification.

## 1.11 Relevance and Significance

The project is relevant because it shows how dispersed Zimbabwean data sources can be
integrated into one reproducible process, and it is significant because it provides a
transparent, updatable market signal that can supplement — not replace — existing
monitoring. Its most defensible contribution is the **documented, leakage-controlled,
reproducible workflow**, together with an honest account of limited temporal
generalisability (see Chapter 5).

## 1.12 Chapter Summary

This chapter introduced the project, stated the specific missing capability, defined
food price stress precisely (unit, horizon, and its distinction from inflation and
household insecurity), set measurable objectives with acceptance criteria, named the
primary user, fixed the temporal coverage, and tied each assumption to a validation
procedure. Chapter 2 reviews the literature; Chapter 3 gives the reproducible method.
