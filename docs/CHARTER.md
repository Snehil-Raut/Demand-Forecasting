# Project Charter — Walmart Demand Forecasting (M5)

**Owner / decision-maker:** Ankita  
**Status:** FINAL (v1)  
**Last updated:** 2026-11-10

## 1. Problem
Store managers must decide how many units of each food item to stock. Ordering too
little causes empty shelves and lost sales; ordering too much ties up money and,
for food, leads to waste. Today this is guesswork. This system forecasts daily
demand per item and store so managers can stock the right amount.

## 2. User and business decision
- **Primary user:** store manager
- **Decision supported:** how many units of each item to stock for the next 28 days
- **Secondary user:** admin / HQ planner (views all stores, monitors model accuracy)

## 3. Scope (decided)
- **Data:** Kaggle M5 Forecasting – Accuracy (Walmart, 2011–2016)
- **Stores:** California only: CA_1, CA_2, CA_3, CA_4
- **Category:** FOODS only (FOODS_1, FOODS_2, FOODS_3): about 1,437 items × 4 stores ≈ 5,700 series
- Built so more states and categories can be added later through `config.yaml`

## 4. Forecast definition (decided)
- **Target:** units sold
- **Granularity:** per item, per store, per day
- **Horizon:** next 28 days

## 5. Run cadence
- M5 is a fixed dataset, so the system simulates a live feed: the last weeks of
  data are held back and fed in one day at a time.
- New sales data loaded **daily**; forecasts refreshed **daily**; model retrained **weekly**.

## 6. Success metrics
Models are chosen by ONE primary metric; the others are tracked to catch problems
and explain results.

| Type | Metric | Target |
|---|---|---|
| Primary (model) | WRMSSE (official M5 metric) on the final holdout | Beat the seasonal naive baseline by at least **15%** |
| Secondary (model) | Bias: total forecast vs total actual (%) | Within ±5% |
| Secondary (model) | MAE per item (units per day) | Lower than baseline |
| Business | Under-stocked units (actual > forecast) and over-stocked units (forecast > actual) | Both lower than baseline |
| Product | Daily pipeline runs without failure; API response time | No failed runs; < 1 second |

- **Final holdout:** last 28 days (d_1914–d_1941), never used during development.
- **Baseline:** seasonal naive (repeat the last 28 days / same weekday last week).
- **Product done:** a store manager can log in on the live AWS site and see a
  28-day restock list and forecast-vs-actual charts.

## 7. Constraints
- **Timeline:** 6–8 weeks part-time
- **Team:** Ankita
- **AWS budget:** free tier, max ~$20/month
- **Machine:** local Windows laptop for development

## 8. Out of scope
- Real-time point-of-sale data
- Supplier lead times, minimum order sizes, safety-stock optimization
- Stores outside CA and categories other than FOODS (for version 1)
- Price optimization or promotion planning

## 9. Risks
- Many items sell rarely (lots of zero days), so they are hard to forecast.
- Pre-launch zeros and missing prices can mislead the model if not handled.
- Old data (2011–2016) means there is no truly live feed; the feed is simulated.