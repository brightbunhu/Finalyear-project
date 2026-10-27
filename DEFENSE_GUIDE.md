# Zimbabwe Food-Price Stress Prediction

## Defense Preparation Guide

**A plain-language walkthrough of every dashboard page, the numbers to memorise, and what to say in the viva**

Project: Early Warning Machine Learning Architecture for Food Price Stress and Anomalies in Zimbabwe

Prepared from the live dashboard code and the stored pipeline artefacts.

---

## How to use this guide

This document explains the dashboard the way an examiner will experience it. For every page you get:

- **What it shows** — the controls and the output.
- **What it is for** — the one job that page does.
- **What to say** — a short, defensible sentence you can use in the presentation.
- **The data behind it** — the artefact or calculation that produces the numbers.

Sections 5 to 8 are the ones to revise the night before: the numbers table, the glossary, the demo script and the question-and-answer bank.

> **The single most important message:** the dashboard is the evidence layer of a reproducible pipeline. It does not train models live, it does not invent values, and it is not an official early-warning system. Every number is read from a stored artefact, and every page states its provenance.

---

## Contents

1. The system in one page
2. How the user interface is organised
3. Page-by-page walkthrough
4. Architecture: how the dashboard is built
5. Numbers to memorise
6. Glossary of terms examiners may ask about
7. A six-minute demonstration script
8. Viva questions and model answers
9. Limitations you must state
10. Issues found and fixes applied
11. Pre-defense checklist

---

# 1. The system in one page

The project predicts **market food-price stress** in Zimbabwe using a supervised machine-learning pipeline. The dashboard is the presentation layer over that pipeline.

The pipeline does five things:

1. **Ingests** WFP food prices, WFP market coordinates, CHIRPS rainfall, geoBoundaries district polygons and HDX population data.
2. **Harmonises** market coordinates to districts with a point-in-polygon join, and aggregates rainfall to district-month values.
3. **Builds a model-ready panel** of monthly market-commodity-currency cells with engineered features and next-month labels.
4. **Trains and evaluates** five learners — majority baseline, persistence baseline, logistic regression, histogram gradient boosting and XGBoost — using expanding-window cross-validation and a final forward holdout.
5. **Persists** metrics, predictions, figures, reports and model binaries. The dashboard reads only these persisted artefacts.

### The four prediction tasks

| Task | Price base | Target | Meaning |
|---|---|---|---|
| T1 | USD | Y1 | Will this market-commodity cell have an unusually large next-month price increase (standardised return z ≥ 1.0)? |
| T2 | USD | Y2 | Will this cell be at least 20% above the national peer median next month (SPI ≥ 1.20)? |
| T3 | Nominal local currency | Y1 | Same as T1, on the nominal price base. |
| T4 | Nominal local currency | Y2 | Same as T2, on the nominal price base. |

The two price bases are never pooled. The two targets answer different questions: **Y1 is temporal volatility**, **Y2 is spatial market divergence**.

### The four headline facts

| Fact | Value |
|---|---|
| Raw price rows ingested | 28,168 |
| Monthly food cells after cleaning | 20,530 |
| Markets matched to a district | 327 of 335 (8 unmatched, not imputed) |
| Best forward-holdout result | T2 USD Y2, HistGBM: ROC-AUC **0.883** |

> **Say this:** "The dashboard is the presentation and evidence layer of the project. The pipeline produces the data, models and metrics; the dashboard lets an examiner inspect every stage without rerunning the code. Nothing shown is fabricated — missing artefacts produce an explicit 'not available' state."

---

# 2. How the user interface is organised

The app has **seven top-level sections** in the dark navy sidebar. Some sections contain sub-pages, switched by the segmented control (the row of pill buttons) under the page title.

| Sidebar section | Icon | Sub-pages |
|---|---|---|
| Home | House | Home |
| Make a Prediction | Pencil | Prediction Studio |
| Geographic Explorer | Map | Geographic Explorer |
| Data & Integration | Database | Dataset Catalogue, Coverage & Quality, Price Trends, Rainfall & Climate |
| Model Performance | Line chart | Overview, Holdout Predictions, Statistical Analysis |
| Reports & Downloads | Document | Research Evidence, Downloads |
| About & Help | Info | About, Limitations & Interpretation |

Those are the twelve screens in the `screenshots/` folder. The current app groups them into seven sections; the screenshots were captured from the earlier twelve-page layout.

### The persistent app shell

- **Sidebar brand:** Zimbabwe flag, "Food-Price Stress", "Zimbabwe research".
- **Sidebar navigation:** the seven sections with icons.
- **Sidebar footer:** a research-prototype disclaimer on every page.
- **Top app bar:** project title and two real, artefact-derived values — latest data month and panel row count.
- **Page header:** section title, subtitle, and (on sub-pages) a provenance line naming the files behind the page.

### How navigation works technically

`dashboard/app.py` is a router. It defines the sections, renders the sidebar radio, and imports only the active page module. Each page module exposes a single `render()` function. This keeps the app fast and means a broken page cannot take down the whole dashboard.

---

# 3. Page-by-page walkthrough

## 3.1 Home

### What it shows

