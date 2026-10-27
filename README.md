# Finalyear-project

## Early Warning Machine Learning Architecture for Food Price Stress and Anomalies in Zimbabwe

An end-to-end econometric and machine learning pipeline for detecting, forecasting, and visualizing localized food price anomalies and price stress across Zimbabwean markets.

---

## Overview

This project harmonizes high-frequency humanitarian market food prices, satellite gridded precipitation climatologies, administrative district boundaries, and demographic data to build an operational early warning system for food security monitoring.

- **Dual-Target Formulations:**
  - **Target $Y_1$ (Temporal Return Surge):** Month-over-month price surge exceeding 1.0 standard deviation of the trailing 12-month volatility.
  - **Target $Y_2$ (Spatial Divergence):** Spatial Price Index (SPI) $\ge 1.20$, capturing localized markets trading $\ge 20\%$ above the contemporaneous national median.
- **Leak-Free Expanding-Window Validation:** 5-fold expanding window with a strict 12-month forward holdout out-of-sample test.
- **Interactive Multi-Page Streamlit Dashboard:** Complete exploration suite covering predictions, spatial mapping, price trends, rainfall anomalies, and model performance.

---

## Dataset Sources & Setup

> [!IMPORTANT]
> Large raw data files (such as the 8.5 GB CHIRPS NetCDF grid `yr.nc`) are excluded from this GitHub repository.

For the complete list of dataset sources, download links, organizations, and setup instructions, see:
👉 **[DATASETS.md](DATASETS.md)**

### Key Data Sources:
1. **WFP Food Prices & Markets:** [UN World Food Programme on HDX](https://data.humdata.org/dataset/wfp-food-prices-for-zimbabwe)
2. **CHIRPS Gridded Precipitation:** [UC Santa Barbara Climate Hazards Center](https://data.chc.ucsb.edu/products/CHIRPS-2.0/)
3. **geoBoundaries Admin Polygons (ADM1 & ADM2):** [geoBoundaries.org](https://www.geoboundaries.org/) / [HDX](https://data.humdata.org/dataset/zimbabwe-administrative-levels-0-3-boundaries)
4. **HDX HAPI Population & Poverty:** [UN OCHA Humanitarian API](https://hapi.humdata.org/)
5. **PRISMA Literature Review:** [OpenAlex](https://openalex.org/) & Google Scholar

---

## Quickstart

### 1. Environment Installation
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Run Data Processing & Modeling
```bash
# Process CHIRPS precipitation grids to district-month zonal statistics
python src/build_rainfall.py

# Build feature panel and generate target variables
python src/build_dataset.py

# Train models and run validation
python src/train.py
```

### 3. Launch the Interactive Dashboard
```bash
streamlit run dashboard/app.py
```

---

## Project Structure
```text
├── config/                 # YAML configuration (targets, features, splits)
├── dashboard/              # Streamlit dashboard application and pages
├── data_processed/         # Derived panels, crosswalks, and feature tables
├── figures/                # Publication-ready figures and evaluation charts
├── models/                 # Serialized model pipelines and metadata
├── raw/                    # Raw datasets (see DATASETS.md for download instructions)
│   └── geo/                # Administrative boundary GeoJSONs
├── reports/                # Technical documentation and evaluation logs
├── screenshots/            # Dashboard interface captures
├── scripts/                # Analysis, report generation, and plotting scripts
├── src/                    # Core machine learning & feature engineering source code
├── DATASETS.md             # Detailed dataset catalogue and download guide
├── README.md               # Repository documentation
└── requirements.txt        # Python package dependencies
```
