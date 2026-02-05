import pandas as pd
import matplotlib.pyplot as plt


def load_and_process_data(file_path):
    """Load and preprocess the sales data."""
    df = pd.read_csv(file_path, low_memory=False)
    
    # Standardize column names
    df.columns = df.columns.str.strip().str.lower()
    
    # Map common column variations to standard names
    column_mapping = {
        'order date': 'date',
        'sales': 'amount',
        'product': 'product_name',
        'customer name': 'cashier'
    }
    df.rename(columns=column_mapping, inplace=True)
    
    # Ensure required columns exist
    if 'date' not in df.columns:
        raise ValueError("CSV must contain a 'date' or 'order date' column")
    if 'amount' not in df.columns:
        raise ValueError("CSV must contain an 'amount' or 'sales' column")
    if 'product_name' not in df.columns:
        raise ValueError("CSV must contain a 'product_name' or 'product' column")
    
    # Convert date
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    
    # Clean and convert numeric columns (remove $ signs)
    numeric_cols = ["quantity", "amount", "discount"]
    for col in numeric_cols:
        if col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].str.replace('$', '', regex=False).str.strip()
            df[col] = pd.to_numeric(df[col], errors="coerce")
    
    # Handle missing values
    if "discount" not in df.columns:
        df["discount"] = 0
    df["discount"] = df["discount"].fillna(0)
    
    if "cashier" not in df.columns:
        df["cashier"] = "Unknown"
    df["cashier"] = df["cashier"].fillna("Unknown")
    
    if "quantity" not in df.columns:
        df["quantity"] = 1
    df["quantity"] = df["quantity"].fillna(1)
    
    df = df.dropna(subset=["date", "product_name", "amount"])
    
    # Remove duplicates
    df = df.drop_duplicates()
    
    # Create useful derived columns
    df["net_amount"] = df["amount"] - df["discount"]
    df["day"] = df["date"].dt.date
    
    return df


def analyze(df):
    return {
        "daily_sales": df.groupby("day")["net_amount"].sum(),
        "top_products": df.groupby("product_name")["quantity"].sum().sort_values(ascending=False).head(10),
        "cashier_sales": df.groupby("cashier")["net_amount"].sum(),
        "discounts": df.groupby("product_name")["discount"].sum()
    }
def serialize(series):
    def to_json_value(x):
        if hasattr(x, "item"):
            return x.item()
        if hasattr(x, "__float__"):
            return float(x)
        return x

    return {
        "labels": [str(x) for x in series.index.tolist()],
        "values": [to_json_value(x) for x in series.values.tolist()]
    }
def get_dashboard_data(file_path):
    df = load_and_process_data(file_path)
    results = analyze(df)

    return {
        "daily_sales": serialize(results["daily_sales"]),
        "top_products": serialize(results["top_products"]),
        "cashier_sales": serialize(results["cashier_sales"]),
        "discounts": serialize(results["discounts"])
    }


if __name__ == "__main__":
    df = load_and_process_data("data/Data_test.csv")