- Two top cards: **Latest data** month and the **latest scored holdout** month.
- Four KPI cards: datasets integrated, records combined, latest available month, model used.
- A **district choropleth** of Zimbabwe, with controls for **Target** (Y1 or Y2) and **District metric** (mean predicted probability or observed stress share).
- A **top-five highest estimated risk** list beside the map, with risk badges.
- A **Food-Price Stress Summary** panel: mean holdout score, risk band, share of scored cells at or above 0.50, and the training prevalence.
- A **monthly trend line** of the mean holdout score.
- A bottom row: Key Insights, Top Districts bar chart, Data Integration Pipeline status, and a metadata strip.

### What it is for

A one-screen situational summary: what data exists, what the model scored, and where estimated stress is highest.

### What to say

> "Home is the executive overview. It answers three questions: what data do we have, what did the model score, and where is estimated stress highest? The map shows historical holdout scores aggregated by district. It is not a live forecast, and it is not household food insecurity — it is market-price stress estimated by the model."

### The data behind it

- Panel: `data_processed/panel_usdprice.parquet` (20,530 rows, 2010-01 to 2026-05).
- Predictions: `artifacts/preds_T1_usd_y1.parquet` or `preds_T2_usd_y2.parquet`.
- Boundaries: `raw/geo/zwe_adm2_geoboundaries.geojson`.
- Model cards: `models/*.meta.json`.

### Things to be precise about

- **Risk badges are relative, not official.** `HIGH` means at least max(2 × training prevalence, prevalence + 0.15); `ELEVATED` means at least 1.3 × prevalence; `ABOVE BASELINE` means at least prevalence; otherwise `BELOW BASELINE`.
- **The map is not a household measure.** A district is coloured only if it has scored market rows with a name matching the boundary file.
- **Month filtering is done through the Chart filters.** Month, district, category, commodity and market selections apply consistently to the map, the summary, the ranking and the trend. Leaving a field empty includes every value.

---

## 3.2 Make a Prediction (Prediction Studio)

### What it shows

A model-target selector at the top, then four tabs:

1. **Market Calculator** — enter the **observation month** (e.g. October), the price in that month, the price in the previous two months, the price three months back, the currency, the peer median for the observation month and the weather condition. The model predicts stress for the **next month** after the observation (e.g. November). The calculator derives returns, SPI, lags and rolling returns, seasonality from the target month and rainfall features, then scores both the Y2 and Y1 models. A button can load a real example from the panel for the chosen district and commodity. You can test past months (retrospectively) or build a next-month forecast using current observations.
2. **Advanced Technical Mode** — direct editing of the 15 numeric and 2 categorical features, with the option to load a real example from the latest eligible panel month.
3. **CSV Batch Prediction** — download a template, upload a CSV, score every row, download the scored file.
4. **Input Schema & Feature Quality** — lists the exact features the persisted model expects.

### What the calculator computes

From the everyday inputs, it derives:

- month-over-month return from the observation-month and previous-month prices (t vs t-1);
- lagged returns from t-1 vs t-2 and t-2 vs t-3;
- a standardised return z-score using a district volatility and drift assumption;
- the Spatial Price Index (SPI) = observation-month price ÷ observation-month peer median;
- lagged and rolling return features;
- rainfall anomaly and lag features from the selected weather condition;
- seasonal harmonic features from the **target month** (t+1), not the wall-clock month;
- a climate-price interaction term.

Set the observation month to the most recent month you have data for and the model predicts stress in **t+1**. You can also set an earlier observation month to test the model retrospectively against known outcomes. The model always answers: *given conditions in month t, what is the probability of stress in month t+1?*

The resulting 17-feature row is passed to the saved `HistGradientBoostingClassifier` pipeline. The page returns:

- four technical metric cards (observed change, SPI, rainfall anomaly, interaction);
- two probability cards (Y2 and Y1) with risk bands and progress bars;
- a plain-English early-warning summary;
- three generic operational recommendations;
- an expander showing the exact feature vector that was scored.

### What to say

> "This page turns the model into a decision-support tool. You choose the month you want to predict for, enter that month's price, the previous two months and the peer median, and the calculator builds the same 17-feature vector used in training before asking the saved model for a probability. The Advanced tab exposes the exact feature vector for transparency."

### The critical caveat

The intuitive mode still uses a few **hard-coded scenario assumptions** in `prediction_studio.py`: district volatility 0.18, drift 0.04, peer count 12, and log population 11.75. The lagged returns are now derived from the prices you enter, and seasonality comes from the target month you choose. Present this mode as a **scenario simulator**; for a fully data-derived demonstration use the **Advanced Technical Mode**, **CSV Batch Prediction**, or the persisted holdout predictions on the Model Performance pages.

### The honest framing

> "The calculator is a communication aid. It shows how observable market conditions map into the model's feature space. The rigorous outputs are the persisted holdout predictions on the Model Performance pages, where the inputs come from real panel rows."

---

## 3.3 Geographic Explorer

### What it shows

- Target selector for all four tasks.
- **Map mode:** predicted probability, predicted risk band, observed historical stress, rainfall anomaly, or data coverage.
- Filters: month, district, category, commodity, and a probability threshold slider.
- Left: choropleth of Zimbabwe's districts using OpenStreetMap tiles.
- Right: top-12 district risk ranking with badges.
- Bottom: district aggregate table and two CSV downloads.

