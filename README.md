<h1 align="center">Walmart Demand Forecasting: 28-Day Restock Planner</h1>

<p align="center">
  Forecasts daily sales for <b>5,748 Walmart item-store pairs</b> over the next <b>28 days</b>,<br>
  so store managers know exactly how much of each food item to stock.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.11%2B-3776AB?logo=python&logoColor=white" alt="python">
  <img src="https://img.shields.io/badge/pandas-3.x-150458?logo=pandas&logoColor=white" alt="pandas">
  <img src="https://img.shields.io/badge/data-Walmart%20M5-0071CE" alt="data">
  <img src="https://img.shields.io/badge/status-in%20progress-orange" alt="status">
</p>

---

## The problem

Order too little and shelves go empty; order too much and food goes to waste. Today, store managers guess. This project replaces the guess with a forecast and a **28-day restock list**, built as an end-to-end product: data pipeline → model → API → web app.

## How it works

```
Kaggle M5 data ─► ingest.py ─► clean.py ─► features + model ─► PostgreSQL + FastAPI ─► Web app on AWS
                  validate      fix fake      (next)              (planned)               (planned)
                  every rule    zeros
```

## Highlights

- **Found that 38% of the "zero sales" days were fake.** Those days came before the product was even on the shelf, so they don't mean "no demand". Keeping them would teach the model to under-forecast, so they are removed per product.
- **The pipeline stops if the data is bad.** Six rules from a written [data contract](docs/data_contract.md) (no duplicates, no missing dates, no negative sales, prices present after launch, and more) are checked in code on every run.
- **Scope lives in config.** The project starts with California × FOODS. Adding a state or category is a one-line change in `config.yaml`, with no code changes.
- **There's a clear bar to beat.** The model has to beat a seasonal-naive baseline by **at least 15% on WRMSSE** (the official M5 metric) on a 28-day holdout it never sees during development.

## Scope

| Data | Stores | Items | Series | History | Horizon |
|---|---|---|---|---|---|
| Walmart M5 (Kaggle) | 4 in California | 1,437 FOODS | 5,748 | 2011 – 2016 | 28 days |

## Tech stack

**Now:** Python · pandas · NumPy · PyArrow (Parquet) · PyYAML · Jupyter
**Next:** ML forecasting model · PostgreSQL · FastAPI · frontend · AWS

## Status

- [x] Project charter, data audit, data contract
- [x] Validated ingest and cleaning pipeline
- [ ] Features, baseline and model
- [ ] Database, API and frontend
- [ ] Deployment on AWS

## Quickstart

```bash
pip install -r requirements.txt
kaggle competitions download -c m5-forecasting-accuracy -p data/raw   # then unzip
python -m src.ingest    # raw CSVs → validated data/interim/sales_long.parquet
python -m src.clean     # → data/interim/sales_clean.parquet
```

## Learn more

| Doc | What's inside |
|---|---|
| [`docs/CHARTER.md`](docs/CHARTER.md) | Users, business decision, success metrics, constraints |
| [`docs/data_contract.md`](docs/data_contract.md) | Schema, validation rules, cleaning rules, holdout |
| [`notebooks/01_data_audit.ipynb`](notebooks/01_data_audit.ipynb) | How each data decision was made |

---

<p align="center">Built by <b>Snehil Raut</b> · <a href="https://www.kaggle.com/competitions/m5-forecasting-accuracy">M5 Forecasting – Accuracy</a></p>