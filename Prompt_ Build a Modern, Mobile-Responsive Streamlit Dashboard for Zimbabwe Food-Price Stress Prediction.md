# Prompt: Build a Modern, Mobile-Responsive Streamlit Dashboard for Zimbabwe Food-Price Stress Prediction

## Role

You are a senior Python, Streamlit, data-visualisation and machine-learning application engineer. You are working inside my existing research project repository. Your task is to redesign and improve the existing Streamlit dashboard into a modern, professional, mobile-responsive research and decision-support dashboard.

Do not create a fictional demo. Use the real datasets, real model files, real artefacts and real metadata already stored in the project. The raw source files may be large and may not be visible in the current uploaded archive, but they exist in the complete local project environment. Do not remove, replace or simplify the existing research pipeline.

The dashboard must help users find information quickly, understand the prediction results, inspect the complete data-integration process and demonstrate that the research objectives have been implemented in the actual system.

---

## Project context

The project concerns machine-learning prediction of food-price stress in Zimbabwe using food-price, market, rainfall, geographic and contextual data.

The project contains or may contain the following folders:

```text
raw/
config/
data_processed/
artifacts/
models/
figures/
reports/
src/
scripts/
tests/
dashboard/
```

The existing dashboard is located at:

```text
dashboard/app.py
```

The dashboard must continue to run with:

```bash
streamlit run dashboard/app.py
```

Use the project’s existing `requirements.txt` where possible. Add dependencies only when they provide clear value and are compatible with Streamlit.

---

## Academic and technical integrity rules

1. Use real data from the project files.
2. Use the persisted models from `models/` for predictions.
3. Do not invent raw data, coordinates, prediction results, model metrics or live API responses.
4. Do not show placeholder values when the real artefact is missing.
5. If a raw file is not available, show a clear status such as `Not available in this environment`.
6. If a map cannot be generated because coordinates are missing, explain why rather than fabricating coordinates.
7. Clearly distinguish:
   - Latest available local data
   - User-uploaded current-month data
   - Historical holdout predictions
   - Model evaluation metrics
   - Prospective live forecasts
8. Do not call the system a validated operational early-warning system unless prospective validation exists.
9. Keep the existing disclaimer visible throughout the application:

> Research prototype. Predictions are model outputs from the stored research models. They are not prospectively validated official early-warning forecasts or official food-security classifications.

10. Do not alter model definitions, target thresholds, training boundaries or reported results merely to make the interface look better.
11. Do not change the research conclusions.
12. Preserve British English in all user-facing text.
13. Use accessible labels, readable contrast and keyboard-friendly controls.
14. Add explanatory tooltips and help text for technical terms.

---

# 1. Product goal

Create a modern Streamlit dashboard that acts as:

1. A fast decision-support interface
2. A research-results demonstration system
3. A data-integration evidence viewer
4. A model-scoring interface
5. A geographic exploration tool
6. A reproducibility and transparency layer

The dashboard should make it possible for a supervisor, examiner or stakeholder to ask:

- What data were used?
- How many rows and columns are available?
- Which datasets were combined?
- What is the latest available month?
- What month is being predicted?
- What is the probability of Y1 or Y2 stress?
- Which districts are most affected?
- What does the map show?
- How were the models evaluated?
- What are the limitations?

The answers should be visible through the UI without opening Python files.

---

# 2. Overall visual direction

Use a visual style called **Evidence-led Command Centre**.

The interface should feel:

- Modern
- Professional
- Calm
- Data-rich but not crowded
- Suitable for academic demonstration
- Suitable for fast scanning
- Transparent about uncertainty
- Appropriate for a Zimbabwe food-security and market-monitoring context

Avoid:

- Generic dashboard templates
- Excessive decorative gradients
- Neon colours
- Large empty spaces
- Tiny unreadable charts
- Too many tables shown at once
- Unexplained machine-learning jargon
- Fake live-data indicators
- Red/green-only communication that fails for colour-blind users

Use a strong left navigation rail on desktop and a compact top navigation or collapsible menu on mobile.

---

# 3. Brand and visual identity

## 3.1 Colour palette

