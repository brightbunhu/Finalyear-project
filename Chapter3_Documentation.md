# Chapter 3: Methodology and Technical Implementation Documentation

**Project Title:** Early Warning Machine Learning Architecture for Food Price Stress and Anomalies in Zimbabwe  
**Author:** Researcher / Dissertation Candidate  
**Academic Document Type:** Chapter 3 Technical Methodology and Pipeline Codebase Reference  

---

## 1. Architectural Overview and System Design

In this chapter, I document the end-to-end data processing, feature engineering, and predictive modeling pipeline developed for forecasting localized food price stress across Zimbabwean markets. The pipeline was designed to adhere strictly to econometric and machine learning best practices:
1. **Zero Temporal Leakage:** Feature standardisation, rolling baseline calculations, hyperparameter tuning, and decision thresholds rely strictly on historical information available at time $t$. Future observations are never incorporated into past feature calculations.
2. **Multi-Source Geospatial Integration:** Harmonising point-level humanitarian price monitoring from the World Food Programme (WFP) with continuous high-resolution satellite precipitation grids from the Climate Hazards Group InfraRed Precipitation with Stations (CHIRPS) and demographic census data from the Humanitarian Data Exchange (HDX).
3. **Rigorous Dual Target Formulation:** Distinguishing between temporal volatility (large month-over-month price accelerations, Target $Y1$) and spatial market divergence (severe premiums above national peer market benchmarks, Target $Y2$).
4. **Leak-Free Expanding-Window Validation:** Simulating true operational deployment using an expanding chronological window with a 12-month forward holdout, entirely eliminating shuffle-induced lookahead bias.

The system is modularised across six core Python modules located in `src/`, governed by a central YAML configuration file (`config/targets.yml`). Below is the complete line-by-line and block-by-block technical exposition of the implementation.

```
+---------------------------------------------------------------------------------------------------+
|                                 DATA INGESTION & HARMONISATION                                    |
|   - WFP Food Prices (raw/wfp_food_prices_zwe.csv)                                                 |
|   - CHIRPS Daily/Monthly Precipitation (raw/yr.nc)                                                |
|   - geoBoundaries Administrative Boundaries (raw/geo/zwe_adm2_geoboundaries.geojson)              |
|   - HDX HAPI Census Population Data (raw/hdx_hapi_population_zwe.csv)                             |
+---------------------------------------------------------------------------------------------------+
                                                  |
                                                  v
+---------------------------------------------------------------------------------------------------+
|                                 GEOSPATIAL & CLIMATE PIPELINE                                     |
|   [src/build_rainfall.py]                                                                         |
|   - Bounding-box spatial slicing (-23.0 to -15.0 Lat, 24.5 to 33.5 Lon)                           |
|   - Point-in-polygon assignment of 0.05-deg CHIRPS grid pixels to Admin-2 Districts               |
|   - Area-weighted district monthly zonal mean precipitation                                       |
|   - Long-term baseline climatology (1981-2015) per district x calendar month                     |
|   - Standardised Precipitation Anomaly (Z-score) derivation                                       |
+---------------------------------------------------------------------------------------------------+
                                                  |
                                                  v
+---------------------------------------------------------------------------------------------------+
|                                 PANEL ASSEMBLY & TARGET ENGINEERING                               |
|   [src/build_dataset.py]                                                                          |
|   - Non-food filtering & non-positive price elimination                                           |
|   - Monthly median aggregation per (market, commodity, currency) cell                             |
|   - Spatial crosswalk & district assignment for humanitarian markets                              |
|   - Target Y1: 12-month trailing standard deviation return surge (Z >= 1.0)                       |
|   - Target Y2: Spatial Price Index (SPI) >= 1.20 (20% above contemporaneous national peer median)  |
|   - Feature engineering: lag returns, rolling means, rain lags, harmonic seasonal features        |
+---------------------------------------------------------------------------------------------------+
                                                  |
                                                  v
+---------------------------------------------------------------------------------------------------+
|                                 VALIDATION, TUNING & MODEL TRAINING                               |
|   [src/tune_optuna.py & src/train.py & src/fit_final_model.py]                                    |
|   - Imputation: Median (continuous features) & Most-Frequent (categorical)                        |
|   - Encoding & Scaling: StandardScaler & OneHotEncoder (handle_unknown='ignore')                  |
|   - 5-Fold Chronological Expanding Window Validation (Training period only)                       |
|   - Optuna Bayesian Hyperparameter Optimization (TPE Sampler on CV ROC-AUC)                       |
|   - Decision Threshold Optimisation: F1-maximisation on pooled validation out-of-fold predictions  |
|   - Out-of-sample forward evaluation on unseen 12-month forward holdout                           |
+---------------------------------------------------------------------------------------------------+
                                                  |
                                                  v
+---------------------------------------------------------------------------------------------------+
|                                 DIAGNOSTICS & ROBUSTNESS SUITE                                    |
|   [src/analysis.py & src/robustness.py & src/figures_chapter4.py]                                 |
|   - Lead-lag Pearson & Spearman correlation tests                                                 |
|   - Permutation Feature Importance across 20 bootstrap repeats                                    |
|   - Regime & temporal breakdown (pre-2019 ZWL vs multicurrency era)                               |
|   - Clustered market-level uncertainty bootstrapping                                              |
+---------------------------------------------------------------------------------------------------+
```

