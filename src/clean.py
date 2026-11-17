import pandas as pd
from src.ingest import ROOT, load_config
import numpy as np

def load_interim(cfg):
    path = ROOT / cfg["paths"]["interim"] / "sales_long.parquet"
    return pd.read_parquet(path)

# removing the fake 0's which are present in the table even before the launch of product
def drop_pre_launch(df):
    sales_rows = df[df['sales'] > 0]
    first_selling = sales_rows.groupby('id')['date'].min()
    launch = df['id'].map(first_selling)
    after  = df['date'] >= launch

    return df[after].copy()

# Adding CLOSE flag on Christmas days , as store was closed on that day -- so 0 means on that day = close store
def add_close_flag(df):
    df['is_closed'] = np.where((df['date'].dt.month == 12) & (df['date'].dt.day == 25), 1,0)
    return df

# Save the clean file
def save_clean(df, cfg):
    df = df.sort_values(["id", "date"]).reset_index(drop=True)
    out_path = ROOT / cfg["paths"]["interim"] / "sales_clean.parquet"
    df.to_parquet(out_path, index=False)
    print(f"Saved {len(df):,} rows to {out_path}")


if __name__ == "__main__":
    cfg = load_config()
    df  = load_interim(cfg)
    df  = drop_pre_launch(df)
    df = add_close_flag(df)
    save_clean(df,cfg)