Use CSS variables or a central theme object so all colours are controlled consistently.

### Core colours

```css
--navy-950: #07111F;
--navy-900: #0B1220;
--navy-800: #12213C;
--navy-700: #1A3157;
--blue-700: #1D4ED8;
--blue-600: #2563EB;
--blue-500: #3B82F6;
--blue-100: #DBEAFE;
--blue-50: #EFF6FF;
--teal-700: #0F766E;
--teal-600: #0F9F91;
--teal-100: #CCFBF1;
--teal-50: #F0FDFA;
--green-700: #15803D;
--green-600: #16A34A;
--green-100: #DCFCE7;
--amber-700: #B45309;
--amber-600: #D97706;
--amber-100: #FEF3C7;
--red-700: #B91C1C;
--red-600: #DC2626;
--red-100: #FEE2E2;
--purple-700: #6D28D9;
--purple-100: #EDE9FE;
--slate-950: #0F172A;
--slate-800: #1E293B;
--slate-700: #334155;
--slate-600: #475569;
--slate-500: #64748B;
--slate-400: #94A3B8;
--slate-300: #CBD5E1;
--slate-200: #E2E8F0;
--slate-100: #F1F5F9;
--slate-50: #F8FAFC;
--white: #FFFFFF;
```

### Meaning of colours

| Meaning | Colour | Use |
|---|---|---|
| Primary structure | Navy | Sidebar, top header, headings |
| Primary action | Blue | Buttons, active navigation, links, selected controls |
| Data integration | Teal | Dataset pipeline stages, sync state, successful data loading |
| Low risk | Green | Low probability, healthy data status, completed stage |
| Watch | Amber | Medium probability, missing optional field, caution |
| High stress | Red | High probability, warning, critical limitation |
| Methodological evidence | Purple | Model metadata, validation and research evidence |
| Neutral information | Slate | Secondary text, borders, table labels |

Never communicate risk using colour alone. Always display a text label such as `Low`, `Watch`, `High` or `Very high`.

## 3.2 Backgrounds

Desktop application background:

```css
background: #F8FAFC;
```

Optional subtle background treatment:

```css
background:
  radial-gradient(900px 420px at 100% -10%, #EAF1FF 0%, transparent 62%),
  radial-gradient(760px 380px at -10% 0%, #E9FAF6 0%, transparent 58%),
  #F8FAFC;
```

Cards must remain white with clear borders so that data remains readable.

## 3.3 Typography

Use a modern sans-serif font stack:

```css
font-family: Inter, ui-sans-serif, system-ui, -apple-system,
  BlinkMacSystemFont, "Segoe UI", sans-serif;
```

If external font loading is used, provide a system-font fallback so the dashboard still works offline.

### Type scale

| Element | Font size | Weight | Colour |
|---|---:|---:|---|
| Main page title | 28–34px | 800 | White on hero / Navy on light background |
| Section heading | 18–22px | 700 | Navy-950 |
| Card title | 14–16px | 700 | Slate-800 |
| Metric value | 25–34px | 800 | Navy-950 |
| Metric label | 11–13px | 600 | Slate-500 |
| Body text | 14–16px | 400 | Slate-700 |
| Caption | 11–13px | 400 | Slate-500 |
| Table text | 12–14px | 500 | Slate-700 |
| Badge text | 10–12px | 700 | Context-specific |

Use clear line height and avoid long dense paragraphs in the UI.

---

# 4. Layout system

## 4.1 Desktop layout

Use a two-zone layout:

```text
┌─────────────────────────────────────────────────────┐
│ Persistent sidebar navigation                       │
├───────────────┬─────────────────────────────────────┤
│               │ Header / page context                │
│ Navigation    │ Metrics                              │
│ rail          │ Map or main chart                    │
│               │ Supporting table / evidence          │
└───────────────┴─────────────────────────────────────┘
```

Sidebar width: approximately 250–280px.

Main content width: use Streamlit wide layout with a maximum readable content width.

Use a 12-column conceptual grid:

- Full-width hero: 12 columns
- Four metric cards: 3 columns each
- Map and summary table: 7 columns and 5 columns
- Filters: 3 or 4 columns depending on screen width

