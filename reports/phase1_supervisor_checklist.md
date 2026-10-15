# Phase 1 — Supervisor-Comments Checklist

> **Blocker:** **No supervisor feedback document was supplied.** The working
> directory contains only `Chapter 1-5.docx` (dissertation) and the `raw/` data.
> The DOCX has no tracked changes, comments, footnotes, or endnotes.
> This checklist therefore records what the dissertation itself *claims* the
> supervisor required, plus the standard Level 4.2 / institutional expectations
> that are checkable. **It must be replaced with the real feedback before Phase 9.**
> Do not treat any row below as verified supervisor instruction.

## A. Requirements implied by the dissertation text

| ID | Requirement (as stated in the dissertation) | Where | Status |
|----|---------------------------------------------|-------|--------|
| R1 | Minimum **20 refereed journal articles**, kept separate from institutional/technical documents. | §2 preamble | **Not met** — bibliography is empty; citations are inline only. |
| R2 | Address the data-science gap: consistent currency handling, correct market→district assignment, no future leakage, class imbalance, interpretability. | §1.2.2 | Partially addressed in prose; **no implementing code exists**. |
| R3 | Time-ordered validation (no random split) plus a forward holdout. | §3.6, §3.8 | Described only; **no code, no split records**. |
| R4 | Compare against simple baselines (majority, persistence). | §3.5 | Described only; **no results artefact**. |
| R5 | Define food price stress, and separate standardised-return vs peer-relative (SPI) tasks. | §1.4, §4.1 | Definition is vague; **must be made precise in Phase 2**. |
| R6 | Report multiple metrics (ROC-AUC, PR-AUC, precision, recall, specificity, F1, balanced accuracy, Brier, calibration). | §3.6 | Described only; **no metrics exist**. |
| R7 | Reproducibility: data dictionary, versioning, processing log. | §3.4.10–3.4.11 | Claimed; **no artefacts exist**. |
| R8 | Streamlit dashboard with the 8 sections, driven by real outputs. | §2.9, §4.2.4 | Claimed; **dashboard does not exist**. |
| R9 | Statistical/lead-lag analysis with stated limitations. | §3.9, §4.5 | Numbers in Ch4 are unverified. |
| R10 | Correctness of claims: distinguish implemented / tested / validated. | (rule 9) | Ch4–5 currently overstate status. |

## B. Standard institutional checks (Level 4.2 Data Science & Informatics)

| ID | Check | Status |
|----|-------|--------|
| C1 | Measurable, numbered objectives | Present (5 objectives). |
| C2 | Every objective has evidence of achievement or explicit non-achievement | **Currently no reproducible evidence.** |
| C3 | Literature review method documented and ≥20 refereed articles | **Fails (empty bibliography).** |
| C4 | Methodology matches research design and is reproducible | Described; **unimplemented**. |
| C5 | Results traceable to outputs | **Fails (fabricated/unverifiable numbers).** |
| C6 | Ethics and data-privacy statement | Present (§3.11). |
| C7 | Timeline/feasibility | Not found in the supplied document. |

## C. How this project will resolve them

| Requirement | Corrective action (this rebuild) | Phase |
|-------------|----------------------------------|-------|
| R1 | Build a verified, cited bibliography (≥20 peer-reviewed) with a documented selection process; never invent counts. | 9 |
| R2, R5 | Precise target definition, currency strategy, district join, leakage controls. | 2–3 |
| R3, R4, R6, R9 | Implement chronological CV + holdout, baselines, full metric set, lead-lag. | 5–6 |
| R7 | Data dictionary, hashed versions, processing log, seeds. | 3, 7 |
| R8 | Streamlit dashboard wired to real outputs only. | 8 |
| R10, C2, C5 | Rewrite Ch3–5 to match generated artefacts; add traceability matrix. | 9–10 |

## D. Immediate asks for you

1. Send the **actual supervisor feedback** (file or transcript).
2. Confirm the **expected sample size / target definition** expectations, if the
   supervisor specified any.
3. Confirm whether a **non-food** category was intended to be included or excluded.