---

## 2. Configuration Architecture (`config/targets.yml`)

To prevent arbitrary parameter tuning or divergence across different scripts, I established a single source of truth in `config/targets.yml`. Every downstream script imports this configuration.

### Parameter Specifications

```yaml
version: "0.1.0"
seed: 42

# Panel Unit Definition
unit:
  keys: [market_id, commodity_id, currency]
  time_key: month
horizon_months: 1

# Price Bases Investigated
price_bases:
  - name: nominal_within_currency   # Base 1 (B1): native currency records
    value_column: price
    currency_scoped: true
  - name: usdprice                  # Base 2 (B2): converted USD equivalent
    value_column: usdprice
    currency_scoped: false

# Commodity Filtering
categories:
  include:
    - cereals and tubers
    - pulses and nuts
    - oil and fats
    - meat, fish and eggs
    - miscellaneous food
  exclude:
    - non-food

# Target Y1: Standardised Return Stress
target_return_stress:
  name: y1_return_stress
  return_transform: log
  standardise: trailing
  trailing_window_months: 12
  min_prior_returns: 6
  threshold_sd: 1.0
  threshold_grid_sd: [0.5, 0.75, 1.0, 1.25, 1.5, 2.0]

# Target Y2: Spatial Peer-Relative Stress
target_peer_stress:
  name: y2_peer_stress
  peer_group: [commodity_id, currency, month]
  peer_stat: median
  min_peer_markets: 5
  min_peer_grid: [3, 5, 10]
  threshold_spi: 1.20
  threshold_grid_spi: [1.10, 1.20, 1.30, 1.50]

# Rainfall (CHIRPS NetCDF) Parameters
rainfall:
  source: raw/yr.nc
  variable: precip
  spatial_agg: district_zonal_mean
  climatology_start: 1981-01
  climatology_end: 2015-12
  anomaly: z_score_by_district_calendar_month
  lags_months: [1, 2, 3]
  rolling_sum_months: [3]

# Validation Strategy
validation:
  scheme: expanding_window
  n_folds: 5
  holdout_months: 12

# Bayesian Hyperparameter Tuning
optuna:
  enabled: true
  n_trials: 40
  sampler_seed: 42
  models: [hist_gradient_boosting]
```

---

## 3. Detailed Line-by-Line Code Analysis

### 3.1 CHIRPS Climate Processing (`src/build_rainfall.py`)

This script extracts monthly precipitation from the NetCDF archive, spatially maps raster cells to administrative districts, computes historical climatological baselines, and generates standardized precipitation anomaly Z-scores.

#### Libraries Used
- `xarray`: High-performance multi-dimensional array operations for reading NetCDF raster formats.
- `geopandas` & `shapely`: Vector geospatial operations and topological spatial joins.
- `numpy` & `pandas`: Numerical manipulation and tabular restructuring.

#### Code Walkthrough & Design Decisions