Do not place more than four primary metric cards in one row.

## 4.2 Mobile layout

The interface must remain usable on screens below 768px.

Requirements:

- Sidebar collapses or becomes a top menu.
- Metric cards stack into one or two columns.
- Tables use horizontal scrolling or a carefully selected compact column set.
- Maps use full available width and reduced height.
- Filters stack vertically.
- Do not rely on hover-only interactions.
- Buttons should be at least 44px high.
- Form controls should use full width on mobile.
- Avoid fixed-width HTML elements.
- Use responsive CSS media queries.
- Test the layout at approximately 390px, 768px and desktop width.

Use CSS such as:

```css
@media (max-width: 768px) {
  .hero h1 { font-size: 1.35rem; }
  .hero { padding: 20px; border-radius: 16px; }
  .metric-grid { grid-template-columns: 1fr 1fr; }
  .dashboard-card { padding: 14px; }
}

@media (max-width: 480px) {
  .metric-grid { grid-template-columns: 1fr; }
  .section-title { font-size: 1rem; }
}
```

---

# 5. Navigation structure

Create the following navigation pages:

1. **Home / Live overview**
2. **Prediction Studio**
3. **Data & Integration**
4. **Geographic Explorer**
5. **Coverage & Quality**
6. **Price Trends**
7. **Rainfall & Climate**
8. **Model Performance**
9. **Historical Holdout Predictions**
10. **Research Evidence**
11. **Limitations & Interpretation**

Use icons from an external icon library if compatible with Streamlit, such as:

- `streamlit-option-menu`
- `streamlit-aggrid`
- Material Symbols through CSS
- Lucide-style Unicode or SVG icons

If adding a library creates unnecessary deployment risk, use simple text and Unicode-safe icons. Icons must support the label, not replace it.

Recommended navigation icons:

| Page | Icon concept |
|---|---|
| Home | Dashboard/grid |
| Prediction Studio | Sliders or wand |
| Data & Integration | Database |
| Geographic Explorer | Map pin |
| Coverage & Quality | Activity/check |
| Price Trends | Trending-up |
| Rainfall & Climate | Cloud/rain |
| Model Performance | Bar chart |
| Holdout Predictions | History |
| Research Evidence | Book/open paper |
| Limitations | Alert triangle |

---

# 6. Home / Live overview page

This is the primary page and must be the clearest page in the system.

## 6.1 Hero header

Display:

- Project name: `Zimbabwe Food Price Stress`
- Subtitle: `Machine-learning prediction and evidence dashboard`
- Badge: `Research prototype`
- Latest local sync timestamp
- Latest available month
- Predicted month

The hero must not say `Live` if no external live connector is available. Use:

- `Latest available snapshot`
- `Local artefact sync`
- `User-entered current-month score`

## 6.2 Metric cards

Show cards for:

1. Total rows in final model panel
2. Total columns in final model panel
3. Number of districts
4. Number of markets
5. Number of commodities
6. Rainfall records
7. Labelable Y1 observations
8. Labelable Y2 observations

Each card must have:

- Label
- Large value
- Short supporting caption
- Optional information tooltip
- Consistent icon

## 6.3 Model status strip

Show two model status cards:

### Y1 standardised-return stress

- Model name
- Target definition
- Training boundary
- Number of training rows
- Training prevalence
- Status: available/unavailable

### Y2 peer-relative stress

- Model name
- Target definition
- Training boundary
- Number of training rows
- Training prevalence
- Status: available/unavailable

Use purple for evidence/model metadata.

## 6.4 Latest snapshot prediction section

Use a large two-column layout:

### Left: map

Show a map of latest available predictions by district or market.

Map requirements:

- Use actual latitude and longitude from the project data.
- Use `pydeck`, `st.map`, Plotly Mapbox or another compatible map library.
- Do not use invented coordinates.
- Map point size should reflect the number of observations or population.
- Map colour should reflect selected probability or risk band.
- Provide a legend.
- Add a map metric selector:
  - Y1 probability
  - Y2 probability
  - Observed historical stress
  - Rainfall anomaly
  - Number of observations

