# Guideline Compliance Audit

**Document audited:** `ord_Chapter_1-5_final_document.docx`  
**Guideline:** `Level 2.2 Level 4.2 Data science and Informatics Project guidelines GL-IMS-002.pdf`  
**Audit basis:** visual inspection of the scanned guideline pages, document-heading comparison, and verification of the refreshed project artefacts and dashboard run.

## Overall result

The chapter document now contains Chapters 1–5, the required methodological subsections, refreshed statistical/model evidence, dashboard documentation, a district-level exploratory map, and the two previously absent labels for **1.10 Significance of the Project** and **2.9 Relevant Technologies or Tools**. The file is structurally suitable as a Chapters 1–5 working dissertation document.

Chapter 1 and Chapter 2 were additionally audited section by section. Every numbered Chapter 1–2 section block now contains at least one parenthetical in-text citation using sources already cited in the dissertation, including the food-price, climate, spatial-market, food-security and machine-learning literature.

The guideline also describes front matter and final-submission components that are outside a chapter-only file. These remain to be assembled in the final university submission because the project folder does not provide the student-specific title-page, declaration, approval, dedication, acknowledgement or signature details needed to create them accurately.

## Chapter compliance

| Guideline area | Status | Evidence in document |
|---|---|---|
| Chapter 1: Introduction, background, gap, problem, aim and objectives | Present | Sections 1.1–1.9 |
| Significance of the project | Added | Section 1.10 |
| Stakeholders, scope, assumptions and chapter summary | Present | Sections 1.7–1.11 |
| Chapter 2: literature-review introduction, questions, search strategy, extraction and quality assessment | Present | Sections 2.1–2.5 |
| Key concepts, synthesis, methods, tools and comparison with existing work | Present | Sections 2.6–2.10 |
| Relevant technologies or tools | Added | Section 2.9 |
| Literature-review summary | Present | Section 2.11 |
| Chapter 3: methodology and research design | Present | Sections 3.1–3.3 |
| Data collection, sources, variables, quality, cleaning, integration and feature engineering | Present | Sections 3.4.1–3.4.6 |
| Dimensionality reduction, sampling, privacy/anonymisation, documentation and versioning | Present | Sections 3.4.7–3.4.11 |
| Target construction, model selection, training, tuning, validation and statistical analysis | Present | Sections 3.4.12–3.9 |
| Software/tools, ethical considerations and chapter summary | Present | Sections 3.10–3.12 |
| Chapter 4: introduction, key findings and descriptive analysis | Present | Sections 4.1–4.3, including 4.3.1–4.3.3 |
| Model performance and evaluation | Present | Section 4.4, including ROC, PR, confusion-matrix and calibration subsections |
| Statistical analysis and interpretation | Present under detailed headings | Sections 4.5–4.6 and 4.10 |
| Findings, feature importance, outliers, robustness and sensitivity | Present | Sections 4.7–4.9 |
| Discussion and chapter summary | Present | Sections 4.10–4.11 |
| Chapter 5: findings, objective achievement and implications | Present | Sections 5.1–5.4 |
| Theory, practice and education implications | Standardised | Sections 5.4.1–5.4.3 |
| Limitations, recommendations, future research, conclusion and summary | Present under expanded structure | Sections 5.5–5.8 |

## Evidence and visualisation checks

The following refreshed assets were generated from the current project code and artefacts:

- Matplotlib model-metric comparison: `figures/fig4.4_model_metrics_comparison.png`
- Seaborn statistical-effect visualisation: `figures/fig4.5_statistical_effect_sizes.png`
- Plotly interactive model comparison: `outputs/interactive/interactive_holdout_model_metrics.html`
- Plotly interactive district comparison: `outputs/interactive/interactive_district_holdout_probabilities.html`
- GeoPandas district map: `figures/fig4.8_district_holdout_probability_map.png`
- Refreshed model, statistical, geographic, home and limitations dashboard captures in `screenshots/`
- Refreshed statistical results: `outputs/metrics/parametric_vs_nonparametric_stats.csv`

The dashboard was launched successfully with Streamlit and the existing capture workflow completed all twelve requested page captures. The Statistical Analysis capture route itself did not render reliably when selected programmatically, so the dissertation uses the verified static statistical chart and the project-generated statistical-results CSV rather than embedding a misleading blank dashboard image.

## Final-submission items still required outside this chapter file

The scanned guideline also refers to front matter and submission-control items that are not present in the chapter-only document:

1. Title page with student, programme, institution, supervisor and submission details.
2. Declaration/authorship statement and approval/signature page, where required.
3. Dedication and acknowledgements, if required by the institution.
4. Abstract and keywords.
5. Table of contents, list of figures, list of tables and abbreviations/acronyms list.
6. Final reference-list formatting and any institution-specific declaration of AI/tool use.
7. Final pagination, header/footer, margin and submission-format checks.

These should be added only after the student-specific details and institutional formatting rules are confirmed; they should not be fabricated from the project evidence.