```python
LAT_SLICE = (-23.0, -15.0)
LON_SLICE = (24.5, 33.5)
CLIM_START = "1981-01-01"
CLIM_END = "2015-12-31"
```
*Why:* I sliced the global CHIRPS dataset specifically to the bounding box encompassing Zimbabwe ($15^\circ\text{S} - 23^\circ\text{S}$, $24.5^\circ\text{E} - 33.5^\circ\text{E}$). This reduced RAM consumption by over 98% compared to processing the full global grid. The 1981–2015 baseline represents a standard 35-year World Meteorological Organization (WMO) climate normal.

```python
adm2 = gpd.read_file(RAW / "geo" / "zwe_adm2_geoboundaries.geojson")[["shapeName", "geometry"]]
adm2 = adm2.rename(columns={"shapeName": "district"}).set_crs(4326, allow_override=True)
```
*Why:* Administrative boundary shapefiles from geoBoundaries (Admin-2 / District level) were ingested and explicitly set to EPSG:4326 (WGS84) to match the coordinate reference system of CHIRPS.

```python
lon2d, lat2d = np.meshgrid(lons, lats)
pts = gpd.GeoDataFrame(
    {"flat": np.arange(nlat * nlon)},
    geometry=[Point(x, y) for x, y in zip(lon2d.ravel(), lat2d.ravel())],
    crs=4326,
)
joined = gpd.sjoin(pts, adm2, how="left", predicate="within")[["flat", "district"]]
joined = joined.drop_duplicates("flat")
pix_district = joined["district"].to_numpy()
```
*Why:* I converted the 2D raster grid into explicit centroid coordinates and performed a point-in-polygon spatial join (`predicate="within"`). This maps each $0.05^\circ \times 0.05^\circ$ pixel (approximately $5.5\text{ km} \times 5.5\text{ km}$) directly to its containing district. Pixels falling outside Zimbabwe's borders are filtered out.

```python
districts = sorted(pd.unique(pix_district[pd.notna(pix_district)]))
out = np.full((len(times), len(districts)), np.nan)
for j, d in enumerate(districts):
    mask = pix_district == d
    block = arr[:, mask]
    with np.errstate(invalid="ignore"):
        out[:, j] = np.nanmean(block, axis=1)
```
*Why:* For each district, all enclosed grid cells are averaged (`nanmean`) across time. This creates an area-weighted zonal mean precipitation series $R_{d,t}$ for every district-month.

```python
# Fixed climatology 1981-2015 by district x calendar month
cl = long[(long["month"] >= CLIM_START) & (long["month"] <= CLIM_END)].copy()
cl["cal_month"] = cl["month"].dt.month
clim = cl.groupby(["district", "cal_month"])["rainfall_mm"].agg(["mean", "std", "count"]).reset_index()
clim.columns = ["district", "cal_month", "clim_mean_mm", "clim_sd_mm", "clim_n"]

# Standardised anomalies
full = long.merge(clim[["district", "cal_month", "clim_mean_mm", "clim_sd_mm"]],
                  on=["district", "cal_month"], how="left")
full["rainfall_anom_z"] = (full["rainfall_mm"] - full["clim_mean_mm"]) / full["clim_sd_mm"]
```
*Why & Mathematical Formula:* To account for strong seasonal precipitation cycles in Southern Africa (rainy season from November to March; dry winter from May to August), I computed month-of-year specific climatological means $\mu_{d,m}$ and standard deviations $\sigma_{d,m}$ over the fixed 1981–2015 historical baseline:

$$\mu_{d,m} = \frac{1}{N_{d,m}} \sum_{y=1981}^{2015} R_{d,y,m}, \quad \sigma_{d,m} = \sqrt{\frac{1}{N_{d,m}-1} \sum_{y=1981}^{2015} (R_{d,y,m} - \mu_{d,m})^2}$$

The standardized rainfall anomaly Z-score for district $d$ in calendar month $m$ of year $t$ is formulated as:

$$Z_{d,t,m}^{\text{rain}} = \frac{R_{d,t,m} - \mu_{d,m}}{\sigma_{d,m}}$$

This isolates true meteorological drought ($Z < -1.0$) or excess precipitation ($Z > +1.0$) from normal seasonal periodicity.

---

### 3.2 Dataset Assembly, Integration & Feature Engineering (`src/build_dataset.py`)

This script combines humanitarian market price records with climate anomalies and population counts, filters unrepresentative records, aggregates multiple quotes into monthly medians, and computes features and target labels.

#### Code Walkthrough & Design Decisions