### Right: ranked prediction table

Show:

- Rank
- District
- Market
- Commodity/category
- Predicted month
- Y1 probability
- Y2 probability
- Risk band
- Data quality flag

Add controls:

- Select target
- Select top 10 / 25 / 50 / 100
- Filter by category
- Filter by currency
- Probability threshold slider

Provide a download button for the filtered table.

## 6.5 Sync control

Add a clearly labelled button:

`Refresh latest project data`

If an external data connector exists in the complete project, use it only through the documented project connector or API. If no connector exists:

- Refresh the local artefact cache.
- Show the source path and last modified timestamp.
- Do not claim that an external API was queried.

---

# 7. Prediction Studio page

This page must contain both manual entry and CSV batch scoring on the same page.

Use `st.tabs`:

1. `Manual current-month input`
2. `CSV batch prediction`
3. `Scored results`
4. `Input quality`

## 7.1 Manual form

Use a clean card-style form.

### Identity fields

- District
- Market
- Commodity ID
- Commodity/category
- Currency
- Prediction month

### Current price fields

- Current price
- Previous price
- Peer median
- Peer count

### Rainfall fields

- Current rainfall anomaly z-score
- Lagged rainfall anomaly 1 month
- Lagged rainfall anomaly 2 months
- Lagged rainfall anomaly 3 months
- Three-month rainfall total or rolling measure

### Optional context fields

- Population
- Latitude
- Longitude
- Standardised current return
- Current SPI/peer-relative index

Buttons:

- `Score this input`
- `Clear form`
- `Load example from latest panel month`

## 7.2 Manual prediction result

Show a strong result panel with two side-by-side prediction cards.

### Y1 card

- `Y1 standardised-return stress`
- Probability as percentage
- Risk band
- Target definition
- Model name
- Training boundary
- Warning if fields were defaulted

### Y2 card

- `Y2 peer-relative stress`
- Probability as percentage
- Risk band
- Target definition
- Model name
- Training boundary
- Warning if fields were defaulted

Use progress bars or horizontal probability bars, but do not rely on progress bars alone.

## 7.3 CSV batch upload

Provide:

- Downloadable CSV template
- File uploader
- Input schema description
- Alias handling for common column names
- Clear validation report
- Row count uploaded
- Rows successfully scored
- Rows rejected
- Missing required fields
- Defaulted optional fields

The CSV must support:

- One district
- Multiple districts
- All districts
- Multiple commodities
- Multiple currencies
- Latitude/longitude for mapping

Do not require the user to upload a separate file for each district.

## 7.4 Batch output layout

Use tabs on the same page:

### Map tab

- Map of uploaded predictions
- Select Y1/Y2
- Select probability or risk band
- Threshold slider
- Point-size selector
- Map legend

### Table tab

- Sortable prediction table
- Search/filter controls
- Risk band
- Probability values
- District and commodity
- Data-quality flags
- Download scored CSV

### Summary tab

Show:

- Total rows scored
- Districts scored
- High-risk rows
- Very-high-risk rows
- Missing-input rows
- Average Y1 probability
- Average Y2 probability

---

# 8. Data & Integration page

This page must demonstrate the implementation of the project objectives.

Use a visual pipeline:

```text
Raw sources
   ↓
Validated source tables
   ↓
First combined dataset
   ↓
Cleaned and aggregated panel
   ↓
Rainfall and geographic features
   ↓
Target labels
   ↓
Model-ready datasets
   ↓
Persisted model predictions
```

Use teal for available data stages, amber for warnings and slate for unavailable stages.

## 8.1 Artefact catalogue

Create a table containing:

- Dataset name
- Pipeline stage
- File path
- File type
- Rows
- Columns
- Date range
- Key fields
- Status
- Last modified date
- Purpose

## 8.2 Dataset tabs

Create tabs for:

1. Raw WFP food prices
2. Raw market data
3. Raw rainfall data
4. First combined dataset
5. Processed USD panel
6. Processed nominal panel
7. Rainfall anomaly dataset
8. Market–district crosswalk
9. Final model-ready data
10. Prediction artefacts

