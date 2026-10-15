# ML-Based Food Price Stress Prediction in Zimbabwe — research pipeline

A clean, reproducible rebuild of the food-price-stress study on which the
dissertation chapters were based. **Every reported number is produced by the
scripts here.** Where the dissertation contained results that could not be
reproduced (or that were fabricated), the real numbers are given and the
discrepancy is documented.

## Headline (honest) results

- Two targets, modelled **separately** for each price base (never pooled):
  - **Y1** standardised-return stress: next-month log return ≥ +1.0 SD (trailing 12m).
  - **Y2** peer-relative stress: next price ≥ 1.20 × peer median (same commodity, currency, month).
- Base rates: Y1 ≈ 15%, Y2 ≈ 16%.
- **Y1 is hard**: forward-holdout ROC-AUC ≈ 0.54–0.67.
- **Y2 is moderate-to-good**: holdout ROC-AUC ≈ 0.81–0.90, but partly reflects persistence.
- **XGBoost does not dominate** — histogram gradient boosting (Optuna-tuned, 40 trials/task)
  wins the USD Y2 holdout (0.886 vs 0.842) and is tied on nominal Y2.
- **Rainfall signal is weak**: lead-lag r ≈ −0.11/−0.12, strongest at a **1-month** lead
  (the dissertation claimed −0.22 at 2 months).
- **Not an early-warning system**: no prospective validation; retrospective metrics only.

## Reproduce

```powershell
python -m pip install -r requirements.txt

python src\build_rainfall.py        # CHIRPS -> district-month rainfall + climatology
python src\build_dataset.py         # clean/aggregate/crosswalk -> both panels
python src\eda.py                   # Phase 4 figures + tables
python src\tune_optuna.py           # tune hist GBM (40 trials/task) -> artifacts\optuna_*
python src\train.py                 # Phase 5 model comparison (uses tuned params) -> artifacts\
python src\analysis.py              # Phase 6 lead-lag, sensitivity, importance, figures
python src\robustness.py            # Phase 6b robustness/bootstraps -> reports\phase6b_*.csv
python src\fit_final_model.py       # persist dashboard models -> models\
python tests\run_checks.py          # Phase 10 sanity/QA checks

python scripts\openalex_enrich.py   # OpenAlex type/abstract by DOI (API; optional key)
python scripts\prisma_ingest.py     # literature PRISMA -> reports\revision\prisma_flow.md

streamlit run dashboard\app.py      # Phase 8 dashboard
```

Config (targets, thresholds, CV) is centralised in `config/targets.yml`; seed = 42.
The literature PRISMA reads the exports in `data/literature/raw/`; `openalex_enrich.py`
is optional and needs a free OpenAlex API key (`scripts/.openalex_key`).

## Layout

| Path | Contents |
|------|----------|
| `raw/` | Read-only source data (WFP prices & markets, CHIRPS `yr.nc`, geoBoundaries, HAPI). |
| `config/targets.yml` | Single source of truth for targets, thresholds, validation. |
| `src/` | Pipeline scripts (build → eda → train → analysis → fit model). |
| `data/literature/` | Literature search: raw exports, dedup library, screening sheet, logs. |
| `scripts/phase1_*.py` | Phase 1 profiling/inventory scripts. |
| `data_processed/` | Panels, rainfall tables, crosswalk, build log. |
| `artifacts/` | Metrics, predictions, fold records, importance, run metadata. |
| `models/` | Persisted models + metadata for the dashboard. |
| `figures/` | Phase 4 and Phase 7 figures. |
| `reports/` | Phase reports (inventory, quality, targets, results, QA). |
| `tests/run_checks.py` | Dependency-free QA checks. |
| `dashboard/app.py` | Streamlit research dashboard. |

## Data-quality flags (disclosed, not hidden)

- 8 markets lack coordinates; those rows are excluded from the geographic view.
- `usdprice` contains implausibly small values (min ≈ 1.5e-5).
- `priceflag=aggregate` rows are retained (78% of records) — documented decision.
- Median series length is 4 months; only 37% of cells are next-month labelable.
- 1 of 91 districts has no CHIRPS pixel.
- `raw/DataDetails.xls` is unrelated to this study (World Bank Enterprise Surveys).

## Open blockers

- **No supervisor feedback document** was supplied → the chapter-by-chapter
  traceability matrix (Phase 9) cannot be finalised.
- **No literature sources** were supplied → the ≥20 refereed-article requirement
  cannot be met without fabricating citations, which is out of scope.

## Verified sources

WFP VAM food prices; CHIRPS v3.0 (`yr.nc`); geoBoundaries ADM1/ADM2 (CC BY 3.0 IGO);
HDX HAPI (admin-1 rainfall only, unusable at district level).
