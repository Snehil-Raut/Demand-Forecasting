# Data Contract — demand_forecast (M5, CA × FOODS)

**Version:** 1.0
**Source of decisions:** `notebooks/01_data_audit.ipynb`

## 1. Sources (read-only, `data/raw/`)
| File | Grain | Key | Used |
|---|---|---|---|
| `sales_train_evaluation.csv` | 1 row per item-store, wide (d_1..d_1941) | `id` | Yes |
| `calendar.csv` | 1 row per day (d_1..d_1969) | `d` | Yes |
| `sell_prices.csv` | 1 row per item-store-week | `store_id`, `item_id`, `wm_yr_wk` | Yes |
| `sales_train_validation.csv`, `sample_submission.csv` | — | — | No |

**Scope** (from `config.yaml`): state = CA (CA_1–CA_4), category = FOODS.

## 2. Interim table (`data/interim/`, Parquet)
Grain: **1 row per item-store-day**. Key: **`id` + `date`** (unique).
Expected rows: 5,748 series × 1,941 days = **11,156,868**.

| Column | Type | Rule |
|---|---|---|
| id | string | Not null |
| item_id, dept_id, cat_id, store_id, state_id | string | Not null; cat_id = FOODS, state_id = CA |
| d | string | d_1..d_1941 |
| date | date | 2011-01-29 → 2016-05-22, no gaps |
| wm_yr_wk | int | Not null |
| weekday, wday, month, year | string/int | Not null |
| event_name_1/2, event_type_1/2 | string | Null = no event |
| snap_CA | int | 0 or 1 |
| sales | int | ≥ 0, not null |
| sell_price | float | > 0; null allowed **only before first sale** |

## 3. Validation rules (checked in code, pipeline stops if broken)
1. No duplicate `id` + `date`.
2. Row count = series × days.
3. `sales` ≥ 0 and not null.
4. Dates are continuous (every step = 1 day).
5. After a series' first sale, `sell_price` is never null.
6. Only stores/categories in `config.yaml` are present.

## 4. Cleaning rules (applied in step 4, `src/clean.py`)
| # | Rule | Status | Evidence |
|---|---|---|---|
| 7 | Drop each series' days before its first sale | DECIDED | 38% of all zeros are pre-launch |
| 8 | No price filling | DECIDED | Prices always present after launch |
| 9 | Keep all history (2011–2016) | DECIDED | Products launch every year |
| — | Christmas (25 Dec, stores closed) | OPEN (step 4) | 5 days with near-zero total sales |
| — | Unusual spikes | OPEN (step 4) | e.g. FOODS_3_785_CA_1: 648 vs avg 13.5 |

## 5. Holdout
Days **d_1914–d_1941** are the final test set. Never used for training, tuning or feature choices.

## 6. Future days
Calendar d_1942–d_1969 has no sales. Used only to build features for the 28-day forecast.

## 7. Change log
| Version | Date | Change |
|---|---|---|
| 1.0 | 2026-11-14 | First version from data audit |
