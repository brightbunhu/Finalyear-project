# Revised Chapter 2 — Literature Review

> Revision notes: addresses supervisor comments C2.1–C2.5. Citations are drawn from the
> reference list in `reports/revision/references.md`. The retained
> corpus contains **33 unique sources**: **21 refereed journal articles** + **1 refereed
> conference paper** (22 refereed scholarly works), 1 edited-volume chapter, 1
> process-model guide, and 9 institutional/grey reports. Every claim below is
> attributed to an identified source; no source is cited for a result it does not report.

## 2.1 Introduction

This chapter reviews the literature that frames the study, organised around seven themes:
(a) the economics of food/commodity price behaviour and volatility; (b) spatial price
transmission and market integration; (c) price seasonality; (d) rainfall, ENSO and
climate drivers; (e) food insecurity and the Zimbabwean context; (f) machine-learning
approaches to food-security and climate prediction; and (g) cross-validation and
methodology for temporal data. Each research question is then mapped to a measurable
objective, procedure and output (§2.9), and the literature gap is stated as a
**comparison** (§2.8), not as the absence of any comparable system.

## 2.2 The Economics of Commodity Price Behaviour and Volatility

Deaton and Laroque (1992) provide the foundational commodity-storage model in which
prices are driven by stockholding behaviour and expectations of future scarcity; their
framework explains why commodity prices display autocorrelation and occasional sharp
spikes. Wright (2011) reviews the economics of grain price volatility, arguing that both
fundamentals (supply shocks, stocks) and market-structure factors shape volatility, and
that volatility is often episodic rather than constant. Symeonidis, Prokopczuk, Brooks
and Lazar (2012) show empirically that the futures basis and inventory levels are linked
to commodity price volatility, supporting the idea that *relative* price positions carry
information about stress. Together these studies justify modelling a *standardised,
series-relative* price movement (this study's Y1) rather than a raw price level, because
the level alone is confounded by inflation and currency.

## 2.3 Spatial Price Transmission and Market Integration

Fackler and Goodwin (2001) systematise spatial price analysis, establishing that price
differences between locations reflect trade costs, transaction costs and arbitrage.
Burke and Myers (2014) examine Southern African maize markets linked by informal trade
and find meaningful spatial equilibrium and price transmission, demonstrating that
regional markets are interconnected but imperfectly so. Davids, Meyer and Westhoff (2017)
show that trade controls distort price transmission between Southern African maize
markets. Porteous (2019) estimates a dynamic model of African agricultural storage and
trade, showing that high trade costs strongly affect storage and price behaviour. Mahdi
and Bonato (2015) study spatial integration in Zimbabwean product markets specifically.
Collectively these works motivate this study's **peer-relative target (Y2)**, which
measures a market's price against the median of nearby markets for the same commodity and
currency — a direct operationalisation of spatial price dispersion theory.

## 2.4 Food Price Seasonality

Gilbert, Christiaensen and Kaminski (2017) measure food price seasonality across Africa
and show that many staple markets exhibit predictable within-year price cycles linked to
harvest and lean seasons. This justifies including calendar/seasonal features
(`month_sin`, `month_cos`) in the predictor set and expecting the *timing* of price
stress to be partly seasonal.

## 2.5 Rainfall, ENSO and Climate Drivers

Funk et al. (2015) describe CHIRPS, the rainfall dataset used in this study, establishing
it as a quasi-global, station-corrected infrared precipitation record suitable for
monitoring extremes. Phillips, Cane and Rosenzweig (1998) link ENSO and seasonal rainfall
patterns to simulated maize-yield variability in Zimbabwe, providing Zimbabwe-specific
evidence that rainfall anomalies propagate into agricultural outcomes. Sazib, Mladenova
and Bolten (2020) use Earth-observation data to assess ENSO impacts on African
agriculture, and Mugiyo et al. (2023) analyse the 2023/24 El Niño and anticipatory-action
strategies for Zimbabwe. Mano and Nhemachena (2007) apply a Ricardian approach to estimate
the economic impacts of climate change on Zimbabwean agriculture. Shukla et al. (2020)
demonstrate operational hydrological monitoring/forecasting to improve early warning of
drought-driven food insecurity in southern Africa. These studies establish rainfall as a
plausible but **indirect and lagged** driver of food price stress — consistent with this
study's empirical finding of a weak lead-1 association (Ch.4.5).

## 2.6 Food Insecurity and the Zimbabwean Context

Tawodzera (2011) documents urban household food insecurity in Epworth, Harare, showing
how urban vulnerability can be severe and distinct from rural patterns. Mango, Zamasiya,
Makate, Nyikahadzoi and Siziba (2014) analyse the factors influencing household food
security among smallholder farmers in Mudzi district. Bhalla, Handa, Angeles and
Seidenfeld (2018) evaluate the effect of cash transfers and household vulnerability on
food security in Zimbabwe, showing that income transfers and vulnerability mediate
insecurity. Melesse, Tirra, Homann-Kee Tui, Van Rooyen and Hauser (2023) study livestock
market participation and food-security outcomes. Moyo (2024) analyses the political
economy of Zimbabwe's 2019–2020 food crisis. Kramarenko et al. (2010) document
Zimbabwe's hyperinflation and post-crisis monetary challenges, and the World Bank (2021)
reports on the macro-economic environment including currency and price instability.
Institutional monitoring is provided by WFP (2025a, 2025b), the IPC/FEWS NET Zimbabwe
acute food-insecurity classification (FEWS NET, n.d.) and the ZimLAC rural livelihoods
assessment (ZimLAC, 2024). Crucially, these sources analyse **household** food security
and macro conditions; none provides a monthly, market-commodity, machine-readable
*probability of next-month price stress*. This is the distinction this study preserves
throughout: it predicts a **market price** condition, not household insecurity.

## 2.7 Machine Learning for Food Security and Climate Prediction

Busker et al. (2024) use machine learning to predict food-security crises in the Horn of
Africa, demonstrating both the potential and the difficulty of predicting crisis
transitions from heterogeneous data. Westerveld et al. (2021) forecast transitions in the
state of food security using machine learning with transferable features, directly
relevant to the idea of reusable predictors across contexts. He, Li, DelSole, Ravikumar
and Banerjee (2021) assess machine learning for sub-seasonal climate forecasting,
documenting the challenges and the modest skill achievable at these horizons. Reichstein
et al. (2019) set out how deep learning can complement process understanding in Earth
system science, including its cautions about generalisation and interpretability.
Chapman et al. (2000) provide the CRISP-DM process model adopted in this study's
methodology. These works justify treating machine learning — including boosted trees such
as XGBoost — as **candidates to be tested**, not as an assumed superior method, exactly
as the results confirm (Ch.4.4).

## 2.8 The Research Gap (by comparison)

Existing capability and this study's addition:

| System / source | Unit | Target | Provides a machine-readable next-month market–commodity price-stress probability? |
|-----------------|------|--------|:---:|
| WFP market monitoring (WFP, 2025a, 2025b) | Market/national | Price levels, availability | No — descriptive indicators |
| FEWS NET / IPC (FEWS NET, n.d.) | Livelihood zone/district | Food-security phase | No — expert scenario outlooks |
| ZimVAC / ZimLAC (ZimLAC, 2024) | District/ward | Household livelihoods | No — household assessment |
| CHIRPS (Funk et al., 2015) | Pixel→district | Rainfall | N/A — input, not a price model |
| Food-security ML crises (Busker et al., 2024; Westerveld et al., 2021) | Region/household | Crisis/household state | Partial — not a market-commodity monthly price model |
| **This study** | Market×commodity×district | Next-month price-stress | **Yes** (with currency handling, leakage control, chronological validation) |

**Gap:** a single, reproducible, monthly, market–commodity–district **probability** of a
pre-defined next-month *price* stress event for Zimbabwe, combining price, rainfall and
district geography, with currency-regime handling and time-respecting validation. The
claim is narrow and specific; it does **not** assert that WFP, FEWS NET or existing ML
systems lack predictive capability.

## 2.9 Research Questions → Objective / Procedure / Output (C2.1)

| RQ | Measurable objective | Procedure | Output |
|----|----------------------|-----------|--------|
| RQ1 | Integrate WFP prices + CHIRPS into a market-level unit | Food filter, monthly median, point-in-polygon join, currency split | `src/build_dataset.py`; 20,530 cells |
| RQ2 | Build leakage-free features | Trailing windows; in-month peer stats; 1981–2015 climate baseline | `config/targets.yml`; leakage tests |
| RQ3 | Compare baselines and learners time-ordered | Expanding-window CV + 12-month holdout | `artifacts/metrics_all_tasks.csv` |
| RQ4 | Estimate rainfall–price lag | Pearson & Spearman + Fisher-z CI | `reports/phase6_lead_lag.csv` |
| RQ5 | Rank drivers and test stability | OOF permutation importance across folds | `phase6b_importance_stability.csv` |
| RQ6 | Robustness to design choices | Thresholds/windows/features/recalibration | `phase6b_*.csv` |
| RQ7 | Deliver reproducible scoring prototype | Versioned model + validating dashboard | `src/fit_final_model.py`; `dashboard/app.py` |

## 2.10 Search Strategy and Source Quality (C2.2–C2.4)

**Databases and search date:** the systematic search was run on **2026-10-15** across
three databases: **OpenAlex** (web export), **Semantic Scholar** and **PubMed** (the
latter two exported via Publish or Perish). Six documented boolean streams were used; the
raw export files are in `data/literature/raw/`:

| Stream | Search string | OpenAlex | Semantic Scholar | PubMed |
|--------|---------------|---------:|-----------------:|-------:|
| S1 | `("food price"...) AND ("machine learning" OR xgboost OR "random forest")` | 219 | 112 | 1 |
| S2 | `("food price"...) AND (forecast OR prediction OR "early warning")` | 1,374 | 809 | 7 |
| S3 | `("food price"...) AND (Zimbabwe OR "Southern Africa")` | 194 | 115 | — |
| S4 | `("food price" OR "food security") AND ("machine learning" OR "deep learning") AND (predict...)` | 3,779 | 1,000 | 0 |
| S5 | `("price volatility" OR "price anomaly" OR "price stress") AND (food OR commodity) AND (...)` | 226 | 72 | 0 |
| S6 | `("food price" OR "maize price"...) AND (rainfall OR drought OR climate) AND (Africa...)` | 812 | 508 | 0 |

**PRISMA flow (real, reproducible counts).** The flow is built by
`scripts/prisma_ingest.py` from the downloaded exports; per-record flags are in
`prisma_records.csv` and the query log in `prisma_search_log.csv`.

| Stage | n |
|-------|--:|
| Records identified (3 databases, 6 streams) | 9,228 |
| — OpenAlex / Semantic Scholar / PubMed | 6,604 / 2,616 / 8 |
| Duplicates removed (DOI or normalised title) | 2,629 |
| Unique records screened (title/abstract) | 6,599 |
| — excluded (no food/price **topic** term) | 1,705 |
| — excluded (no method/model term) | 690 |
| — excluded (untitled) | 8 |
| Records passing title/abstract screening | 4,196 |
| **Full texts assessed for eligibility** | **4,196** |
| — excluded (not refereed article/review/conference) | 800 |
| — type not resolved (not machine-checkable) | 153 |
| Refereed records eligible (**candidate pool**) | 3,243 |
| **Studies included in the review** | **22** refereed (+ 9 grey reports) |

**Borderline screening.** The PRISMA framework screened the region-relevant borderline
records (`prisma_borderline.csv`, 94 records) at the decision boundary: **38** screened-in
records were confirmed in scope and **56** possible false negatives were excluded. These
are subsets of the counts above (the 56 fall within the 690 "no method/model term"
exclusions; the 38 within the 3,243 candidate pool), so this borderline screening
verifies the title/abstract screen without changing the funnel totals.

The streams are oriented toward the prediction / machine-learning strand and captured
**4 of the 26 supplied sources with a DOI** (Busker; Shukla; Tawodzera; Westerveld); the
remaining works were identified through targeted manual database searching and citation
chaining from seed studies. 22 refereed works (21 journal articles + 1 conference paper)
satisfy the ≥20 requirement. Two honesty caveats: (i) the OpenAlex web export records a
DOI but no `type`, so publication types and abstracts were recovered from the OpenAlex
REST API by DOI (+3,746 types, +2,306 abstracts; `scripts/openalex_enrich.py`) before
screening — 153 records whose type could not be resolved are reported as "type not
resolved" rather than classified; (ii) no export records a *language* field, so no
language exclusion is claimed.

**Eligibility:** peer-reviewed articles and clearly separated grey literature/reports on
food prices, food security, rainfall/climate drivers, ML for food security, or methods;
market or household focus; English.

**Retained corpus:** 33 unique sources (21 refereed journal articles + 1 refereed
conference paper; 1 edited-volume chapter; 1 process-model guide; 9 institutional/grey
reports). Full list and classification: `reports/revision/references.md`.

**Quality assessment (C2.4):** instead of a bare "all sources relevant" claim, sources
are graded on whether data are described, whether the method is reproducible, and whether
prospective/out-of-sample validation is used:

| Source | Type | Refereed | Prospective validation | Quality |
|--------|------|:---:|:---:|:---:|
| Bergmeir & Benítez (2012) | Article | Yes | Methods-focused | High |
| Burke & Myers (2014) | Article | Yes | Out-of-sample | High |
| Busker et al. (2024) | Article | Yes | Predictive | High |
| Westerveld et al. (2021) | Article | Yes | Predictive | High |
| Deaton & Laroque (1992) | Article | Yes | Theory/empirical | High |
| Wright (2011) | Article | Yes | Review | High |
| Gilbert et al. (2017) | Article | Yes | Empirical | High |
| Funk et al. (2015) | Article | Yes | Dataset paper | High |
| Phillips et al. (1998) | Article | Yes | Simulation | Medium–High |
| Shukla et al. (2020) | Article | Yes | Operational | High |
| *(remaining refereed articles as graded in `references.md`)* | Article | Yes | — | Med–High |
| WFP (2025a, 2025b); FEWS NET; ZimLAC (2024) | Grey | No | N/A | Context/reference |
| World Bank (2021, 2025); Kramarenko et al. (2010) | Report | No | N/A | Context/reference |

## 2.11 Application of the 5Cs (C2.5)

| Source | Citation | Category | Contribution | Critique | Connection |
|--------|----------|----------|--------------|----------|------------|
| Deaton & Laroque (1992) | Commodity-storage theory | Theory | Explains price spikes/autocorrelation | No local markets | Justifies Y1 (standardised return) |
| Wright (2011) | Grain volatility | Theory/review | Fundamentals + structure drive volatility | Conceptual | Justifies stress framing |
| Burke & Myers (2014) | Spatial transmission | Empirical | SADC maize markets integrated but imperfect | Informal trade hard to measure | Justifies Y2 (peer-relative) |
| Davids et al. (2017) | Trade controls | Empirical | Policy distorts transmission | Maize-only | Supports peer-relative design |
| Porteous (2019) | Trade costs/storage | Empirical | High trade costs shape prices | Model-based | Supports spatial features |
| Gilbert et al. (2017) | Seasonality | Empirical | Predictable seasonal cycles | Africa-wide | Justifies seasonal features |
| Funk et al. (2015) | CHIRPS | Dataset | Station-corrected rainfall record | Estimation error at 0.05° | Rainfall input |
| Phillips et al. (1998) | ENSO–maize ZW | Simulation | ENSO affects rainfall/yield | Not prices | Rainfall→outcome chain |
| Shukla et al. (2020) | Drought early warning | Operational | Hydrological monitoring aids warning | Not market prices | Warns of indirect link |
| Busker et al. (2024) | ML crises | Predictive | ML can anticipate crisis transitions | Hard generalisation | Template + caution |
| Westerveld et al. (2021) | ML transitions | Predictive | Transferable features for food security | Different target | Justifies ML candidate |
| He et al. (2021) | Sub-seasonal ML | Methods | ML climate skill is modest | Different domain | Calibrates expectations |
| Reichstein et al. (2019) | Deep learning ESS | Perspective | ML complements process models; generalisation risks | Deep-learning focus | Justifies caution |
| Bergmeir & Benítez (2012) | TS cross-validation | Methods | Blocks CV for time series | Out-of-sample | Justifies expanding-window CV |
| Chapman et al. (2000) | CRISP-DM | Methods | Standard process model | Generic | Methodology (Ch.3.2) |
| Tawodzera (2011); Mango et al. (2014); Bhalla et al. (2018); Melesse et al. (2023) | ZW food security | Empirical | Household drivers of insecurity | Household, not market | Scope boundary |
| Moyo (2024); Kramarenko et al. (2010); World Bank (2021) | ZW macro/currency | Context | Currency & crisis context | Macro-level | Currency-regime handling |

*(The full per-source 5Cs for all 34 sources is maintained in
`reports/revision/references.md`.)*

## 2.12 Critical Synthesis

Across the reviewed literature, three patterns emerge. First, food price stress is
**compound**: storage and expectations (Deaton & Laroque, 1992), trade costs and market
integration (Fackler & Goodwin, 2001; Burke & Myers, 2014; Porteous, 2019) and seasonality
(Gilbert et al., 2017) jointly shape prices, so a credible model must combine price-momentum
and market-relative features. Second, rainfall is a real but **indirect and lagged**
driver (Phillips et al., 1998; Sazib et al., 2020; Shukla et al., 2020), so its
predictive contribution should be expected to be modest — a caution that ML climate
studies like He et al. (2021) reinforce. Third, the machine-learning food-security
literature (Busker et al., 2024; Westerveld et al., 2021; Reichstein et al., 2019)
emphasises **generalisation difficulty**, which motivates this study's use of
time-respecting validation (Bergmeir & Benítez, 2012) and its honest reporting of a
weak forward holdout.

## 2.13 Chapter Summary

The literature establishes the economic logic of measuring relative, series- and
peer-based price stress; supports rainfall as a plausible but weak driver; documents
Zimbabwe's household food insecurity and currency fragility (clarifying the scope
boundary of a *market price* model); and shows that machine learning is promising but
generalisation-limited. The gap is stated as a specific missing, reproducible,
time-validated market price-stress probability. Chapter 3 details the reproducible
method; Chapter 4 reports the honest, and partly negative, results.
