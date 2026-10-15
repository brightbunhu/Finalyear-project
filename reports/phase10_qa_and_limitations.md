# Phase 10 — QA, traceability and remaining work

## QA checks (`tests/run_checks.py`) — 20/20 pass

- Both panels exist; unit key `market×commodity×currency×month` is unique.
- No target/next-month columns leak into the feature set.
- `labelable_y1 ⇒ z_next` present; `labelable_y2 ⇒ next_spi` present.
- Y1 prevalence 14.8% / 15.0%; Y2 16.3% / 16.1% (both bases) — within expected band.
- Metrics file covers 4 tasks × 5 models × 2 splits; ROC-AUC ∈ [0,1];
  majority baselines ≈ 0.5 (verified against the pooled-fold artefact).
- Dashboard models and metadata present.

## Dashboard (`dashboard/app.py`) — 10/10 pages render

Verified headlessly with `streamlit.testing.v1.AppTest`: Overview, Data coverage &
quality, Price trends, Rainfall, Market & commodity explorer, Model performance,
Historical holdout predictions, Prediction, Geographic view, Limitations.

Every page shows the research-prototype disclaimer; the **Prediction** screen labels its
output as a single-point, non-validated scenario.

## Traceability of dissertation claims

See `reports/phase1_claims_to_verify.md` and `reports/phase5_results.md`.
0 of 22 original claims verified; several are **factually false** (referenced files
that do not exist: `food_prices_zwe_core.parquet`, `adm2_monthly_rainfall.parquet`,
`market_admin_crosswalk.csv` as originally described, `live_prediction.py`,
`map_stress.py`). The original fabricated result tables (Optuna config, confusion
matrices, per-commodity AUCs, risk bands, districts) had no supporting artefact and have
been **removed or replaced** with real outputs: the Optuna configuration is now produced
by `src/tune_optuna.py` (40 trials/task; `artifacts/optuna_*`), and the confusion
matrices, per-commodity AUCs and thresholds are in `artifacts/` and `reports/phase6b_*`.

## Phase 6b robustness diagnostics — complete

`src/robustness.py` produced 9 files `reports/phase6b_*.csv`. Highlights: bootstrap CIs
(Y1 market-clustered CI reaches chance); OOF Y1 AUC **below 0.5** in 2020/2022/2023
(currency-transition years); Y2 stable and higher; rainfall importance unstable across
folds; recalibration/recent-window retraining do not improve the holdout; winsorising
outliers negligible. Full write-up: `reports/phase6b_diagnostics.md`.

## Phase 9 — dissertation revision (in progress)

Supervisor comments were supplied and are tracked in
`reports/supervisor_traceability.md`. Revisions written to `reports/revision/`:

- `chapter1_revised.md` — definition box, measurable objectives + acceptance criteria,
  capability-comparison gap, users, scope, validation-linked assumptions.
- `chapter2_revised.md` — full literature review using the 33 author-supplied sources
  (21 refereed articles + 1 refereed conference paper), RQ↔objective/procedure/output
  map, comparison gap, quality grading, 5Cs. Reference list + per-source 5Cs:
  `references.md`.
- `chapter3_revised.md` — full audit trail, 3,571/10,459 reconciliation, exact target
  maths + label-vs-predictor leakage, partition boundaries, hyperparameter spaces,
  horizon gap.
- `chapter4_revised.md` — real tables, per-task confusion matrices at CV-derived
  threshold, bootstrap CIs, inferential stats, importance stability, robustness.
- `chapter5_revised.md` — holdout failure central, three-tier objective table, softened
  theory, limitations→validity, prioritised recommendations.

## Compiled deliverable

`reports/revision/Chapters_1-5_revised.docx` — Chapters 1–5 plus References compiled from
the markdown sources via `scripts/compile_revision.py`.

## Systematic search / PRISMA (Ch2 §2.10) — complete

`scripts/prisma_ingest.py` ingests the author's downloaded exports
(`data/literature/raw/`: OpenAlex 6 streams, Semantic Scholar 6, PubMed 2), merges and
de-duplicates them, applies documented title/abstract screening rules, and writes
`reports/revision/prisma_flow.md`:
**9,228 identified** (OpenAlex 6,604 + Semantic Scholar 2,616 + PubMed 8) → 2,629
duplicates → 6,599 screened → 4,196 passed title/abstract → 3,243 refereed candidate pool
→ **22 refereed included** (+9 grey). Per-record flags: `prisma_records.csv`; per-query
log: `prisma_search_log.csv`; merged library: `data/literature/dedup/library.csv`;
screening sheet: `data/literature/screen/screening_sheet.csv`. OpenAlex `type`/`abstract`
metadata was recovered from the OpenAlex API by DOI via `scripts/openalex_enrich.py`
(`data/literature/raw/openalex_enriched.csv`). (This supersedes the earlier
single-database OpenAlex-API run.)

## Remaining work / blockers

1. 1 of 91 districts has no CHIRPS pixels — identify and note.

The PRISMA borderline screening set (`reports/revision/prisma_borderline.csv`, 94
records) was reviewed and confirmed by the author on 2026-10-15.

## Recommended next steps

- Supply literature references to complete Ch2 to publication standard.
- Optionally extend Phase 6 with additional subgroup analyses (frameworks in place).
- Decide whether `priceflag=aggregate` rows should be excluded (currently retained).
