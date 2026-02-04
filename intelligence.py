import os
import google.generativeai as genai
import json

genai.configure(api_key="AIzaSyDXh6jSYeadPyQSM4Alw2Pyc8w-pnYjrBg")
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
def generate_ai_insights(kpis, chart_data):
    """
    Uses Google Gemini to analyze the data summary.
    """
    
    # 1. Construct the data context (Same as before)
    context = f"""
    Dataset Summary:
    - Total Revenue: ${kpis.get('total_revenue', 0)}
    - Total Rows: {kpis.get('row_count', 0)}
    """
    
    if 'bar_chart' in chart_data:
        context += f"\n- Top Performers: {chart_data['bar_chart']['labels'][:3]} with values {chart_data['bar_chart']['values'][:3]}"
    
    if 'waterfall' in chart_data:
        context += f"\n- Profitability: {chart_data['waterfall']['values']}"

    # 2. specific instructions for JSON output
    prompt = f"""
    You are a business intelligence analyst. Analyze this summary:
    {context}

    Return a JSON object with exactly these two keys:
    1. "short_insights": A list of 3 short strings (bullet points).
    2. "paragraph": A single string summarizing the business health.

    Example format:
    {{ "short_insights": ["insight 1", "insight 2"], "paragraph": "analysis..." }}
    """

    try:
        # 3. Call Gemini
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
        
        # 4. Parse the result
        return json.loads(response.text)

    except Exception as e:
        print(f"AI Error: {e}")
        return {
            "short_insights": ["AI unavailable", "Check API Key", "Data processed successfully"],
            "paragraph": "Could not generate narrative analysis at this time."
        }