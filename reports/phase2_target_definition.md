# Phase 2 — Research Problem and Target Definition

This document fixes the measurable definition of **food price stress** before any
model is trained. It is grounded in what the Phase 1 data inspection proved is
feasible. Confirmed decisions (user): (D1) analyse **within-currency nominal** and
**`usdprice`-based** series in parallel; (D7) **exclude** `non-food`; (D5) primary
threshold = **standardised next-month log return ≥ +1 SD**.

> Literature citations are intentionally **not fabricated** here. Statements that
> would normally carry a citation are marked **[cite required — Phase 9]** and must
> be backed by a real, read source. No source is cited until it is verified.

---

## 1. Unit of analysis

**Market × commodity × currency × month**, denoted `s = (market_id, commodity_id, currency)`.
Verified feasible: 20,530 food cells; 3,029 series. Also carried: `admin1`, `admin2`
(district), P-code, `category`, `unit`, coordinates.

Two parallel **price bases**, never pooled:
- **B1 — within-currency nominal**: log returns computed inside each `(market, commodity, currency)` series.
- **B2 — `usdprice`**: returns computed on the `usdprice` column, which is currency-comparable.

All modelling and reporting keep B1 and B2 **separate**; their results are never
combined into a single ranking.

## 2. Prediction horizon

One month ahead. Predictors use information available at the end of month `t`;
the label refers to month `t+1`. One-month horizon is chosen because Phase 1 showed
series are short (median 4 months, only 108 series ≥ 24 months) — longer horizons
would leave almost no training data. **[cite required — justify horizon vs early-warning literature]**

## 3. Time-availability rule (leakage prevention)

Each predictor for a row at month `t` is computed **only** from records whose
`month ≤ t`. Specifically:
- Price lags/rolling statistics use months `≤ t` of the same series.
- Standardisation parameters use months `≤ t` (trailing/expanding), never the full sample.
- Peer-market statistics use month `t` only (contemporaneous across markets), never `t+1`.
- Rainfall anomaly uses a **fixed historical climatology (1981–2015)** that predates
  the modelling period; lagged rainfall uses lags ≥ 1 month so the `t+1` weather is unknown.
- The label uses the price at `t+1` and is **never** a predictor.

The prediction is treated as being made at the end of month `t` (price observed on
the 15th; rainfall monthly aggregate assumed available after month end).

## 4. Target 1 (primary): standardised-return stress

For series `s` with price `P_{s,t}` (base B1 or B2):

```
r_{s,t}      = ln(P_{s,t}) - ln(P_{s,t-1})            (monthly log return, computed within base)
μ_{s,t}      = mean( r_{s,k} : months k ≤ t, window of prior returns )
σ_{s,t}      = sd(   r_{s,k} : months k ≤ t )
z_{s,t+1}    = ( r_{s,t+1} - μ_{s,t} ) / σ_{s,t}      (future return, PAST scale)
```

- **Standardisation reference**: trailing window of the **same series**, minimum
  **6 prior returns**, primary window = **12 months** (sensitivity: 6, 18, 24 in Phase 6).
- **Primary threshold τ = +1.0** → `Y1_{s,t} = 1[ z_{s,t+1} ≥ 1.0 ]`.
- Rows with `σ_{s,t}=0` or < 6 prior returns are **unlabelable** and excluded from
  supervised training (report the exact count; do **not** code them as non-stress).

**Positive prediction means:** the model expects this market–commodity–currency
observation to rise unusually fast next month relative to its own recent history.

## 5. Target 2 (secondary): peer-relative price stress (SPI)

Define the peer population for a given month `t` as all eligible markets selling the
**same commodity and same currency** in month `t`, with **≥ 5 peer markets** (sensitivity: 3, 10).

```
SPI_{s,t}   = P_{s,t} / median( P_{peer, t} )
```

- **Label**: `Y2_{s,t} = 1[ SPI_{s,t+1} ≥ δ ]`. Primary **δ = 1.20** (≥ 20% above the
  peer median); sensitivity δ ∈ {1.10, 1.20, 1.30, 1.50} in Phase 6.
- Requires the same commodity/currency to be observed in ≥5 peer markets at `t+1`.

**Positive prediction means:** the market is expected to be priced unusually high
relative to comparable markets next month (a local divergence / spatial stress signal).

Targets 1 and 2 are **reported separately** and never merged into one ranking.

## 6. Standardisation / reference population summary

| Aspect | Target 1 | Target 2 |
|--------|----------|----------|
| Reference | own series' trailing 12-month returns | same commodity+currency, same month, ≥5 markets |
| Scale | trailing mean & SD | peer median |
| Window | ≤ t | month t |
| Leakage guard | minimum 6 prior obs; past-only SD | peer month = t only |

## 7. Base rates (to be computed in Phase 3, not assumed here)

The **actual** prevalence of Y1 and Y2 will be computed on the processed panel and
reported. No base rate is assumed. Phase 1 showed the supervised sub-panel is at most
7,624 labelable cells; expect
base rates to differ from the dissertation's unverified 17.0% / 12.43%.

## 8. Conceptual distinctions (must be stated in the dissertation)

- **Price stress** (this project): an unusually large relative price movement, or a
  large peer-relative divergence, in a market–commodity observation.
- **Price inflation**: a general rise in the price level; not the same as one
  market/commodity spiking, and confounded by currency here. **[cite required]**
- **Price volatility**: the magnitude of price *variation* irrespective of direction;
  this project predicts the **upward** tail, not volatility per se. **[cite required]**
- **Household food insecurity**: a welfare outcome driven by income, assets,
  production, labour, social protection — **not measured or predicted here**. The
  project predicts a **market signal** only. **[cite required]**

## 9. Reference population for standardisation/peer comparison (fixed choices)

- Within-series standardisation uses the series' own trailing history (Target 1).
- Peer standardisation uses same commodity + same currency + same month (Target 2).
- Rainfall anomaly: **district** (admin-2) monthly total standardised against the
  **1981–2015** district calendar-month climatology (fixed, pre-modelling).
- No national-level averaging is used as a substitute for market-level analysis.

## 10. Justification of target choices (data-driven)

- Trailing standardisation is exposed as a standard safeguard against look-ahead bias
  in financial/price forecasting. **[cite required]**
- Peer-relative measures follow spatial-market / price-transmission logic (markets
  sharing a commodity & currency should roughly comove absent local shocks). **[cite required]**
- Two thresholds are kept because the data support **two conceptually different
  questions** (own-history acceleration vs cross-market divergence) and Phase 1 showed
  currency regimes make a single pooled target indefensible.

## 11. What is explicitly *not* claimed

- Predictions are not household food-insecurity classifications.
- A positive label is not proof of scarcity, causation, or famine.
- Model performance is not assumed to be good; if baselines win, that is reported.
- No operational early-warning suitability is claimed without prospective evidence.

## 12. Phase 2 outputs

1. `reports/phase2_target_definition.md` (this file).
2. A `config/targets.yml` capturing thresholds, windows, bases, and peer rules, so the
   pipeline in Phase 3 reads one source of truth.

Next: Phase 3 will implement this definition and report the **actual** label counts.
