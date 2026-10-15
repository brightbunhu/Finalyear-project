# Supervisor Feedback — Requirement Traceability Matrix

Prepared after receiving the supervisor's comments. Each requirement is mapped to
its **status**, the **evidence** produced by this rebuild, and the **action** taken
(or pending). Statuses: DONE (evidence exists now) · PARTIAL · PENDING (needs an
external input) · NEW (added in this revision).

## Meta / cross-cutting

| # | Supervisor requirement | Status | Evidence / action |
|---|---|---|---|
| M1 | "A functioning pipeline is not a reliable model"; make weak forward-holdout performance a central finding | DONE | `reports/phase5_results.md`; Chapter 4/5 revisions foreground the holdout deterioration. |
| M2 | Do not combine different targets into one ranking; use same target/observations/metrics per claim | DONE | Separate tables per task T1–T4 in `artifacts/metrics_all_tasks.csv`; `phase6b_*` outputs. |
| M3 | Investigate *why* holdout deteriorates (distribution shift, currency, target instability, overfitting, class composition, implementation error) | DONE (NEW) | `src/robustness.py` → OOF-by-year, OOF-by-currency, calibration, recalibration, recent-window retraining. |
| M4 | Report uncertainty intervals; treat repeated market/district observations | DONE (NEW) | Bootstrap CIs (row- and market-clustered) in `reports/phase6b_bootstrap_ci.csv`. |
| M5 | Do not fabricate: every number must trace to an artefact | DONE | `tests/run_checks.py` (20/20); `reports/phase1_claims_to_verify.md`. |

## Chapter 1

| # | Requirement | Status | Action |
|---|---|---|---|
| C1.1 | Reference specific empirical evidence on Zimbabwe food prices, rainfall shocks, inflation, geographic differences | DONE | Revised Ch.1.2.1 now cites Phillips et al. (1998), Kramarenko et al. (2010), Gilbert et al. (2017), Burke & Myers (2014), Funk et al. (2015), Moyo (2024) and others from the author-supplied list. |
| C1.2 | Establish the gap by systematic comparison with WFP/FEWS NET etc.; avoid equating "no identical system" with "no comparable capability" | PARTIAL | Revised Ch.1.2.2 rewritten as a capability comparison table (what WFP/FEWS NET/ZimVAC already do vs the missing machine-readable district–commodity probability). |
| C1.3 | Make objectives measurable with outputs + acceptance criteria | DONE (NEW) | Revised Ch.1.5 objectives now carry concrete outputs and pass/fail criteria drawn from real artefacts. |
| C1.4 | Define food price stress explicitly: unit, horizon, and distinction from inflation / household insecurity | DONE | Revised Ch.1 adds a definition box: unit = market×commodity×currency×month; horizon = 1 month; stress ≠ inflation ≠ household food insecurity. |
| C1.5 | Identify primary users precisely; temporal coverage; interpretation when performance is weak; assumptions tied to validation | DONE | Revised Ch.1.7/1.8/1.9 specify primary user, coverage 2010-01→2026-05, weak-performance interpretation, and validation-linked assumptions. |

## Chapter 2

| # | Requirement | Status | Action |
|---|---|---|---|
| C2.1 | Link each research question to a measurable objective, procedure and output | DONE (NEW) | `reports/revision/chapter2_revised.md` §2.9 (and earlier protocol §2.2) maps RQ1–RQ7 to objective/procedure/output. |
| C2.2 | Report search dates, database-specific expressions, publication period | DONE | Search date 2026-10-15; 6 boolean streams across OpenAlex, Semantic Scholar, PubMed with expressions in Ch.2.10; `prisma_search_log.csv`. |
| C2.3 | PRISMA-style selection record (identified/duplicates/screened/full-text/retained) | DONE | `scripts/prisma_ingest.py` from downloaded exports → `reports/revision/prisma_flow.md`: 9,228 identified → 2,629 duplicates → 6,599 screened → 4,196 pass → 3,243 candidate pool → 22 included (+9 grey). OpenAlex type/abstract recovered via API by DOI (`scripts/openalex_enrich.py`). Real counts from retrieved files. |
| C2.4 | Verify ≥20 refereed journal articles, separated from reports | DONE | `references.md`: 21 refereed journal articles + 1 refereed conference paper (22), separated from 9 grey reports and 1 chapter/1 guide. |
| C2.5 | Transparent quality-assessment procedure | DONE | Quality-grading procedure applied per source (Ch.2.10; `references.md` §F 5Cs). |
| C2.6 | Apply 5Cs (Cite, Compare, Contrast, Critique, Connect) | DONE | `references.md` §F provides the 5Cs for all 33 sources; Ch.2.11–2.12 synthesise. |
| C2.7 | Justify XGBoost as a candidate, not assume superiority | DONE | Real results show XGBoost is **not** best on Y2 holdout; stated explicitly (Ch.2.7, Ch.4). |

## Chapter 3

