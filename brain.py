import pandas as pd
import matplotlib.pyplot as plt
import os


def load_and_process_data(file_path):
    """Load and preprocess the sales data from CSV or Excel files."""
    # Detect file type by extension
    file_extension = os.path.splitext(file_path)[1].lower()
    
    if file_extension == '.csv':
        df = pd.read_csv(file_path, low_memory=False)
    elif file_extension in ['.xlsx', '.xls']:
        df = pd.read_excel(file_path)
    else:
        raise ValueError("File must be CSV or Excel format (.csv, .xlsx, .xls)")
    
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


def compare_files(file_path1, file_path2):
    """Compare two CSV files and return comparison metrics."""
    df1 = load_and_process_data(file_path1)
    df2 = load_and_process_data(file_path2)
    
    results1 = analyze(df1)
    results2 = analyze(df2)
    
    # Calculate totals
    total_sales1 = df1["net_amount"].sum()
    total_sales2 = df2["net_amount"].sum()
    sales_change = total_sales2 - total_sales1
    sales_change_pct = (sales_change / total_sales1 * 100) if total_sales1 > 0 else 0
    
    # Compare top products
    top_products1 = results1["top_products"].head(5)
    top_products2 = results2["top_products"].head(5)
    
    # Compare cashier performance
    cashier_sales1 = results1["cashier_sales"].sort_values(ascending=False).head(5)
    cashier_sales2 = results2["cashier_sales"].sort_values(ascending=False).head(5)
    
    # Date range
    date_range1_start = df1["date"].min().strftime("%Y-%m-%d") if not df1.empty else "N/A"
    date_range1_end = df1["date"].max().strftime("%Y-%m-%d") if not df1.empty else "N/A"
    date_range2_start = df2["date"].min().strftime("%Y-%m-%d") if not df2.empty else "N/A"
    date_range2_end = df2["date"].max().strftime("%Y-%m-%d") if not df2.empty else "N/A"
    
    return {
        "file1": {
            "total_sales": round(total_sales1, 2),
            "total_transactions": len(df1),
            "date_range": f"{date_range1_start} to {date_range1_end}",
            "top_products": serialize(top_products1),
            "top_cashiers": serialize(cashier_sales1),
            "avg_transaction": round(total_sales1 / len(df1) if len(df1) > 0 else 0, 2)
        },
        "file2": {
            "total_sales": round(total_sales2, 2),
            "total_transactions": len(df2),
            "date_range": f"{date_range2_start} to {date_range2_end}",
            "top_products": serialize(top_products2),
            "top_cashiers": serialize(cashier_sales2),
            "avg_transaction": round(total_sales2 / len(df2) if len(df2) > 0 else 0, 2)
        },
        "comparison": {
            "sales_change": round(sales_change, 2),
            "sales_change_pct": round(sales_change_pct, 2),
            "transaction_change": len(df2) - len(df1),
            "better_file": "File 2" if sales_change > 0 else "File 1" if sales_change < 0 else "Equal"
        }
    }


#if __name__ == "__main__":
    df = load_and_process_data("data/Data_test.csv")