Each tab must include:

- File path
- Number of rows and columns
- Date range
- Preview table
- Missingness summary
- Download button
- Documentation note

For large files:

- Do not load the entire file repeatedly.
- Use cached loaders.
- Show sampled rows and summary statistics.
- Use `st.cache_data`.
- Use Parquet filters where possible.

## 8.3 Integration metrics

Show:

- Number of price records integrated
- Number of monthly food cells
- Number of markets matched to districts
- Number of unmatched markets
- Number of rainfall district-month rows
- Number of model-ready rows
- Percentage of rows with target labels
- Percentage with rainfall features
- Percentage with geographic coordinates

---

# 9. Geographic Explorer page

This page should demonstrate spatial analysis and support rapid decision-making.

## Filters

Provide filters for:

- Year
- Month
- District
- Province
- Market
- Commodity
- Category
- Currency
- Price base
- Stress type: Y1 or Y2
- Probability threshold
- Risk band
- Minimum peer count
- Rainfall anomaly range

## Map modes

Allow the user to choose:

1. Probability map
2. Risk-band map
3. Observed historical stress map
4. Rainfall anomaly map
5. Price-change map
6. Data coverage map

## Map design

Use a geographic colour scale:

- Low: Green or teal
- Watch: Amber
- High: Orange-red
- Very high: Red

Use a visible legend with text labels.

On hover, display:

- District
- Market
- Commodity
- Month
- Target
- Probability
- Risk band
- Current price
- Peer median
- Rainfall anomaly
- Data-quality flags

## Map/table relationship

The table and map must respond to the same filters.

Add:

- `Download filtered data`
- `Download map-ready CSV`
- `Reset filters`

---

# 10. Coverage & Quality page

Display:

- Monthly record coverage chart
- Currency coverage
- Category coverage
- District coverage
- Market coverage
- Missingness heatmap or table
- Price-flag distribution
- Series-length distribution
- Labelability by month
- Rainfall coverage
- Coordinate coverage

Use compact charts with clear titles and units.

Every chart must have a short explanation beneath it.

Example:

> Only 37% of cells are labelable for a next-month supervised target because several market–commodity series are short.

---

# 11. Price Trends page

Include:

- Median monthly price by category
- Price trend by district
- Price trend by commodity
- Currency selector
- Price-base selector
- Date-range selector
- Optional normalised price index
- Download filtered trend data

Use Plotly where suitable, with:

- Hover labels
- Zoom
- Reset axes
- Legend toggles
- Responsive width

Do not use misleading dual axes unless clearly labelled.

---

# 12. Rainfall & Climate page

Include:

- District rainfall map
- Monthly rainfall series
- Rainfall anomaly series
- Seasonal climatology
- Lagged rainfall variables
- Three-month rolling rainfall
- Rainfall–return lead-lag table
- Rainfall data source and climatology period

Clearly state:

> Rainfall is treated as an indirect predictor. The dashboard does not establish that rainfall causes price stress.

---

# 13. Model Performance page

Include:

- Model selector
- Target selector
- Price-base selector
- Cross-validation versus holdout comparison
- ROC-AUC
- PR-AUC
- F1 score
- Balanced accuracy
- Brier score
- Calibration
- Confusion matrix
- Precision-recall curve
- ROC curve
- Feature importance
- Importance stability
- Threshold sensitivity
- Robustness results

Use a model summary card with:

- Model name
- Training rows
- Training boundary
- Holdout boundary
- Number of features
- Seed
- Configuration version

Use purple styling for research-validation components.

Include a clear note:

> Performance varies by target. Y2 is partly persistence-driven, while Y1 is more difficult. Do not compare scores across different targets as if they measured the same task.

---

# 14. Historical Holdout Predictions page

Include:

- Task selector
- Model selector
- Year filter
- Month filter
- Commodity filter
- District filter
- Probability threshold
- Ranked table
- Historical prediction map if coordinates are available
- Download button

Label the page explicitly:

> Historical holdout predictions — not live forecasts

---

# 15. Research Evidence page

