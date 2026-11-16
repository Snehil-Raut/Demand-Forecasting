from pathlib import Path
import yaml
import pandas as pd

ROOT = Path(__file__).resolve().parents[1] # project root (src/ → root)

def load_config():
    with open(ROOT / "config.yaml") as f:
        return yaml.safe_load(f)

def load_raw(cfg):
    raw      = ROOT / cfg["paths"]["raw"]
    sales    = pd.read_csv(raw / "sales_train_evaluation.csv")
    calendar = pd.read_csv(raw / "calendar.csv")
    prices   = pd.read_csv(raw / "sell_prices.csv")
    return sales, calendar, prices

def filter_scope(sales, prices, cfg):
    sales_scope     = sales[(sales['state_id']==cfg["state"]) &  (sales["cat_id"]==cfg["category"])].copy()
    unique_pairs    = sales_scope[['store_id', 'item_id']].drop_duplicates()
    prices_scope    = pd.merge(prices, unique_pairs, on=['store_id', 'item_id'])
    return sales_scope, prices_scope

# reshape from wide to long.
def to_long(sales_scope):
    id_cols = ["id", "item_id", "dept_id", "cat_id", "store_id", "state_id"]
    long    = sales_scope.melt(id_vars=id_cols, var_name='d', value_name='sales')
    return long

def add_calendar(long, calendar, cfg):
    calendar = calendar.copy()
    calendar['date'] = pd.to_datetime(calendar['date'])
    merged    = pd.merge(long, calendar, on='d', how='left')
    keep      = "snap_" + cfg["state"]
    drop_cols = [c for c in merged.columns if c.startswith("snap_") and c != keep]
    merged    = merged.drop(columns=drop_cols)
    
    return merged

def add_prices(merged, prices_scope):
    df = pd.merge(merged, prices_scope, on=['store_id', 'item_id', 'wm_yr_wk'], how='left')
    return df

def validate(df, cfg):
    assert not df.duplicated(subset=['id', 'date']).any(), "Duplicate pairs found!" 
    n_series = df['id'].nunique()
    n_days   = df['d'].nunique()
    assert len(df) == n_series * n_days, "Row count mismatch!"
    assert not ((df['sales'].isna()) | (df['sales'] < 0)).any(), ("Sales contain null or negative values!")
    days_expected = (df['date'].max() - df['date'].min()).days + 1
    days_actual = df["date"].nunique()
    assert days_actual  == days_expected, 'Missing dates found!'
    assert list(df['state_id'].unique()) == [cfg['state']], "Wrong state found!"
    assert list(df['cat_id'].unique()) == [cfg['category']], "Wrong category found!"

    sold_rows  = df[df['sales'] > 0]
    first_date = sold_rows.groupby('id')['date'].min()
    launch = df['id'].map(first_date)
    after  = df['date'] >= launch
    assert not df.loc[after, "sell_price"].isna().any(), "Missing price after launch!"
    print("All checks passed")

def save(df, cfg):
    out_dir = ROOT / cfg["paths"]["interim"]
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "sales_long.parquet"
    df.to_parquet(out_path, index=False)
    print(f"Saved {len(df):,} rows to {out_path}")

if __name__ == "__main__":
    cfg = load_config()
    sales, calendar, prices   = load_raw(cfg)
    sales_scope, prices_scope = filter_scope(sales, prices, cfg)
    long                      = to_long(sales_scope)
    merged                    = add_calendar(long, calendar, cfg)
    df                        = add_prices(merged, prices_scope)

    validate(df, cfg)
    save(df, cfg)