### What it is for

Spatial analysis: where is estimated stress concentrated, and how does that change by target, mode and threshold?

### What to say

> "This page answers 'where?'. It shows the spatial concentration of estimated stress. Districts without scored rows are left uncoloured — absence from the map is a coverage artefact, not evidence of low risk. The values are market-level model outputs, not a household food-security measure."

### The data behind it

District aggregates are computed from the stored prediction files. Rainfall-anomaly mode merges the panel's district rainfall anomaly. Coverage mode colours by the number of scored rows.

---

## 3.4 Data & Integration — Dataset Catalogue

### What it shows

- A six-stage **pipeline overview**: raw sources → market-district crosswalk → rainfall features → model-ready panels → persisted models → prediction artefacts. Each stage has an availability dot and the expected file paths.
- A searchable **artefact catalogue** with stage, path, format, rows, columns, date range, size, modified time, status and purpose.
- A **dataset preview** for selected files: dimensions, date range, column selection, a 200-row sample, missingness and duplicate counts.
- **Integration completeness** metrics with explicit numerators and denominators.
- **Data lineage and caveats.**

### What to say

> "This is the reproducibility page. Every dataset in the project is catalogued with its real path, size, row count, date range and status. It shows the journey from 28,168 raw price rows to 20,530 model-ready food cells, and it states the eight markets that could not be geospatially matched instead of inventing coordinates."

### Integration numbers

| Metric | Value |
|---|---|
| Raw price records integrated | 28,168 |
| Monthly food cells | 20,530 |
| Markets matched to a district | 327 |
| Markets unmatched | 8 |
| Y2-labelable cells | 12,635 of 20,530 (61.5%) |
| Y1-labelable cells | 5,429 of 20,530 (26.4%) |

The eight unmatched markets are Dulibadzimu Market, Kombai, Mandava, Mucheke, Murombedzi, Plumtree town, Renkini Bus Terminus and Tshovani. They are preserved for national baseline calculations but excluded from district-level climate merges and maps.

---

## 3.5 Data & Integration — Coverage & Quality

### What it shows

- Eight KPI cards: total records, unique markets, unique commodities, district coverage, date coverage, Y1 labelability, Y2 labelability, mean missing rate.
- Chart filters for the visual tabs.
- Five tabs: coverage over time, category/currency/district mix, missingness, labelability by month, and a field-quality table with quality rules and flags.
- Documented data-quality notes.

### What to say

> "This page audits the data before modelling. It shows where coverage is thin, how many cells can actually be labelled for next month, and which fields have quality flags. Missing values are reported, never imputed, in the dashboard. Labelability falls at the end of the series because the next month has not been observed yet."

### Numbers to remember

- 20,530 food cells; 335 markets; 26 commodities; 79 districts with price data.
- Date coverage: 2010-01 to 2026-05.
- Y1 labelable: 26.4% (5,429 cells).
- Y2 labelable: 61.5% (12,635 cells).
- Mean missing rate: 12.4%.

The performance gap between Y2 and Y1 starts here: Y2 has more than twice as many usable labelled cells.

---

## 3.6 Data & Integration — Price Trends

### What it shows

- Price-base switch: **USD converted** or **nominal within currency**.
- Filters: months, category, district, commodity, market, and median or mean aggregation.
- Seven tabs: by category, by commodity, by district/market, distribution, month-over-month change, indexed series (first selected month = 100), and the filtered data table with CSV download.

### What to say

> "This is exploratory price analysis. The important methodological choice is that USD and nominal local-currency series are kept separate, because they represent different monetary regimes and mixing them would create misleading trends. Nothing is interpolated across missing months."

### Why the separation matters

Zimbabwe moved between currency regimes during the study period. A nominal ZWL price and a USD price are not the same measurement. The dashboard never puts them on one axis; it makes the user choose a base first.

---

## 3.7 Data & Integration — Rainfall & Climate

### What it shows

- KPIs: rainfall district-month observations, date range, districts in the panel.
- Five tabs: rainfall anomalies over time, seasonal climatology by district, lead-lag correlations, district coverage, and raw data tables.
- The lead-lag tab shows Pearson and Spearman correlations between rainfall at lags 0–3 months and next-month returns, for both price bases.

### What to say

> "Rainfall is treated as an indirect predictor. The strongest association is at a one-month lag, around r = -0.11 in USD and -0.12 nominal. That is statistically detectable but weak, so I present it as association, not causation. Rainfall features still matter: the ablation showed removing them hurts Y1 more than Y2."

### Numbers to memorise

- USD price base, lag 1: Pearson r = **-0.1117**, Spearman ρ = **-0.1338**.
- Nominal price base, lag 1: Pearson r = **-0.1244**, Spearman ρ = **-0.1347**.
- Climatology baseline: 1981–2015, by district and calendar month.
- 1,080 district-by-calendar-month climatology reference points (90 districts × 12 months).

### Why it is in the model even though weak

The ablation in Chapter 4 shows:

- T2 (Y2): removing rainfall leaves ROC-AUC essentially unchanged (0.8456 → 0.8469), because spatial features dominate.
- T1 (Y1): removing rainfall drops ROC-AUC from 0.5886 to 0.5105, close to chance.