Use this page to connect the implementation to the dissertation objectives.

Display objective cards such as:

### Objective 1: Data integration

Evidence shown in the UI:

- Raw dataset catalogue
- Combined panel preview
- Rainfall integration
- Geographic crosswalk
- Model-ready table

### Objective 2: Target construction

Evidence shown in the UI:

- Y1 definition
- Y2 definition
- Target prevalence
- Labelability metrics

### Objective 3: Predictive modelling

Evidence shown in the UI:

- Persisted models
- Feature lists
- Training boundary
- Model metrics
- Holdout predictions

### Objective 4: Geographic decision support

Evidence shown in the UI:

- District filters
- Maps
- Ranked prediction tables
- CSV export

### Objective 5: Reproducibility and limitations

Evidence shown in the UI:

- Artefact paths
- Metadata
- Configuration version
- Data-quality warnings
- Limitations page

Include a table:

| Objective | Implementation evidence | Dashboard page |
|---|---|---|
| Data integration | Dataset catalogue and pipeline stages | Data & Integration |
| Target construction | Y1 and Y2 definitions | Home, Research Evidence |
| Prediction | Persisted model scoring | Prediction Studio |
| Geographic analysis | Filtered maps and tables | Geographic Explorer |
| Model evaluation | Validation metrics and robustness | Model Performance |

---

# 16. Limitations & Interpretation page

Use a visually distinct warning style but keep it professional.

Include:

- No prospective validation
- Latest local snapshot may not be live external data
- Sparse market–commodity series
- Currency-regime differences
- Missing or incomplete raw source files
- Missing geographic coordinates where applicable
- Weak rainfall association
- Y2 persistence limitation
- Model uncertainty
- Market stress is not household food insecurity
- Dashboard predictions are not official warnings

Use amber and red callout cards, but avoid alarmist wording.

---

# 17. Component design rules

## Cards

```css
.dashboard-card {
  background: #FFFFFF;
  border: 1px solid #E2E8F0;
  border-radius: 16px;
  padding: 18px;
  box-shadow: 0 8px 24px -22px rgba(15, 23, 42, .55);
}
```

Use cards for:

- Metrics
- Model status
- Prediction results
- Dataset stages
- Research objectives

## Buttons

Primary button:

- Background: Blue-600
- Hover: Blue-700
- Text: White
- Radius: 10px
- Height: at least 42px

Secondary button:

- Background: White
- Border: Slate-300
- Text: Slate-800
- Hover border: Blue-600

Danger/warning button:

- Use only for reset or destructive actions.
- Never use red for ordinary prediction actions.

## Badges

Examples:

- `Available` — green
- `Latest available` — blue
- `Model loaded` — teal
- `Needs review` — amber
- `Not bundled` — slate/amber
- `High stress` — red

## Tables

Use compact tables with:

- Sticky headers where supported
- Zebra rows only if readability improves
- Right-aligned numeric values
- Rounded outer border
- Download button
- Human-readable column labels
- Hidden technical columns by default

Never display dozens of raw technical feature columns by default. Put them in an expander called `Technical fields`.

## Expanders

Use expanders for:

- Technical metadata
- Feature definitions
- File paths
- Data-quality details
- Validation methodology
- Raw schema

---

# 18. Performance and caching

Use:

```python
@st.cache_data(show_spinner=False)
```

for:

- Parquet loading
- CSV loading
- Dataset summaries
- Metrics loading
- Historical predictions

Use:

```python
@st.cache_resource(show_spinner=False)
```

for:

- Persisted model loading
- Reusable model pipelines

Do not load very large raw files on every interaction.

Use lightweight previews and summaries for large datasets.

Avoid repeated full-data joins inside widget callbacks.

Use session state for:

- Uploaded prediction results
- Active filter state
- Selected target
- Selected map metric
- Last scoring results

---

# 19. Input validation and error messages

All user input must be validated.

Examples:

- Current price must be greater than zero.
- Previous price must be greater than zero when supplied.
- Peer median must be greater than zero when supplied.
- Peer count must be a non-negative integer.
- Month must be a valid date.
- Probability thresholds must be between 0 and 1.
- Latitude must be between -90 and 90.
- Longitude must be between -180 and 180.
- CSV must contain at least one row.
- CSV must include enough fields for scoring.

