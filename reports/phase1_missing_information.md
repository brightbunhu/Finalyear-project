# Phase 1 — Missing Information and Decisions Needed

Things that must be obtained or decided before the project can proceed cleanly.
None of these will be invented.

## A. Documents not supplied (blocking)

| # | Missing item | Why it matters | Can I proceed without it? |
|---|--------------|----------------|---------------------------|
| M1 | **Supervisor feedback / comments** | Drives revisions and the final traceability matrix; requirement R-mapping in Phase 9. | Partially — I can proceed with the empirical rebuild, but Phase 9 cannot be finalised. |
| M2 | **Literature sources / reading list** | The bibliography is empty; the ≥20-refereed-article requirement must be met without inventing citations. | No — need the sources or permission to source them. |
| M3 | **WFP data licence / codebook** (incl. meaning of `priceflag` and `usdprice` basis) | Affects data-quality handling and reproducibility. | Yes, with an explicit documented assumption flagged as unverified. |
| M4 | **Institutional report template / marking rubric** | Affects Chapter structure and required sections. | Yes, for now. |
| M5 | **Original project proposal / approved scope** | To check the 5 objectives and target against what was approved. | Yes, for now. |

## B. Methodological decisions I need from you (Phase 2 inputs)

| # | Decision | Options | My recommendation |
|---|----------|---------|-------------------|
| D1 | **Currency handling** | (a) pool USD+ZWL; (b) analyse each currency separately; (c) use `usdprice` to build one comparable series; (d) both (b) and (c) | **(b) and (c) as two parallel tasks**; never pool nominal prices. |
| D2 | **Price basis for returns** | nominal `price` within currency, or `usdprice` | Compute returns on `usdprice` (currency-comparable) **and** on within-currency nominal as a robustness check. |
| D3 | **Unit of analysis** | market×commodity×currency×month (confirmed feasible) | Keep as is. |
| D4 | **Prediction horizon** | 1 month (as claimed) | 1 month, given series shortness. |
| D5 | **Stress threshold** | e.g. standardised log-return ≥ +1σ, ≥ +1.5σ, or top decile; peer-relative SPI ≥ *k* | Test thresholds in Phase 6; pick a primary threshold on **training data only**. |
| D6 | **Standardisation reference** | trailing window vs training-period stats vs full-sample | **Trailing/training only** (avoid leakage). |
| D7 | **Non-food rows** | include (fuel/soap) or exclude | **Exclude** from food-stress targets; optionally keep fuel as a *predictor*. |
| D8 | **`priceflag=aggregate` rows** | keep / drop / flag | Keep but **flag** pending M3; run sensitivity. |
| D9 | **Minimum series length** | e.g. require ≥6 consecutive months to enter the supervised panel | Require ≥6; report how few series remain and be transparent. |
| D10 | **District rainfall** | zonal stats from `yr.nc` | Use `yr.nc`; report the matching method. |

## C. Technical blockers / environment notes

| # | Item | Status |
|---|------|--------|
| T1 | Python stack | OK: pandas 3.0.3, numpy 2.4.6, scikit-learn 1.9.1, xgboost 3.4.1, xarray 2026.7.0, netCDF4, geopandas 1.1.4, streamlit 1.58.0, optuna?, matplotlib 3.11.2. |
| T2 | Optuna availability | **To confirm** (needed only if we keep Optuna tuning). |
| T3 | No git repository | Directory is not a repo; will initialise only if you ask. |
| T4 | `yr.nc` is 8.94 GB | Zonal statistics must be streamed/chunked; extraction for ZW only. |

## D. Open data-quality questions (from DQ report)

- E5 meaning of `priceflag=aggregate`.
- E6 basis of `usdprice` conversion.
- E7 rows with `usdprice` ≈ 0.000015.
- E8 exact WFP licence.
- E9 CHIRPS metadata inconsistency ("convective precipitation rate").