That is a nuanced, defensible story: rainfall is not a strong standalone driver of spatial stress, but it carries signal for temporal return surges.

---

## 3.8 Model Performance — Overview

### What it shows

- Task selector T1–T4.
- Four KPIs: best holdout ROC-AUC, PR-AUC, balanced accuracy and Brier score.
- A model-and-validation-boundaries card: estimator, training boundary, holdout start, number of features, training rows and prevalence.
- Seven tabs:
  1. **Comparison** — metric table and charts by model and split.
  2. **Confusion matrix** — at the reported threshold.
  3. **Curves** — ROC and precision-recall figures.
  4. **Calibration** — predicted probability versus observed frequency.
  5. **Importance** — permutation importance where available.
  6. **Threshold and robustness** — threshold sensitivity, bootstrap confidence intervals.
  7. **Full table** — all metric rows for the selected task, with CSV download.

### What to say

> "This is the transparent evaluation page. Cross-validation and the final forward holdout are always shown separately. Baselines — majority and persistence — are included so the examiner can see whether the ML actually adds value. Y1 and Y2 are different tasks and their scores are not comparable."

### Forward-holdout numbers (HistGradientBoosting)

| Task | ROC-AUC | PR-AUC | Precision | Recall | Specificity | Brier |
|---|---|---|---|---|---|---|
| T1 USD Y1 | 0.583 | 0.440 | 0.111 | 0.667 | 0.351 | 0.0847 |
| T2 USD Y2 | **0.883** | 0.546 | 0.656 | 0.583 | 0.947 | 0.0877 |
| T3 Nominal Y1 | 0.592 | 0.275 | 0.113 | 0.667 | 0.365 | 0.0939 |
| T4 Nominal Y2 | 0.876 | 0.454 | 0.522 | 0.462 | 0.950 | 0.0710 |

Also know:

- **T1 XGBoost** has the highest Y1 holdout ROC-AUC at **0.641**, but precision is only **0.101** — roughly nine out of ten alerts would be false. The saved Y1 model is HistGBM.
- **T4 XGBoost** has the highest nominal Y2 ROC-AUC at **0.899**, but HistGBM has better Brier (0.071 vs 0.101).
- Cross-validation, pooled out-of-fold: T2 HistGBM **0.8145**; T1 HistGBM **0.6077**.
- Market-clustered bootstrap, T2 HistGBM: **95% CI [0.788, 0.919]**, entirely above chance.
- Market-clustered bootstrap, T1 HistGBM: lower bound around **0.49**, so the interval can include chance.

### The honest Y1 answer

Y1 is a hard, low-signal task. There are only nine positive events in the T1 holdout. The model can achieve high recall only by generating many false alarms. The dashboard reports this instead of hiding it. That is a strength, not a weakness, in a research defense.

---

## 3.9 Model Performance — Holdout Predictions

### What it shows

- Task selector and model selector (majority, persistence, logistic, HistGBM, XGBoost).
- Filters: month, district, category, commodity, market, and a decision-threshold slider.
- KPIs: mean score, share flagged at the threshold, observed stress, and row count.
- Five tabs: ranked predictions, score distribution with a threshold line, observed-versus-predicted confusion matrix recomputed live, historical district map, and the filtered data table with CSV download.

### What to say

> "This page lets the examiner inspect the actual saved out-of-sample scores, not just aggregate metrics. You can move the decision threshold and watch the confusion matrix recompute. These are historical holdout scores, not live forecasts."

### Why this page exists

Metrics can hide behaviour. This page shows the individual scored cells, their ranking, their distribution and their errors. It is the transparency check on the aggregate numbers.

---

## 3.10 Model Performance — Statistical Analysis

### What it shows

- Dataset selector: USD panel, nominal panel, rainfall anomalies, or the market-district crosswalk.
- Context KPIs and filters (date range, district, category, currency, commodity, market).
- Seven tabs:
  1. **Overview** — descriptive statistics and a downloadable table.
  2. **Distributions** — histogram, box plot, and violin plots by group.
  3. **Trends over time** — aggregation choice, rolling window, seasonality, and a Spearman trend test.
  4. **Group comparisons** — mean by group, box plots, group summary table.
  5. **Correlations** — Pearson or Spearman, heatmap, top pairs, scatter plot with optional OLS line.
  6. **Missingness and quality** — missingness by column and month, duplicate rows, constant columns.
  7. **Statistical tests** — Welch t-test, Mann–Whitney U, one-way ANOVA or Kruskal–Wallis, with effect size and confidence interval where available.

### What to say

> "This is descriptive and inferential statistics on the panel itself, not model validation. Tests only run when sample sizes and group structure permit, and every result is shown with its assumptions and caveats. This is where the lead-lag and group-difference evidence lives."

### Why it matters in the defense

It shows you can do more than fit models: you can describe the data, test assumptions, quantify uncertainty and avoid over-claiming. The page explicitly states that a p-value is not the probability that the null hypothesis is true, and that significance is not practical importance.

---

## 3.11 Reports & Downloads — Research Evidence

### What it shows

- Five provisional research objectives, each mapped to:
  - a plain-language claim;
  - the concrete artefacts that support it;
  - the dashboard page that displays it.