```python
def build_crosswalk(price_markets: pd.DataFrame) -> pd.DataFrame:
    # Point-in-polygon matching of reported market GPS coordinates
    pts = gpd.GeoDataFrame(
        m[has_xy].copy(),
        geometry=[Point(x, y) for x, y in zip(m.loc[has_xy, "longitude"], m.loc[has_xy, "latitude"])],
        crs=4326,
    )
    j2 = gpd.sjoin(pts, adm2, how="left", predicate="within").drop(columns="index_right")
    ...
    # Validation check between reported text admin2 and spatial boundary polygon
    rep = m["admin2"].fillna("").str.lower().str.strip()
    geo = m["district_geo"].fillna("").str.lower().str.strip()
    m["district_name_match"] = (rep == geo) & (rep != "")
    return m.reset_index(drop=True)
```
*Why:* WFP market tables often contain typographical discrepancies in administrative names. Rather than relying on text strings, I used the verified GPS coordinates of each market to perform a spatial join against geoBoundaries polygons. I retained `district_name_match` to audit alignment. For markets lacking coordinates, rather than guessing coordinates, they are kept unassigned to prevent spurious climate joins.

```python
# Monthly aggregation per market, commodity, currency
key = ["market_id", "commodity_id", "currency", "month"]
panel = (prices.groupby(key, dropna=False)
         .agg(price=("price", "median"), usdprice=("usdprice", "median"),
              n_records=("price", "size"),
              unit=("unit", lambda s: s.mode().iat[0]),
              category=("category", lambda s: s.mode().iat[0]),
              admin1=("admin1", "last"), admin2=("admin2", "last"),
              priceflag_any_aggregate=("priceflag", lambda s: bool((s == "aggregate").any())))
         .reset_index())
```
*Why:* High-frequency price surveys often report multiple transactions in a single month or week. Calculating the monthly median eliminates intra-month quote noise, minimizes the effect of recording errors, and establishes an evenly spaced panel unit for time-series modeling.

---

### 3.3 Mathematical Formulation of Targets

#### Target Y1: Standardised Trailing Return Stress

```python
# Return calculation with strict monthly continuity check
r = np.log(g[value_col]).diff()
gap = (m - m.shift(1)).dt.days
r = r.where(gap.between(28, 31))

# Trailing baseline strictly using prior information (window = 12 months, min 6 returns)
mu_cur = r.rolling(win, min_periods=minp).mean()
sd_cur = r.rolling(win, min_periods=minp).std()

# Forward 1-month return standardisation
next_r = r.shift(-1).where((m.shift(-1) - m).dt.days.between(28, 31))
z_next = (next_r - mu_cur) / sd_cur

# Binary classification label
y1 = np.where(z_next.notna(), (z_next >= thr).astype(float), np.nan)
```

**Econometric Justification & Math:**  
Let $P_{i,t}$ denote the monthly median price of commodity $c$ in market $m$ in currency $k$ at month $t$. The month-over-month logarithmic return is defined as:

$$r_{i,t} = \ln(P_{i,t}) - \ln(P_{i,t-1})$$

A continuity constraint is enforced: $r_{i,t}$ is valid if and only if $\Delta t = \text{Date}_t - \text{Date}_{t-1} \in [28, 31]\text{ days}$. If a market survey was missed, the subsequent return across multi-month gaps is set to `NaN` to prevent attributing 3-month inflation surges to a single monthly step.

The trailing baseline mean $\mu_{i,t}$ and sample standard deviation $\sigma_{i,t}$ are computed over a 12-month rolling window up to and including month $t$:

$$\mu_{i,t} = \frac{1}{K_t} \sum_{s=0}^{W-1} r_{i,t-s}, \quad \sigma_{i,t} = \sqrt{\frac{1}{K_t - 1} \sum_{s=0}^{W-1} (r_{i,t-s} - \mu_{i,t})^2}$$

where $W = 12$ and $K_t \ge 6$ (minimum of 6 valid historical observations). The forward standardized return Z-score is:

$$Z_{i,t+1} = \frac{r_{i,t+1} - \mu_{i,t}}{\sigma_{i,t}}$$

The binary target variable $Y1_{i,t}$ indicates whether the commodity experiences an abnormal upward price acceleration exceeding 1.0 historical standard deviation:

