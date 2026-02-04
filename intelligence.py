def select_top_visuals(metadata, df):
    recommendations = []
    
    # Logic for Waterfall: Needs multiple financial columns or calculated revenue
    if 'calculated_revenue' in df.columns and any(k in metadata['financial'] for k in ['profit', 'cost']):
        recommendations.append('waterfall')
        
    # Logic for Line Chart: Needs temporal data
    if metadata['temporal']:
        recommendations.append('line_chart')
        
    # Logic for Bar Chart: Needs categories
    if metadata['categorical']:
        recommendations.append('bar_chart')
        
    # Big Number KPIs are always included in the returned kpis object
    return recommendations[:3] # Returns top 3