- Status cards showing how many referenced artefacts exist.
- A searchable evidence matrix with objective, claim, artefact path, dashboard location and status.
- Counts of evidenced links and robustness reports.

### What to say

> "This page maps each research objective to the artefact that proves it and the dashboard page that displays it. It makes the project auditable: an examiner can go from claim to file to screen."

### Be upfront

The page itself warns that the objective wording is **provisional**, because the repository does not contain a machine-readable list of verbatim dissertation objectives. Say that before you are asked. Do not quote the groupings as exact dissertation wording.

### The five objectives

| Objective | Implemented in |
|---|---|
| Data integration | Data & Integration |
| Target construction | Coverage & Quality, Statistical Analysis |
| Predictive modelling | Model Performance, Prediction Studio |
| Geographic analysis | Geographic Explorer, Home |
| Reproducibility and limitations | Research Evidence, Limitations & Interpretation |

---

## 3.12 Reports & Downloads — Downloads

### What it shows

- Direct download lists for `artifacts/`, `reports/`, `figures/` and `models/`.
- File name, size, and a download button.
- Files over 40 MB are listed but not offered as inline downloads.

### What to say

> "This is the reproducibility exit. The examiner can download the metrics, figures, reports and saved models directly from the app rather than taking my word for the results."

---

## 3.13 About & Help — About

### What it shows

- Project overview, scope statement and the research-prototype disclaimer.
- A short statement that every figure is read from project artefacts.

### What to say

> "The About page states the scope up front: academic research prototype, not an operational early-warning system, and not a household food-security assessment."

---

## 3.14 About & Help — Limitations & Interpretation

### What it shows

An eleven-item limitation register. Each item has:

- a severity badge (Serious, Caveat, General caution);
- a plain-language explanation;
- the evidence or source;
- the pages it affects;
- interpretation guidance.

The eleven limitations:

1. No prospective validation.
2. The latest snapshot is local, not live.
3. Sparse market-commodity series.
4. Currency-regime differences.
5. Missing or incomplete source files.
6. Missing geographic coordinates.
7. Weak rainfall association.
8. Y2 is partly persistence-driven.
9. Model uncertainty.
10. Market stress is not household food insecurity.
11. Outputs are not official warnings.

### What to say

> "This is deliberately the most honest page. It lists every material limitation: no prospective validation, a local snapshot rather than live data, sparse series, currency-regime differences, missing coordinates, weak rainfall association, Y2's persistence component, model uncertainty, and the difference between market price stress and household food insecurity. It also states what each limitation means for interpretation."

This is your strongest page in a viva. Quote it instead of improvising.

---

# 4. Architecture: how the dashboard is built

### The dashboard layer

| Path | Role |
|---|---|
| `dashboard/app.py` | Router: sidebar, sections, sub-page switcher, static Downloads and About pages. |
| `dashboard/pages/*.py` | One `render()` function per screen. |
| `dashboard/components/layout.py` | Theme CSS, app bar, page headers, cards, KPI rows, badges, risk bands. |
| `dashboard/components/charts.py` | Reusable Plotly figure builders: line, bar, histogram, box, violin, heatmap, scatter, choropleth, confusion matrix. |
| `dashboard/components/filters.py` | Shared chart filter controls. |
| `dashboard/utils/loaders.py` | Cached file access and the artefact catalogue. Missing file returns an empty frame, never fake data. |
| `dashboard/utils/statistics.py` | Descriptive statistics, correlations, hypothesis tests. |
| `dashboard/utils/formatting.py` | Number, percentage and date formatting. |
| `config/targets.yml` | Single source of truth for units, price bases, targets, rainfall, validation and tuning. |

### The pipeline layer

| Script | Role |
|---|---|
| `src/build_rainfall.py` | CHIRPS raster to district-month rainfall, climatology and z-anomalies. |
| `src/build_dataset.py` | Price cleaning, monthly aggregation, crosswalk, features and labels. |
| `src/tune_optuna.py` | Bayesian hyperparameter search on training folds only. |
| `src/train.py` | Model zoo, expanding-window CV, threshold tuning and holdout evaluation. |
| `src/fit_final_model.py` | Fits and persists the final models and metadata. |
| `src/analysis.py` | Lead-lag correlations. |
| `src/robustness.py` | Ablation, bootstrap, sensitivity and stability diagnostics. |
| `src/figures_chapter4.py` | Chapter 4 figures. |

### The artefact layer

- `data_processed/` — panels, rainfall features, crosswalk.
- `artifacts/` — metrics, predictions, folds, Optuna results, run metadata.
- `models/` — `*.joblib` pipelines and `*.meta.json` model cards.
- `figures/` — pre-generated evaluation figures.
- `reports/` — robustness tables and narrative reports.

### Why this architecture is defensible

1. **Separation of concerns.** Data processing, modelling and presentation are separate. The dashboard cannot change a model or a metric.
2. **Traceability.** Every page prints its provenance. Every metric can be traced to a CSV or Parquet file.
3. **No fabrication.** Missing artefacts produce an explicit unavailable state. The UI never substitutes a plausible-looking number.
4. **Reproducibility.** The pipeline is deterministic given the config and seed; the dashboard reads the outputs.
5. **Caching.** Loaders use Streamlit caching keyed on file modification time, so the app is responsive without becoming stale.