$$Y1_{i,t} = \begin{cases} 1, & \text{if } Z_{i,t+1} \ge 1.0 \text{ and } \sigma_{i,t} > 0 \\ 0, & \text{if } Z_{i,t+1} < 1.0 \text{ and } \sigma_{i,t} > 0 \\ \text{NaN}, & \text{otherwise} \end{cases}$$

#### Target Y2: Spatial Peer-Relative Price Stress (Spatial Price Index)

```python
# Peer group: contemporaneous median across all markets for commodity c and currency k
grp = ["commodity_id", "currency", "month"]
peer = df.groupby(grp)[value_col].agg(peer_median="median", peer_count="size").reset_index()
df = df.merge(peer, on=grp, how="left")

# Spatial Price Index (SPI)
df["spi"] = df[value_col] / df["peer_median"]
df.loc[df["peer_count"] < int(tp["min_peer_markets"]), "spi"] = np.nan

# Forward 1-month peer stress label (SPI >= 1.20)
next_spi = g["spi"].shift(-1).where((m.shift(-1) - m).dt.days.between(28, 31))
y2 = np.where(next_spi.notna(), (next_spi >= float(tp["threshold_spi"])).astype(float), np.nan)
```

**Spatial Economics Justification & Math:**  
In hyperinflationary and dual-currency regimes, nominal price changes are frequently dominated by macro-monetary depreciation rather than localized supply failure. Target $Y2$ isolates geographic market failure by measuring whether a market charges a substantial premium relative to its contemporaneous national peers.

For commodity $c$ and currency $k$ in month $t$, let $\mathcal{M}_{c,k,t}$ represent the set of reporting markets. The national peer median price is:

$$M_{c,k,t} = \text{median}_{j \in \mathcal{M}_{c,k,t}} (P_{j,c,k,t})$$

The Spatial Price Index ($SPI_{i,t}$) for market $i$ is:

$$SPI_{i,t} = \frac{P_{i,t}}{M_{c,k,t}}, \quad \text{defined only when } |\mathcal{M}_{c,k,t}| \ge 5$$

If fewer than 5 markets reported quotes for that commodity-currency pair in month $t$, the SPI is undefined (`NaN`) to prevent noise from small sample sizes.

The forward binary target $Y2_{i,t}$ flags whether market $i$ will experience severe relative price stress (selling at $\ge 20\%$ above the national median) in month $t+1$:

$$Y2_{i,t} = \begin{cases} 1, & \text{if } SPI_{i,t+1} \ge 1.20 \\ 0, & \text{if } SPI_{i,t+1} < 1.20 \\ \text{NaN}, & \text{otherwise} \end{cases}$$

---

### 3.4 Feature Engineering Matrix

The feature vector $X_{i,t} \in \mathbb{R}^{17}$ constructed for predicting $Y_{i,t}$ consists of 15 numerical features and 2 categorical features:

| Feature Name | Type | Description | Theoretical Rationale |
| :--- | :--- | :--- | :--- |
| `ret_z_cur` | Continuous | Standardised log-return at month $t$: $(r_t - \mu_{t-1})/\sigma_{t-1}$ | Captures existing price momentum prior to prediction |
| `ret_lag1` | Continuous | 1-month lagged logarithmic return ($r_{t-1}$) | Short-term temporal autocorrelation |
| `ret_lag2` | Continuous | 2-month lagged logarithmic return ($r_{t-2}$) | Second-order price momentum |
| `ret_roll3` | Continuous | 3-month rolling mean logarithmic return | Medium-term inflationary drift |
| `spi` | Continuous | Current Spatial Price Index ($P_{i,t} / M_{c,k,t}$) | Measures existing spatial price premium |
| `peer_count` | Discrete | Number of markets reporting commodity in month $t$ | Proxy for national market integration / liquidity |
| `rain_anom_z` | Continuous | Contemporary district rainfall anomaly Z-score | Immediate drought or flood shock |
| `rain_anom_lag1` | Continuous | 1-month lagged district rainfall anomaly Z-score | Short-term hydrological lag |
| `rain_anom_lag2` | Continuous | 2-month lagged district rainfall anomaly Z-score | Crop vegetative development lag |
| `rain_anom_lag3` | Continuous | 3-month lagged district rainfall anomaly Z-score | Harvest-to-market supply delay |
| `rain_roll3_mm` | Continuous | 3-month cumulative rainfall total (mm) | Absolute soil moisture and agricultural adequacy |
| `month_sin` | Continuous | $\sin(2\pi \cdot \text{month} / 12)$ | Captures periodic intra-annual agricultural seasonality |
| `month_cos` | Continuous | $\cos(2\pi \cdot \text{month} / 12)$ | Cyclical component of lean season vs harvest season |
| `log_population` | Continuous | $\ln(\text{District Population})$ from 2023 HDX census | Market demand scale and urbanisation density |
| `interaction` | Continuous | $ret\_z\_cur \times rain\_anom\_z$ | Non-linear interaction: price acceleration compound with drought |
| `category` | Categorical | Commodity group (Cereals, Pulses, Oil/Fats, Meat/Fish, Misc) | Food-group specific demand elasticity and storability |
| `currency` | Categorical | Denomination currency (USD, ZWL, ZWG, etc.) | Monetary regime and currency volatility fixed effects |

