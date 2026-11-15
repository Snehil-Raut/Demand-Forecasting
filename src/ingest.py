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
    assert not ((df["sales"].isna()) | (df["sales"] < 0)).any(), ("Sales contain null or negative values!")
 


if __name__ == "__main__":
    cfg = load_config()
    sales, calendar, prices   = load_raw(cfg)
    sales_scope, prices_scope = filter_scope(sales, prices, cfg)
    long                      = to_long(sales_scope)
    merged                    = add_calendar(long, calendar, cfg)
    df                        = add_prices(merged, prices_scope)
    validates                 = validate(df, cfg)        
    print(sales.shape, calendar.shape, prices.shape)
    print(sales_scope.shape, prices_scope.shape)
    print(long.shape)
    print(merged.shape)
    print(df.shape)