---

# 5. Numbers to memorise

### Data

| Quantity | Value |
|---|---|
| Raw WFP price rows | 28,168 |
| Non-food rows removed | 7,638 |
| Monthly food cells | 20,530 |
| Markets | 335 |
| Markets geospatially matched | 327 |
| Markets unmatched | 8 |
| Commodities | 26 |
| Food categories | 5 |
| Districts with price data | 79 |
| Date range | 2010-01 to 2026-05 |
| Y1 labelable cells | 5,429 (26.4%) |
| Y2 labelable cells | 12,635 (61.5%) |
| Y1 prevalence | about 15% |
| Y2 prevalence | about 16% |
| Mean missing rate | 12.4% |

### Model metadata

| Model | Trained through | Holdout from | Training rows | Training prevalence |
|---|---|---|---|---|
| Y1 return HistGBM (USD) | 2025-04 | 2025-05 | 5,346 | 14.9% |
| Y2 peer HistGBM (USD) | 2024-10 | 2024-12 | 12,390 | 16.3% |

### Forward-holdout performance

| Task | Model | ROC-AUC | PR-AUC | Precision | Recall | Brier |
|---|---|---|---|---|---|---|
| T1 USD Y1 | HistGBM | 0.583 | 0.440 | 0.111 | 0.667 | 0.0847 |
| T1 USD Y1 | XGBoost (best AUC) | 0.641 | 0.295 | 0.101 | 0.889 | 0.1415 |
| T2 USD Y2 | HistGBM | **0.883** | 0.546 | 0.656 | 0.583 | 0.0877 |
| T3 Nominal Y1 | HistGBM | 0.592 | 0.275 | 0.113 | 0.667 | 0.0939 |
| T4 Nominal Y2 | HistGBM | 0.876 | 0.454 | 0.522 | 0.462 | 0.0710 |
| T4 Nominal Y2 | XGBoost (best AUC) | 0.899 | 0.477 | 0.329 | 0.885 | 0.1013 |

### Validation and uncertainty

- Cross-validation: 5-fold expanding window, pooled out-of-fold.
- Final holdout: 12 forward months, never used in training, tuning or threshold selection.
- T2 HistGBM CV ROC-AUC: 0.8145.
- T2 HistGBM holdout ROC-AUC: 0.8831.
- T2 HistGBM bootstrap 95% market-clustered CI: [0.788, 0.919].
- T1 HistGBM bootstrap CI lower bound: about 0.49, so it can include chance.

### Rainfall lead-lag

- USD, lag 1: Pearson r = -0.1117, Spearman ρ = -0.1338.
- Nominal, lag 1: Pearson r = -0.1244, Spearman ρ = -0.1347.
- Interpretation: weak association, not causation.

---

# 6. Glossary of terms examiners may ask about

**Y1 — standardised return stress.** A binary label for whether the next month's log price return is at least one standard deviation above the cell's own trailing 12-month average. It captures sudden price acceleration.

**Y2 — peer-relative stress.** A binary label for whether the next month's Spatial Price Index is at least 1.20. It captures a market charging at least 20% more than its national peers for the same commodity and currency.

**SPI — Spatial Price Index.** Price divided by the contemporaneous national peer median for the same commodity and currency. It is only defined when at least five peer markets report.

**Labelable cell.** A row that has enough history or enough peers to construct a valid next-month label. Only 26.4% of rows are Y1-labelable, compared with 61.5% for Y2.

**Prevalence.** The share of labelled cells that are positive (stress). Around 15–16% for both targets. This is why accuracy is misleading and why PR-AUC, precision, recall and Brier are reported.

**ROC-AUC.** The probability that a randomly chosen positive cell is ranked above a randomly chosen negative cell. 0.5 is chance; 1.0 is perfect. It is threshold-independent.

**PR-AUC.** Area under the precision-recall curve. More informative than ROC-AUC when positives are rare.

**Precision.** Of the cells the model flags, what share are truly stressed.

**Recall.** Of the truly stressed cells, what share the model flags.

**Specificity.** Of the non-stressed cells, what share the model correctly leaves unflagged.

**F1.** The harmonic mean of precision and recall.

**Brier score.** Mean squared difference between predicted probability and observed outcome. Lower is better. It rewards calibration, not just ranking.

**Calibration.** Whether a predicted 30% risk actually corresponds to about 30% observed frequency. A model can rank well but be badly calibrated.

**Expanding-window cross-validation.** Time-ordered folds where the training window grows and the validation window moves forward. It prevents training on the future.

**Forward holdout.** The final 12 months, set aside before any training, tuning or threshold selection. It is the most honest estimate of out-of-sample performance.

**Persistence baseline.** A heuristic that predicts next month will be the same as this month. It is a strong baseline for Y2 because spatial stress is persistent.

**Permutation importance.** The drop in ROC-AUC when a feature is randomly shuffled. It measures how much the model relies on that feature out of sample.

**Market-clustered bootstrap.** Resampling whole markets rather than individual rows, to respect the fact that observations within a market are correlated. It gives more honest confidence intervals.

**Ablation.** Removing a group of features and re-evaluating, to see how much that group contributes. The project uses it for rainfall and peer features.

---

# 7. A six-minute demonstration script