---

### 3.5 Model Zoo and Validation Architecture (`src/train.py`)

#### Preprocessing Pipeline
```python
pre = ColumnTransformer([
    ("num", Pipeline([("imp", SimpleImputer(strategy="median")),
                      ("sc", StandardScaler())]), NUM),
    ("cat", Pipeline([("imp", SimpleImputer(strategy="most_frequent")),
                      ("oh", OneHotEncoder(handle_unknown="ignore"))]), CAT),
])
```
*Why:* Missing values are imputed using the training median (for continuous variables) and most frequent value (for categorical variables). Imputers are fitted strictly on the training partition within each fold, then applied to the validation/holdout sets. `OneHotEncoder(handle_unknown="ignore")` ensures that unseen currencies or categories appearing in later periods do not raise execution exceptions.

#### Chronological Expanding Window Cross-Validation
```python
def chrono_folds(months, n_folds, holdout_n):
    months = list(months)
    holdout = set(months[-holdout_n:]) if holdout_n > 0 else set()
    pre = months[:-holdout_n] if holdout_n > 0 else months
    n_folds = max(1, min(n_folds, len(pre) - 1))
    edges = np.linspace(0, len(pre), n_folds + 1).astype(int)
    folds = []
    for i in range(1, n_folds + 1):
        vstart, vend = edges[i - 1], edges[i]
        val = set(pre[vstart:vend])
        train = set(pre[:vstart])
        if train and val:
            folds.append((train, val))
    return folds, holdout
```
*Why:* In observational panel time series, random K-fold shuffling is strictly invalid because training on future observations to predict the past violates the temporal causal arrow and produces overoptimistic error metrics. I implemented a 5-fold expanding window:
- Fold 1: Train on interval $[T_0, T_1)$, validate on $[T_1, T_2)$.
- Fold 2: Train on interval $[T_0, T_2)$, validate on $[T_2, T_3)$.
- ...
- Fold 5: Train on interval $[T_0, T_5)$, validate on $[T_5, T_6)$.
- Final Out-of-Sample Holdout: The final 12 contiguous calendar months are set aside and remain untouched during cross-validation, feature tuning, and threshold selection.

#### Model Zoo Specifications
1. **Majority Classifier Baseline (`DummyClassifier`):** Predicts the marginal empirical class prevalence. Establishes the floor ROC-AUC ($0.50$).
2. **Persistence Rule Baseline:** Formulates a heuristic rule where the current stress state is projected directly into the next month.
3. **Regularized Logistic Regression (ElasticNet):**
   ```python
   LogisticRegression(solver="saga", l1_ratio=0.5, C=1.0, max_iter=10000, tol=1e-3,
                      class_weight="balanced", random_state=SEED)
   ```
   Provides a linear, interpretable parametric benchmark with balanced class weighting.
4. **Histogram-Based Gradient Boosting (`HistGradientBoostingClassifier`):**
   ```python
   HistGradientBoostingClassifier(learning_rate=0.05, max_iter=300, max_leaf_nodes=15,
                                  min_samples_leaf=30, l2_regularization=1.0, random_state=SEED)
   ```
   Constructs non-linear decision trees using histogram binning, suited for capturing non-linear threshold responses between rainfall anomalies and commodity prices.
