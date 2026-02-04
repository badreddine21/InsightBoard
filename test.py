from intelligence import select_top_visuals,generate_ai_insights
import pandas as pd
import numpy as np
import time
import os
import json

class BusinessEngine:
    def __init__(self, file_path):
        self.file_path = file_path
        self.raw_df = None
        self.clean_df = None
        self.metadata = {}

    def load_data(self):
        ext = os.path.splitext(self.file_path)[-1].lower()
        if ext == '.csv':
            self.raw_df = pd.read_csv(self.file_path, low_memory=False)
        elif ext in ['.xls', '.xlsx']:
            self.raw_df = pd.read_excel(self.file_path, engine='openpyxl')
        else:
            raise ValueError(f"Unsupported format: {ext}")
        return self.raw_df

    def standardize_and_clean(self):
        df = self.raw_df.copy()
        
        # Standardize Headers
        df.columns = (df.columns.str.strip().str.lower()
                      .str.replace(' ', '_').str.replace('(', '', regex=False)
                      .str.replace(')', '', regex=False))
        
        # Numeric Scrubber
        for col in df.columns:
            if any(k in col for k in ['price', 'sales', 'revenue', 'quantity', 'amount', 'cost']):
                if df[col].dtype == 'object':
                    df[col] = df[col].replace(r'[\$, ]', '', regex=True)
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        # Revenue Calculation
        price_col = next((c for c in df.columns if 'price' in c or 'unit_price' in c), None)
        qty_col = next((c for c in df.columns if 'quantity' in c or 'qty' in c), None)
        
        if price_col and qty_col:
            df['calculated_revenue'] = df[price_col] * df[qty_col]

        # Fill text gaps
        text_cols = df.select_dtypes(include=['object']).columns
        df[text_cols] = df[text_cols].fillna('Unknown')
        
        self.clean_df = df
        return df

    def classify_columns(self):
        df = self.clean_df
        classes = {'temporal': [], 'financial': [], 'categorical': [], 'identity': []}

        cols = list(df.columns)
        if 'calculated_revenue' in cols:
            cols.insert(0, cols.pop(cols.index('calculated_revenue')))

        for col in cols:
            col_lower = col.lower()
            if any(k in col_lower for k in ['id', 'sku', 'code']) and 'customer' not in col_lower:
                classes['identity'].append(col)
            elif any(k in col_lower for k in ['date', 'time', 'year', 'month']):
                classes['temporal'].append(col)
                df[col] = pd.to_datetime(df[col], errors='coerce', format='mixed')
            elif any(k in col_lower for k in ['revenue', 'sales', 'price', 'profit', 'amount']):
                classes['financial'].append(col)
            elif df[col].dtype == 'object' and df[col].nunique() < (len(df) * 0.2):
                classes['categorical'].append(col)

        self.metadata = classes
        return classes
    
    def run_analysis(self):
        classes = self.metadata
        df = self.clean_df
        
        # Initialize report structure
        report = {
            "metadata": {
                "filename": os.path.basename(self.file_path),
                "columns_classified": self.metadata,
                "row_count": len(self.clean_df)
            },
            "kpis": {},
            "charts": {},
            "recommendations": []
        }

        # 1. Get Recommendations
        recommended_types = select_top_visuals(classes, df)
        report["recommendations"] = recommended_types

        # 2. Calculate KPIs
        rev_col = 'calculated_revenue' if 'calculated_revenue' in df.columns else None
        report['kpis']['total_revenue'] = float(df[rev_col].sum()) if rev_col else 0
        report['kpis']['row_count'] = len(df)

        # 3. Generate Data for Recommended Charts
        
        # --- A. BAR CHART (Top Category) ---
        if 'bar_chart' in recommended_types and classes['categorical']:
            cat_col = classes['categorical'][0]  # Use first categorical column
            
            if rev_col:
                data = df.groupby(cat_col)[rev_col].sum().sort_values(ascending=False).head(10)
                metric = "Revenue"
            else:
                data = df[cat_col].value_counts().head(10)
                metric = "Count"
                
            report['charts']['bar_chart'] = {
                "labels": data.index.astype(str).tolist(),
                "values": [float(x) for x in data.values],
                "title": f"Top {cat_col.replace('_', ' ').title()} by {metric}"
            }

        # --- B. LINE CHART (Time Series) ---
        if 'line_chart' in recommended_types and classes['temporal']:
            time_col = classes['temporal'][0]
            
            if rev_col:
                try:
                    df_time = df.set_index(time_col)
                    data = df_time[rev_col].resample('M').sum()
                    labels = data.index.strftime('%Y-%m').tolist()
                except:
                    data = df.groupby(time_col)[rev_col].sum()
                    labels = data.index.astype(str).tolist()
                
                metric = "Revenue"
            else:
                data = df.groupby(time_col).size()
                labels = data.index.astype(str).tolist()
                metric = "Activity"

            report['charts']['line_chart'] = {
                "labels": labels,
                "values": [float(x) for x in data.values],
                "title": f"{metric} Trends Over Time"
            }

        # --- C. WATERFALL (Profitability) ---
        if 'waterfall' in recommended_types:
            total_rev = report['kpis']['total_revenue']
            
            profit_col = next((c for c in classes['financial'] if 'profit' in c), None)
            cost_col = next((c for c in classes['financial'] if 'cost' in c), None)
            
            if profit_col:
                total_profit = df[profit_col].sum()
                total_cost = total_rev - total_profit
            elif cost_col:
                total_cost = df[cost_col].sum()
                total_profit = total_rev - total_cost
            else:
                total_profit = total_rev * 0.25 
                total_cost = total_rev * 0.75

            report['charts']['waterfall'] = {
                "labels": ["Total Revenue", "Costs", "Net Profit"],
                "values": [total_rev, -total_cost, total_profit],
                "title": "Profitability Breakdown"
            }

        print("Generating AI Analysis...")
        ai_result = generate_ai_insights(report['kpis'], report['charts'])
        
        report['ai_analysis'] = ai_result

        return report
    # Renamed to simply serialize the result
    def generate_json_report(self, analysis_results):
        return json.dumps(analysis_results, indent=4)