### 0:00–0:45 — Open with the problem and the architecture

> "This is a research dashboard for predicting market food-price stress in Zimbabwe. The pipeline ingests WFP prices, CHIRPS rainfall, district boundaries and population data, builds a model-ready panel, and trains and evaluates several models. The dashboard is the evidence layer: it lets you inspect the data, the targets, the spatial patterns, the model comparison and the limitations without rerunning the code."

### 0:45–2:00 — Home

> "This is the one-screen situational summary. Latest data is May 2026. We have 20,530 monthly food cells from 28,168 raw price records and six integrated sources. The map shows model-estimated market-price stress by district. The highest-risk districts are ranked relative to training prevalence. The summary panel shows the mean holdout score and the share of cells at or above 0.50."

Point out that the map is a model output, not a household measure.

### 2:00–3:15 — Prediction Studio

> "I set the observation month to October and enter the October, September and August prices, the October peer median and the rainfall condition. The model predicts stress for November (next month). The system computes the returns, SPI, lags and seasonality from those inputs and asks the saved model for a probability. Here is the Y2 probability and the plain-English summary. The Advanced tab shows the exact 17-feature vector that was scored."

Mention the scenario-assumption caveat in one sentence, then move on.

### 3:15–4:00 — Geographic Explorer

> "I can switch target, switch map mode and change the probability threshold. The ranking updates. Uncoloured districts simply have no scored rows — that is a coverage fact, not a risk judgement."

### 4:00–4:45 — Data & Integration and Coverage

> "This traces 28,168 raw rows to 20,530 food cells. 327 of 335 markets matched to a district; eight are flagged, not guessed. Y2 has 12,635 labelable cells versus 5,429 for Y1, which is the main reason performance differs."

### 4:45–5:45 — Model Performance

> "For T2 USD Y2, HistGBM reaches 0.883 holdout ROC-AUC, 0.656 precision, 0.947 specificity and a Brier score of 0.088. For T1 USD Y1, performance is much weaker: 0.583, and the bootstrap interval can include chance. Baselines are shown so you can see whether the ML adds value. Here are the calibration, confusion matrix and threshold sensitivity."

### 5:45–6:30 — Limitations and close

> "I want to be explicit about the limits. This is retrospective, not prospectively validated. The snapshot is local, not live. Rainfall association is weak. Y2 is partly persistence. And market price stress is not household food insecurity. The next steps would be prospective validation, more complete surveys, a hierarchical spatial model and external validation against household data."

---

# 8. Viva questions and model answers

### "Is this real-time or live?"

No. It reads a local snapshot produced by the pipeline. "Latest data" means the newest month in that snapshot (currently May 2026), not a live feed.

### "How did you prevent data leakage?"

Expanding-window cross-validation; the final 12 months are held out and untouched; features use only information available at time t; labels use t+1; imputers and scalers are fitted inside each fold; Optuna and threshold selection never see the holdout.

### "Why is Y2 so much better than Y1?"

Y2 has more than twice as many labelable cells (12,635 versus 5,429), and peer-relative stress is partly persistence-driven: the current SPI is highly informative about next month's SPI. Y1 is a sudden return spike with only nine positive holdout events, so it is statistically fragile.

### "What does a predicted probability mean?"

It is the model-estimated chance that a market-commodity cell will meet the next-month stress definition. It is not the probability of household food insecurity and not an official warning.

### "Why do you have four tasks?"

To test whether conclusions hold across two price bases (USD versus nominal) and two definitions of stress (temporal return surge versus spatial peer premium). It is a robustness design, not four separate products.

### "What is the Spatial Price Index?"

Price divided by the contemporaneous national peer median for the same commodity and currency, defined only when at least five peer markets report. SPI ≥ 1.20 means the market is at least 20% above its peers.

### "Why use ROC-AUC if the classes are imbalanced?"

ROC-AUC is reported alongside PR-AUC, precision, recall, F1, specificity and Brier. The threshold is tuned by F1 on validation, not fixed at 0.5. Accuracy is deliberately not the headline.

### "Why not use XGBoost everywhere if it has higher AUC on T1 and T4?"

Because AUC is not the only criterion. On T1, XGBoost's precision is about 10%, meaning nine out of ten alerts would be false. On T4, HistGBM has a materially better Brier score. The project reports the full trade-off rather than selecting the highest single number.

### "Why is rainfall included if the correlation is weak?"

It is an indirect predictor. The ablation shows removing rainfall hurts Y1 substantially (about eight AUC points) but does not collapse Y2, where spatial features dominate. It is kept for interpretation and robustness, not as a causal driver.

### "What are the biggest limitations?"

No prospective validation; local snapshot; sparse series and few Y1 positives; currency-regime differences; eight unmapped markets; uncertain calibration; and market stress is not household food insecurity. The Limitations page lists all of them with evidence.

### "How do you know the dashboard is showing real numbers?"

Every page has a provenance line naming the file behind it. The loaders read directly from `artifacts/`, `data_processed/`, `models/`, `figures/` and `reports/`. Missing files produce an explicit unavailable state. The Downloads page lets you inspect the raw files yourself. The only displayed values that were not artefact-derived were two hard-coded AUC captions, which have now been replaced with live reads from the metrics file.