| # | Requirement | Status | Action |
|---|---|---|---|
| C3.1 | Complete reproducible workflow (inputs→transforms→target→partitions→training→eval→scoring) | DONE | `src/` scripts + `reports/revision/chapter3_revised.md` workflow diagram. |
| C3.2 | Auditable data prep: exact period, versions, initial counts, exclusions, missing-value treatment, match rates, final sizes | DONE | `data_processed/panel_build_log.txt`, `reports/phase3_rainfall_summary.json`, revised Ch.3.4. |
| C3.3 | Handle currency/unit/commodity-definition changes and irregular reporting | DONE | Revised Ch.3.4: regime split, unit kept, median aggregation, currency-scoped panels. |
| C3.4 | Reconcile the "3,571 / 10,459" panels | DONE | Those numbers do not exist in the data; revised Ch.3.4 gives the real derivation table (20,530 → 5,429 / 12,635 labelable). |
| C3.5 | Exact target math, thresholds, reference populations, temporal calc; justify thresholds | DONE | `config/targets.yml` + revised Ch.3.4.12 with full equations and prevalence-vs-threshold table. |
| C3.6 | Prove standardisation/targets use no future info; separate label-from-future vs predictor leakage | DONE | Revised Ch.3.4.12: labels use t+1 by design; trailing-only standardisation; leakage checks in pipeline + `tests/run_checks.py`. |
| C3.7 | Exact calendar boundaries of every partition | DONE (NEW) | `artifacts/folds_*.json` + summary table in revised Ch.3.8. |
| C3.8 | Specify pipelines, hyperparameter spaces, objectives, trials, selection rules | DONE | `src/tune_optuna.py` (TPE, seed 42, **40 trials/task, 160 total**); `reports/revision/chapter3_revised.md` §3.5–3.7 (search spaces + selected configs + `artifacts/optuna_*`). |
| C3.9 | Prevent temporal leakage in rolling/peer/standardisation/rainfall-baseline features | DONE | Trailing windows, expanding peer stats within month, 1981–2015 climatology; revised Ch.3.4.6/3.8. |
| C3.10 | Demonstrate whether a forecast-horizon gap is needed at train/validation boundary | DONE (NEW) | Horizon = 1 month; holdout begins the month after the last training month; documented in revised Ch.3.8. |

## Chapter 4

| # | Requirement | Status | Action |
|---|---|---|---|
| C4.1 | Replace 3,571/10,459, 17%/12.43%, 57.3% USD with real values | DONE | Real values in revised Ch.4 (5,429/12,635; ~15%/16%; USD ≈27%). |
| C4.2 | Do not rank mixed-target models; repeat on common target + holdout; report uncertainty; examine by time and commodity | DONE (NEW) | `phase6b_oof_by_year.csv`, `phase6b_oof_by_commodity.csv`, `phase6b_bootstrap_ci.csv`. |
| C4.3 | Complete confusion matrices + precision/recall/specificity/F1 on identified eval sets; thresholds not tuned on holdout | DONE | `artifacts/metrics_*.csv` (tn/fp/fn/tp, P/R/spec/F1; threshold = F1-optimal from pooled CV validation, applied unchanged to holdout); surfaced in revised Ch.4.4.3. |
| C4.4 | Do not claim superior calibration from a different-target Brier score | DONE | Brier reported per task only; recalibration results in `phase6b_*`. |
| C4.5 | Inferential stats: n, exact method, uncertainty interval, repeated-observation treatment | DONE | Revised Ch.4.5: Pearson+Spearman, n=12,520, 95% CI via Fisher z, block caveat. |
| C4.6 | Connect Optuna hyperparameters to actual validation objective | DONE | `src/tune_optuna.py` objective = mean validation-block ROC-AUC (training-only folds); revised Ch.4.6 states objective + selection rule; parameters from the real run (`artifacts/optuna_best_*.json`). |
| C4.7 | Interpret permutation importance cautiously; test stability across folds | DONE (NEW) | `phase6b_importance_stability.csv` (per-fold importance for XGB). |
| C4.8 | Quantify outliers; distinguish real shocks from errors; alternative handling effects | DONE (NEW) | `phase6b_outlier_sensitivity.csv` (winsorisation). |
| C4.9 | Extend sensitivity: thresholds, windows, currency samples, commodity groups, feature exclusions; recalibration/retraining | DONE (NEW) | `phase6b_threshold_model_sensitivity.csv`, `phase6b_feature_exclusion.csv`, recalibration/recent-window in summary. |
| C4.10 | Label district bands as exploratory, model-generated | DONE | Revised Ch.4.2.5 relabels bands as exploratory. |

## Chapter 5

| # | Requirement | Status | Action |
|---|---|---|---|
| C5.1 | Make poor holdout central; separate "developed" from "validated" | DONE | Revised Ch.5.2/5.3. |
| C5.2 | Reassess objectives; 3-tier table (implementation / validation / operational readiness) | DONE (NEW) | Revised Ch.5.3 tiered table. |
| C5.3 | Avoid overstating theory; Education 5.0: name the innovation, applications, stakeholder evidence | DONE | Revised Ch.5.4 names the innovation (reproducible, leakage-controlled pipeline), states the project includes no field deployment/end-user engagement, and presents community/industry application as proposed future work (§5.6). Completed work is distinguished from potential contributions. |
| C5.4 | Connect each limitation to validity of conclusions / operational suitability | DONE | Revised Ch.5.5 rewritten with an effect-on-validity column. |
| C5.5 | Prioritise recommendations (investigate holdout & targets first) | DONE | Revised Ch.5.6 reordered. |
| C5.6 | Defensible contribution statement (workflow, not reliable early-warning model) | DONE | Revised Ch.5.8. |

## Human screening confirmation

1. **Borderline screening decisions** — the PRISMA flow uses reproducible automated
   rules; the region-relevant borderline worklist (`reports/revision/prisma_borderline.csv`,
   94 records: 38 includes to confirm, 56 possible false negatives) was reviewed and
   confirmed by the author on 2026-10-15 (G1 kept, G2 excluded).
