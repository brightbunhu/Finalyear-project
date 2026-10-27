# Deploying to Streamlit Community Cloud

This guide details the exact steps to deploy this repository on [Streamlit Community Cloud](https://share.streamlit.io/).

---

## 1. Prerequisites
- A GitHub account connected to Streamlit Community Cloud: [share.streamlit.io](https://share.streamlit.io/)
- This repository: `https://github.com/brightbunhu/Finalyear-project`

---

## 2. Deployment Settings

When creating a new app in Streamlit Cloud:

| Field | Setting | Notes |
| :--- | :--- | :--- |
| **Repository** | `brightbunhu/Finalyear-project` | Select from your GitHub repositories |
| **Branch** | `main` | Default branch |
| **Main file path** | `dashboard/app.py` | ⚠️ **Crucial**: Ensure this is `dashboard/app.py` (not root `app.py`) |
| **App URL** | *Optional custom subdomain* | E.g., `zimbabwe-food-price-stress.streamlit.app` |

Under **Advanced settings** (optional):
- **Python version:** Select **3.11** or **3.12**

---

## 3. How the Dashboard Runs (Self-Contained)

- **Models & Predictions:** The pre-trained Hist-GBM pipelines (`models/y1_return_histgbm_usd.joblib` and `models/y2_peer_histgbm_usd.joblib`) and holdout predictions (`artifacts/preds_*.parquet`) are already pushed to GitHub.
- **Geographic & Panel Data:** The district crosswalks, GeoJSON boundary files (`data_processed/zwe_adm2_simplified.geojson`), and processed panels (`data_processed/panel_*.parquet`) are included directly in the repository.
- **Raw 8.5 GB CHIRPS NetCDF:** The raw `yr.nc` precipitation grid is **NOT** needed by the dashboard runtime. All rainfall anomalies and climatology metrics used by the dashboard are loaded from pre-aggregated, lightweight Parquet tables.
- **Memory Consumption:** The dashboard utilizes caching (`@st.cache_data`) and consumes < 350 MB RAM, well within Streamlit Cloud's 1 GB free-tier limit.

---

## 4. Verification of Pages

Once deployed, all 7 sections and 13 views are fully functional:
1. **Home:** Executive overview, methodology, key findings, and quick KPI indicators.
2. **Make a Prediction (Prediction Studio):** Real-time interactive model inference using trained estimators for Target Y1 (Return Surge) and Target Y2 (Spatial SPI Divergence).
3. **Geographic Explorer:** Interactive district choropleth map, regional food price distribution, and market locator.
4. **Data & Integration:** Ingestion flows, dataset catalog, coverage statistics, price trends, and rainfall anomalies.
5. **Model Performance:** Cross-validation vs. holdout metrics, ROC/PR curves, confusion matrices, and statistical hypothesis tests.
6. **Reports & Downloads:** Export center for CSV prediction batches, diagnostic tables, and PRISMA literature evidence.
7. **About & Help:** Research scope, limitations, econometric caveats, and glossary.