### "What would you do next?"

Prospective validation; more frequent and complete market surveys; a hierarchical or spatial model; recalibration over time; external validation against household food-security data; and a formal cost-sensitive threshold policy for any operational use.

---

# 9. Limitations you must state

Do not wait to be asked. State these early and confidently.

1. **Retrospective only.** All metrics come from cross-validation and one forward holdout. There has been no prospective operational trial.
2. **Local snapshot.** The dashboard reads stored files. It does not pull live data.
3. **Sparse series.** Only 26.4% of cells are Y1-labelable. Short series weaken both features and evaluation.
4. **Currency regimes differ.** USD and nominal prices are never pooled, and nominal prices across currencies are not directly comparable.
5. **Coverage gaps.** Eight markets lack coordinates and cannot be mapped. Uncoloured districts are a coverage fact, not a low-risk finding.
6. **Weak rainfall association.** The lead-lag correlation is small and unstable. Rainfall is an indirect predictor, not a proven cause.
7. **Y2 is partly persistence.** Higher Y2 scores partly reflect the persistence of spatial premiums rather than independent forecasting skill.
8. **Uncertainty.** Probabilities carry sampling and model uncertainty. The Y1 bootstrap interval can include chance.
9. **Market stress is not household food insecurity.** The targets measure market prices and peer-relative premiums, not household access.
10. **Not an official warning.** Outputs are research evidence only.

---

# 10. Issues found and fixes applied

These were found during the full code review and corrected:

| Issue | Location | Fix |
|---|---|---|
| Y1 holdout ROC-AUC caption showed 0.6411, which is XGBoost's score, not the saved HistGBM's 0.5826 | `dashboard/pages/prediction_studio.py` | Replaced both AUC captions with live reads from `artifacts/metrics_all_tasks.csv` via a new `_holdout_auc()` helper. |
| Threshold sensitivity table loaded a non-existent file | `dashboard/pages/model_performance.py` | Changed the filename to the existing `reports/phase6b_threshold_model_sensitivity.csv`. |
| Research Evidence referenced four deleted files | `reports/` and `tests/` | Restored `phase2_target_definition.md`, `phase6b_diagnostics.md`, `phase10_qa_and_limitations.md` and `tests/run_checks.py` from git HEAD. |
| Home had an unused "Prediction month" selector that changed nothing | `dashboard/pages/home.py` | Removed the redundant selector; month filtering is handled by the Chart filters, which apply to the map, summary and trend. The second top card now shows the latest scored holdout month. |

### Remaining advisories

1. **Recapture screenshots.** The files in `screenshots/` and `outputs/figures/` show the older twelve-page layout. The live app is grouped into seven sections. If you use them in the dissertation, they will not match the demo.
2. **The calculator still uses a few hard-coded scenario assumptions** (district volatility, drift, peer count, log population). Present it as a scenario simulator, or use Advanced/Batch mode for fully data-derived outputs.
3. **`showErrorDetails = true`** is set in `.streamlit/config.toml`. During a live demo, an unexpected error would expose a stack trace. Consider setting it to `false`.
4. **The data dictionary is unavailable.** Home states this explicitly because no dictionary artefact exists. If asked, say the field-level catalogue on Data & Integration is the substitute.

---

# 11. Pre-defense checklist

### The day before

- [ ] Run the app locally: `streamlit run dashboard/app.py`.
- [ ] Click through all seven sections and every sub-tab once.
- [ ] Confirm the latest data month is what you expect.
- [ ] Confirm no page shows an avoidable "not available" state.
- [ ] Open Model Performance for T2 and confirm the headline numbers.
- [ ] Open Limitations and read the eleven items aloud once.
- [ ] Rehearse the six-minute script with a timer.

### Ten minutes before

- [ ] Start the app in a clean browser tab.
- [ ] Close anything that shows personal files or notifications.
- [ ] Set the browser zoom to a readable level.
- [ ] Have this guide open on a second screen or printed.
- [ ] Have the PDF and the repository folder ready for download questions.

### The three sentences to have ready

1. "The dashboard is the evidence layer of a reproducible pipeline; it reads stored artefacts and never fabricates values."
2. "The strongest result is the peer-relative Y2 target at 0.883 holdout ROC-AUC; the temporal Y1 target is much harder and is reported honestly as low-signal."
3. "This is a research prototype, not an operational early-warning system, and market price stress is not household food insecurity."

---

## Final summary

The project contributes a reproducible, leakage-aware pipeline for market food-price stress in Zimbabwe, and a dashboard that makes every stage inspectable. The strongest empirical result is the spatial peer-relative target: 0.883 forward-holdout ROC-AUC for USD Y2, with a market-clustered confidence interval that stays above chance. The weakest result is the temporal return-surge target, which is genuinely hard and is reported with its uncertainty rather than hidden.

The defense should be built on three pillars:

1. **Rigor** — expanding-window validation, an untouched forward holdout, baselines, calibration, bootstrap intervals and ablations.
2. **Transparency** — provenance on every page, download links for every artefact, and explicit unavailable states instead of invented numbers.
3. **Honesty** — a dedicated limitations page, a clear distinction between market stress and household food insecurity, and no claim of operational readiness.

Those three pillars are stronger than any single accuracy number.