Use friendly error messages:

> The file was read successfully, but no usable current-price column was found. Accepted names include `current_price`, `price`, `latest_price` and `usdprice`.

Do not expose Python tracebacks to normal dashboard users. Log technical details separately.

---

# 20. Accessibility

Implement:

- High colour contrast
- Clear visible labels
- Text labels alongside icons
- No colour-only risk interpretation
- Readable font sizes
- Keyboard-friendly controls
- Descriptive help text
- Alt text or captions for images and charts where possible
- Mobile-friendly controls

---

# 21. File and module structure

Prefer a maintainable structure:

```text
dashboard/
├── app.py
├── scoring.py
├── data_catalog.py
├── ui_components.py
├── charts.py
├── map_views.py
├── styles.py
└── README.md
```

Responsibilities:

- `app.py`: navigation and page composition
- `scoring.py`: input normalisation, model loading and scoring
- `data_catalog.py`: dataset discovery and summaries
- `ui_components.py`: cards, badges, metric blocks and notices
- `charts.py`: reusable Plotly/Streamlit charts
- `map_views.py`: map aggregation and map rendering
- `styles.py`: CSS and theme definitions

If the existing project is simpler, do not create unnecessary files. Maintain clear separation of concerns.

---

# 22. External libraries

Use these only where compatible and justified:

- `plotly` for interactive charts
- `pydeck` for geographic layers
- `streamlit-aggrid` for sortable/filterable tables
- `streamlit-option-menu` for navigation
- `streamlit-extras` for small UI enhancements
- `joblib` for persisted model loading
- `pandas` and `pyarrow` for data handling
- `scikit-learn` for model pipeline inference

Do not add a library merely for decoration. The application must remain reproducible and easy to run.

---

# 23. Testing requirements

Before completion:

1. Run Python syntax checks.
2. Import every dashboard module.
3. Load every expected persisted model.
4. Run one manual score.
5. Run a multi-row CSV score.
6. Test missing optional fields.
7. Test invalid prices and dates.
8. Test empty CSV upload.
9. Test coordinate-present map data.
10. Test coordinate-missing fallback.
11. Test every page loads without a fatal exception.
12. Test the app at desktop width.
13. Test the app at mobile width.
14. Confirm that all download buttons produce valid files.
15. Confirm that raw, combined, processed and model-ready artefacts are labelled correctly.
16. Confirm that the UI does not claim external live data when only local artefacts exist.
17. Confirm that all existing research results remain unchanged.

Create a validation report at:

```text
reports/dashboard_validation.md
```

The report must list:

- Files changed
- Pages implemented
- Model tests passed
- CSV tests passed
- Map tests passed
- Responsive checks completed
- Missing project inputs
- Remaining limitations

---

# 24. Final acceptance criteria

The dashboard is complete only when:

- The home page gives an immediate overview of data, model state and latest predictions.
- Users can enter current-month data manually and receive real predictions from the persisted models.
- Users can upload a CSV containing one or many districts and receive predictions for every valid row.
- The CSV output includes Y1 and Y2 predictions, risk bands and data-quality flags.
- The map and table are available on the same prediction page through separate switches or tabs.
- The map responds to the same filters as the table.
- The data page shows raw, combined, processed and model-ready datasets where those files exist.
- The geographic page supports filtering by year, commodity, target and other relevant metrics.
- Model metrics and validation evidence are easy to find.
- The UI visibly demonstrates the implementation of the research objectives.
- The interface is modern, consistent and mobile-responsive.
- Missing raw files or coordinates are reported honestly.
- All scores shown in the UI come from real persisted models or clearly labelled historical artefacts.
- No result, source, coordinate, data row or model metric is fabricated.

At the end, provide a concise implementation report containing:

1. Pages added or redesigned
2. Components added
3. Data files used
4. Models used
5. New dependencies
6. Tests completed
7. Dashboard URL or run command
8. Remaining limitations
" 