5. **Extreme Gradient Boosting (`XGBClassifier`):**
   ```python
   XGBClassifier(n_estimators=300, learning_rate=0.05, max_depth=4, subsample=0.8,
                 colsample_bytree=0.8, reg_lambda=1.0, scale_pos_weight=pos_weight,
                 random_state=SEED, eval_metric="logloss")
   ```
   Implements tree-level stochastic subsampling and exact Hessian regularization with class imbalance compensation (`scale_pos_weight`).

#### Decision Threshold Optimization
```python
def best_threshold(y, p):
    cands = np.linspace(0.02, 0.98, 97)
    best, bt = -1, 0.5
    for t in cands:
        f = f1_score(y, (p >= t).astype(int), zero_division=0)
        if f > best:
            best, bt = f, t
    return bt
```
*Why:* Due to class imbalance, the standard default probability threshold $\tau = 0.50$ is severely suboptimal. I searched across 97 candidates $\tau \in [0.02, 0.98]$ on out-of-fold validation predictions to select the threshold $\tau^*$ that maximizes the F1-score:

$$\tau^* = \arg\max_{\tau \in [0.02, 0.98]} F1(y_{\text{val}}, \mathbb{I}(P_{\text{val}} \ge \tau))$$

This calibrated threshold is then evaluated on the forward holdout without further tuning.

---

### 3.6 Bayesian Hyperparameter Optimization (`src/tune_optuna.py`)

To optimize the histogram gradient boosting architecture, I deployed Optuna's Tree-structured Parzen Estimator (TPE) algorithm.

```python
def suggest_hgb(trial):
    return {
        "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.30, log=True),
        "max_iter": trial.suggest_int("max_iter", 100, 500, step=50),
        "max_leaf_nodes": trial.suggest_int("max_leaf_nodes", 7, 63),
        "min_samples_leaf": trial.suggest_int("min_samples_leaf", 10, 60),
        "l2_regularization": trial.suggest_float("l2_regularization", 1e-3, 10.0, log=True),
        "max_bins": trial.suggest_categorical("max_bins", [128, 255]),
    }
```
*Why:* Optimization was conducted over 40 trials per task. The objective function evaluated the unweighted mean validation ROC-AUC across the 5 expanding window training folds. The forward holdout remained unseen during this procedure to avoid data snooping.

---

### 3.7 Statistical Inference and Robustness Framework (`src/analysis.py` & `src/robustness.py`)

#### Lead-Lag Meteorological Correlation
```python
for lag, col in [(0, "rain_anom_z"), (1, "rain_anom_lag1"), (2, "rain_anom_lag2"), (3, "rain_anom_lag3")]:
    sub = df[[col, "ret"]].replace([np.inf, -np.inf], np.nan).dropna()
    r, p = stats.pearsonr(sub[col], sub["ret"])
    rs, ps = stats.spearmanr(sub[col], sub["ret"])
```
*Why:* I evaluated both linear (Pearson $r$) and monotonic non-linear (Spearman $\rho$) correlations across varying monthly lags ($\ell \in \{0, 1, 2, 3\}$). This tests whether precipitation deficits propagate into food price increases over a multi-month agrarian cycle.

#### Permutation Feature Importance
```python
r = permutation_importance(pipe, Xf[ho], yv[ho], scoring="roc_auc", n_repeats=20, random_state=SEED)
```
*Why:* Unlike tree impurity-based importance, permutation importance directly measures the drop in out-of-sample ROC-AUC when a feature column is randomly shuffled. A feature that yields zero or negative importance upon shuffling has no generalizable predictive utility.

#### Clustered Bootstrap Confidence Intervals
```python
# Clustered resampling by market to respect spatial correlation
markets = df["market_id"].unique()
boot_aucs = []
for _ in range(n_boot):
    sample_mkts = RNG.choice(markets, size=len(markets), replace=True)
    sample_df = pd.concat([df[df["market_id"] == m] for m in sample_mkts])
    ...
```
*Why:* Standard independent and identically distributed (i.i.d.) bootstrapping underestimates variance when observations are spatially clustered within physical markets. Resampling entire market clusters preserves intra-market residual dependence and provides valid 95% confidence intervals.
