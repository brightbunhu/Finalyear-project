# Dataset Sources & Download Guide

This document lists all datasets utilized in this research project (**"Early Warning Machine Learning Architecture for Food Price Stress and Anomalies in Zimbabwe"**). It provides the exact sources, publishing organizations, official download links, and descriptions so that anyone can download the exact same datasets to reproduce the pipeline.

---

## Summary of Core Datasets

| Dataset Name | Organization / Provider | Direct / Portal Link | Local Destination Path | Format & Approx. Size |
| :--- | :--- | :--- | :--- | :--- |
| **WFP Food Prices for Zimbabwe** | United Nations World Food Programme (WFP) | [HDX WFP Food Prices Zimbabwe](https://data.humdata.org/dataset/wfp-food-prices-for-zimbabwe) | `raw/wfp_food_prices_zwe.csv` | CSV (~4.6 MB) |
| **WFP Market Master List & Coordinates** | United Nations World Food Programme (WFP) | [HDX WFP Food Prices Zimbabwe](https://data.humdata.org/dataset/wfp-food-prices-for-zimbabwe) | `raw/wfp_markets_zwe.csv` | CSV (~28 KB) |
| **CHIRPS High-Resolution Precipitation NetCDF** | Climate Hazards Center (CHC), UC Santa Barbara (UCSB) | [UCSB CHC CHIRPS-2.0 Data Portal](https://data.chc.ucsb.edu/products/CHIRPS-2.0/) | `raw/yr.nc` | NetCDF (`.nc`, ~8.5 GB uncompressed) |
| **geoBoundaries Zimbabwe ADM2 (Districts)** | William & Mary geoLab / ZIMSTAT / UN OCHA | [geoBoundaries GitHub Release](https://github.com/wmgeolab/geoBoundaries/raw/9469f09/releaseData/gbOpen/ZWE/ADM2/geoBoundaries-ZWE-ADM2.geojson) | `raw/geo/zwe_adm2_geoboundaries.geojson` | GeoJSON (~17.4 MB) |
| **geoBoundaries Zimbabwe ADM1 (Provinces)** | William & Mary geoLab / ZIMSTAT / UN OCHA | [geoBoundaries GitHub Release](https://github.com/wmgeolab/geoBoundaries/raw/9469f09/releaseData/gbOpen/ZWE/ADM1/geoBoundaries-ZWE-ADM1.geojson) | `raw/geo/zwe_adm1_geoboundaries.geojson` | GeoJSON (~7.2 MB) |
| **HDX HAPI Census & Population Data** | UN OCHA / Humanitarian Data Exchange (HDX) | [HDX HAPI Platform](https://hapi.humdata.org/) | `raw/hdx_hapi_population_zwe.csv` | CSV (~650 KB) |
| **HDX HAPI Subnational Poverty Rate** | UN OCHA / Humanitarian Data Exchange (HDX) | [HDX HAPI Platform](https://hapi.humdata.org/) | `raw/hdx_hapi_poverty_rate_zwe.csv` | CSV (~4 KB) |
| **HDX HAPI Food Price Index (ZWE)** | UN OCHA / Humanitarian Data Exchange (HDX) | [HDX HAPI Platform](https://hapi.humdata.org/) | `raw/hdx_hapi_food_price_zwe.csv` | CSV (~4.6 MB) |
| **HDX HAPI District Rainfall (ZWE)** | UN OCHA / Humanitarian Data Exchange (HDX) | [HDX HAPI Platform](https://hapi.humdata.org/) | `raw/hdx_hapi_rainfall_zwe.csv` | CSV (~666 KB) |
| **World Bank Enterprise Survey (Sampling & Stratification)** | World Bank Group | [World Bank Enterprise Surveys](https://www.enterprisesurveys.org/) | `raw/DataDetails.xls` | XLS (~683 KB) |
| **PRISMA Literature Systematic Search** | OpenAlex (OurResearch) & Google Scholar | [OpenAlex Portal](https://openalex.org/) & [Harzing Publish or Perish](https://harzing.com/resources/publish-or-perish) | `data/literature/raw/` | CSVs |

---

## Detailed Dataset Descriptions & Download Instructions

### 1. WFP Food Prices for Zimbabwe
* **Organization:** United Nations World Food Programme (WFP) — Vulnerability Analysis and Mapping (VAM)
* **Dataset Name:** Zimbabwe Food Prices
* **HDX Dataset URL:** <https://data.humdata.org/dataset/wfp-food-prices-for-zimbabwe>
* **Alternative Portal:** <https://dataviz.vam.wfp.org/>
* **File Target:** `raw/wfp_food_prices_zwe.csv`
* **Description:** Monthly food commodity retail and wholesale price monitoring data across Zimbabwean markets covering maize meal, maize grain, cooking oil, sugar, bread, and other key dietary essentials. Includes prices in both local currencies (ZWL/ZiG) and converted USD equivalent prices.

### 2. WFP Markets Master List
* **Organization:** United Nations World Food Programme (WFP)
* **Dataset Name:** Zimbabwe Market List & Geographic Coordinates
* **HDX Dataset URL:** <https://data.humdata.org/dataset/wfp-food-prices-for-zimbabwe> (resource: `wfp_markets_zwe.csv`)
* **File Target:** `raw/wfp_markets_zwe.csv`
* **Description:** Contains `market_id`, market name, administrative levels (`admin1`, `admin2`), and official GPS coordinates (`latitude`, `longitude`) used for spatial crosswalking and point-in-polygon assignment.

### 3. CHIRPS Precipitation Gridded NetCDF
* **Organization:** Climate Hazards Center (CHC), University of California, Santa Barbara (UCSB) & USGS
* **Dataset Name:** Climate Hazards Group InfraRed Precipitation with Station data (CHIRPS) v2.0
* **Official Website:** <https://www.chc.ucsb.edu/data/chirps>
* **Direct Data Repository / FTP:** <https://data.chc.ucsb.edu/products/CHIRPS-2.0/>
  - Global Monthly NetCDF: <https://data.chc.ucsb.edu/products/CHIRPS-2.0/global_monthly/netcdf/>
  - Global Daily NetCDF: <https://data.chc.ucsb.edu/products/CHIRPS-2.0/global_daily/netcdf/p05/>
* **File Target:** `raw/yr.nc`
* **Note on GitHub & File Size:** This file is approximately **8.5 GB** uncompressed and is excluded from GitHub via `.gitignore`. Download the monthly or daily NetCDF covering the southern Africa window (Lat: -23.0 to -15.0, Lon: 24.5 to 33.5) and save it as `raw/yr.nc`.

### 4. geoBoundaries Administrative Boundaries (ADM1 & ADM2)
* **Organization:** William & Mary geoLab, in partnership with Zimbabwe National Statistics Agency (ZIMSTAT) and UN OCHA ROSEA
* **Dataset Name:** geoBoundaries Zimbabwe Administrative Boundaries (Open License gbOpen)
* **geoBoundaries Home:** <https://www.geoboundaries.org/>
* **HDX Source:** <https://data.humdata.org/dataset/zimbabwe-administrative-levels-0-3-boundaries>
* **Direct Download Links:**
  - **ADM2 (Districts):** <https://github.com/wmgeolab/geoBoundaries/raw/9469f09/releaseData/gbOpen/ZWE/ADM2/geoBoundaries-ZWE-ADM2.geojson>
    - Save to: `raw/geo/zwe_adm2_geoboundaries.geojson`
  - **ADM1 (Provinces):** <https://github.com/wmgeolab/geoBoundaries/raw/9469f09/releaseData/gbOpen/ZWE/ADM1/geoBoundaries-ZWE-ADM1.geojson>
    - Save to: `raw/geo/zwe_adm1_geoboundaries.geojson`
* **Description:** Official boundary polygons for spatial alignment and calculating district-level monthly rainfall zonal means.

### 5. HDX Humanitarian API (HAPI) Data
* **Organization:** United Nations Office for the Coordination of Humanitarian Affairs (UN OCHA)
* **Dataset Name:** HDX HAPI (Humanitarian API) - Zimbabwe Ingestion Endpoints
* **API Portal & Documentation:** <https://hapi.humdata.org/> & <https://hapi.humdata.org/docs>
* **Files Target:**
  - `raw/hdx_hapi_population_zwe.csv`: District demographic population metrics from ZIMSTAT / UN OCHA.
  - `raw/hdx_hapi_poverty_rate_zwe.csv`: Multidimensional Poverty Index (MPI) and headcount deprivation rates.
  - `raw/hdx_hapi_food_price_zwe.csv`: HAPI food price standardized indicators.
  - `raw/hdx_hapi_rainfall_zwe.csv`: Aggregated rainfall indicators and anomaly metrics.

### 6. World Bank Enterprise Surveys
* **Organization:** The World Bank Group
* **Dataset Name:** Enterprise Surveys Zimbabwe Stratification and Methodology
* **Website:** <https://www.enterprisesurveys.org/>
* **File Target:** `raw/DataDetails.xls`
* **Description:** Sampling stratification variables and sector details for economic baseline validation.

### 7. PRISMA Systematic Literature Review Data
* **Organizations:** OpenAlex ([OurResearch](https://openalex.org/)) & Google Scholar ([Harzing's Publish or Perish](https://harzing.com/resources/publish-or-perish))
* **Directory Target:** `data/literature/raw/`
* **Description:** Search logs and retrieved records for 6 academic query strings (S1 to S6) detailing food price volatility, climate shocks, and machine learning architectures in Sub-Saharan Africa.

---

## Directory Setup Instructions

To run the complete data processing pipeline after cloning the repository:

1. Create the `raw/` and `raw/geo/` directories if they do not exist:
   ```bash
   mkdir -p raw/geo
   ```
2. Download the datasets from the links provided above.
3. Place each file in its corresponding directory as specified in the table.
4. Execute the pipeline:
   ```bash
   python src/build_rainfall.py
   python src/build_dataset.py
   python src/train.py
   ```
