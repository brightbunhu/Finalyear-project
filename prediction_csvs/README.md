# Prediction Datasets for Early Warning Stress Forecasting

This directory contains standardized, pre-configured prospective prediction datasets for forecasting food-price stress across Zimbabwe for **November 2026 through February 2027** (the critical Southern Africa summer agricultural & lean season).

---

## Summary of Datasets

| File Name | Horizon / Months | Scope / Markets | Format & Purpose | Dashboard Tab |
|---|---|---|---|---|
| **`prediction_november_2026_all_markets.csv`** | Nov 2026 (1 month) | All 327 active markets | Technical batch feature schema (21 cols) | Prediction Studio &rarr; *CSV batch prediction* |
| **`prediction_november_2026_3_markets.csv`** | Nov 2026 (1 month) | 3 benchmark markets (Harare, Nkayi, Mutare) | Technical batch feature schema (21 cols) | Prediction Studio &rarr; *CSV batch prediction* |
| **`prediction_dec_jan_feb_all_markets.csv`** | Dec 2026, Jan 2027, Feb 2027 | All 327 active markets (981 rows) | Technical batch feature schema (21 cols) | Prediction Studio &rarr; *CSV batch prediction* |
| **`prediction_dec_jan_feb_3_markets.csv`** | Dec 2026, Jan 2027, Feb 2027 | 3 benchmark markets (9 rows) | Technical batch feature schema (21 cols) | Prediction Studio &rarr; *CSV batch prediction* |
| **`prediction_nov_to_feb_all_markets.csv`** | Nov 2026 &ndash; Feb 2027 (4 months) | All 327 active markets (1,308 rows) | Full multi-month national batch dataset | Prediction Studio &rarr; *CSV batch prediction* |
| **`prediction_nov_to_feb_3_markets.csv`** | Nov 2026 &ndash; Feb 2027 (4 months) | 3 benchmark markets (12 rows) | Multi-month benchmark inspection | Prediction Studio &rarr; *CSV batch prediction* |
| **`prediction_non_technical_nov_to_feb_one_by_one.csv`** | Nov 2026 &ndash; Feb 2027 (4 months) | 3 benchmark markets (12 scenarios) | **Human-readable intuitive prices & weather** | Prediction Studio &rarr; *Next-month predictor* |
| **`prediction_technical_nov_to_feb_one_by_one.csv`** | Nov 2026 &ndash; Feb 2027 (4 months) | 3 benchmark markets (12 scenarios) | **Direct mathematical features + audited model probabilities** | Prediction Studio &rarr; *Advanced mode* & *CSV batch* |

---

## 1. How to Use: For Non-Technical Users
Open file: **`prediction_non_technical_nov_to_feb_one_by_one.csv`**

1. Go to **Dashboard &rarr; Make a Prediction &rarr; Next-month predictor**.
2. Select any row from the CSV (e.g., Row 1 for Harare Mbare or Row 2 for Nkayi Growth Point).
3. Fill in the intuitive form:
   - **District**: Select the district (e.g., `Harare` or `Nkayi`).
   - **Market (optional)**: Enter the market name (e.g., `Mbare`).
   - **Commodity**: Select `Maize (grain)` or roller meal.
   - **Observed month (t)**: Set year and month (e.g. `2026` / `10` for October 2026).
   - **Price inputs**: Enter the 4 prices: current month price, 1 month prior, 2 months prior, 3 months prior.
   - **Contemporaneous peer median price**: Enter the peer median.
   - **Precipitation conditions**: Pick the preset matching the `weather_condition` column (e.g. *Severe Drought* or *Below Normal*).
4. Click **Run Prediction**:
   - The dashboard automatically calculates the standardized return Z-score, SPI, and climate-price interaction.
   - Outputs the predicted risk band and actionable operational recommendations!

---

## 2. How to Use: For Technical Users
Open file: **`prediction_technical_nov_to_feb_one_by_one.csv`** or upload any of the batch CSVs:

1. **Direct Inspection (Row-by-Row)**:
   - Go to **Dashboard &rarr; Make a Prediction &rarr; Advanced mode (direct Z-scores)**.
   - Enter `ret_z_cur`, `spi`, `rain_anom_z`, and categorical labels directly.
   - Click **Score Technical Features** to verify mathematical score reproducibility.
2. **Automated Batch Scoring (Fulfills Objective 4)**:
   - Go to **Dashboard &rarr; Make a Prediction &rarr; CSV batch prediction**.
   - Click **Browse files** and upload **`prediction_november_2026_all_markets.csv`** (or `prediction_nov_to_feb_3_markets.csv`).
   - The engine validates all columns, generates predictions via `pipe.predict_proba()`, displays summary statistics, and provides a **Download Scored Rows (CSV)** button.

---

## Benchmark Markets Included
- **Mbare (Market ID 708)**: Harare District &mdash; Primary urban capital wholesale hub.
- **Nkayi Growth Point (Market ID 716)**: Nkayi District (Matabeleland North) &mdash; Rural drought-vulnerable agricultural market.
- **Sakubva (Market ID 724)**: Mutare Urban District (Manicaland) &mdash; Eastern trade corridor border market.
