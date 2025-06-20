#!/usr/bin/env python3
"""
Component Risk Analysis Table Generator
Reusable component risk analysis for all notebooks
"""

import pandas as pd
from IPython.display import display, HTML

def component_risk_table(data, project_name):
    """
    Generate component risk analysis table with color coding
    
    Args:
        data (pd.DataFrame): JIRA data with Components column
        project_name (str): Name of the project for display
    """
    
    # Check if data is empty or missing required columns
    if data.empty or 'Components' not in data.columns:
        display(HTML(f"<b>No data available for {project_name}. DataFrame is empty or missing 'Components' column.</b>"))
        return
    
    # Filter out rows with missing components
    data_filtered = data[data['Components'].notna()].copy()
    
    if data_filtered.empty:
        display(HTML(f"<b>No bug data with components available for {project_name}.</b>"))
        return
        
    # Use the filtered data for analysis (already filtered to last 6 months)
    data_last6 = data_filtered

    # Group by component and count bugs
    component_counts = data_last6['Components'].value_counts()
    component_risk_rank = component_counts.rank(ascending=False, method='min').astype(int)
    
    # Create component-level summary (not individual bug level)
    summary_df = pd.DataFrame({
        '🧩 Components': component_counts.index,
        '🐞 Bug Count': component_counts.values,
        'Risk Score': component_risk_rank.values
    })
    
    # Add explanation based on component risk with realistic assessments
    def get_component_explanation(component, count, risk_score, max_risk):
        if risk_score == 1:  # Highest risk (most bugs)
            if count >= 5:
                return f'The "{component}" component has the highest number of bugs ({count}), making it very high-risk.'
            elif count >= 3:
                return f'The "{component}" component has {count} bugs, making it high-risk.'
            else:
                return f'The "{component}" component has {count} bugs, making it medium-risk.'
        elif count == 1:  # Single bug components
            return f'The "{component}" component has only 1 bug, making it low-risk.'
        elif count == 2:  # Two bug components
            return f'The "{component}" component has 2 bugs, making it medium-risk.'
        elif count >= 3:  # Multiple bug components
            return f'The "{component}" component has {count} bugs, making it high-risk.'
        else:
            return f'The "{component}" component has {count} bug(s), making it low-risk.'
    
    max_risk = component_risk_rank.max()
    summary_df['Explanation'] = [
        get_component_explanation(row['🧩 Components'], row['🐞 Bug Count'], row['Risk Score'], max_risk) 
        for _, row in summary_df.iterrows()
    ]

    # Add color mapping based on bug count
    def get_risk_color_style(count):
        try:
            if count >= 5:  # Very high risk
                return 'background-color: #ff4d4d; color: white; font-weight: bold;'
            elif count >= 3:  # High risk
                return 'background-color: #ff8c66; color: white; font-weight: bold;'
            elif count == 2:  # Medium risk
                return 'background-color: #ffd966; color: black; font-weight: bold;'
            else:  # Low risk (1 bug)
                return 'background-color: #85e085; color: black; font-weight: bold;'
        except:
            return ''
    
    # Apply color styling based on bug count
    summary_df['_style'] = summary_df['🐞 Bug Count'].apply(get_risk_color_style)
    
    # Fancy summary
    total_bugs = len(data_last6)
    total_components = len(component_counts)
    top_component = component_counts.index[0]
    top_count = component_counts.iloc[0]
    
    # Determine risk level for top component
    if top_count >= 5:
        risk_level = "Very High Risk"
        risk_color = "#ff4d4d"
    elif top_count >= 3:
        risk_level = "High Risk"
        risk_color = "#ff8c66"
    elif top_count == 2:
        risk_level = "Medium Risk"
        risk_color = "#ffd966"
    else:
        risk_level = "Low Risk"
        risk_color = "#85e085"
    
    summary_html = f"""
<div style="background: #111; border-radius: 12px; padding: 18px 28px; margin-bottom: 24px; box-shadow: 0 2px 8px #222;">
    <h2 style="margin-top:0; color:#ffe066;">✨ <b>Component Risk Analysis for {project_name}</b> ✨</h2>
    <ul style="font-size: 1.1em; color: #fff;">
        <li><b>Total bugs (last 6 months):</b> {total_bugs}</li>
        <li><b>Total components affected:</b> {total_components}</li>
        <li><b>Top component:</b> <span style="color:{risk_color};">{top_component}</span> ({top_count} bugs - {risk_level})</li>
        <li><b>Risk levels:</b> 5+ bugs = Very High, 3-4 bugs = High, 2 bugs = Medium, 1 bug = Low</li>
    </ul>
</div>
"""

    # Create custom HTML table with color coding
    table_rows = []
    for i, row in summary_df.head(10).iterrows():
        component = row['🧩 Components']
        bug_count = row['🐞 Bug Count']
        risk_score = row['Risk Score']
        explanation = row['Explanation']
        style = row['_style']
        
        table_rows.append(f"""
        <tr>
            <td style="padding: 8px; border: 1px solid #ddd;">{i}</td>
            <td style="padding: 8px; border: 1px solid #ddd;">{component}</td>
            <td style="padding: 8px; border: 1px solid #ddd; text-align: center;">{bug_count}</td>
            <td style="padding: 8px; border: 1px solid #ddd; text-align: center; {style}">{risk_score}</td>
            <td style="padding: 8px; border: 1px solid #ddd; max-width: 400px; word-wrap: break-word;">{explanation}</td>
        </tr>
        """)
    
    custom_table = f"""
    <table style="border-collapse: collapse; width: 100%; margin: 0 auto;">
        <thead>
            <tr style="background-color: #1a1368; color: white; font-size: 1.1em;">
                <th style="padding: 12px; border: 1px solid #ddd;"></th>
                <th style="padding: 12px; border: 1px solid #ddd;">🧩 Components</th>
                <th style="padding: 12px; border: 1px solid #ddd;">🐞 Bug Count</th>
                <th style="padding: 12px; border: 1px solid #ddd;">Risk Score</th>
                <th style="padding: 12px; border: 1px solid #ddd;">Explanation</th>
            </tr>
        </thead>
        <tbody>
            {''.join(table_rows)}
        </tbody>
    </table>
    """

    display(HTML(summary_html))
    display(HTML(f"""
    <div style="display: flex; flex-direction: column; align-items: center;">
        <h3 style="text-align:center; color:#2d4157;"><span style="color:#ffd166;">📊 <b>Component Risk Scoring Table</b></h3>
        <div style="min-width:450px; max-width:900px;">
            {custom_table}
        </div>
        <p style="color:#888; font-size:0.95em; margin-top:18px;">🔎 <i>Components with realistic risk assessment: Red = Very High (5+ bugs), Orange = High (3+ bugs), Yellow = Medium (2 bugs), Green = Low (1 bug).</i></p>
    </div>
    """))

def generate_risk_summary_stats(data):
    """
    Generate risk summary statistics
    
    Args:
        data (pd.DataFrame): JIRA data with Components column
    
    Returns:
        dict: Summary statistics
    """
    
    if data.empty or 'Components' not in data.columns:
        return {}
    
    data_filtered = data[data['Components'].notna()].copy()
    if data_filtered.empty:
        return {}
    
    component_counts = data_filtered['Components'].value_counts()
    
    return {
        'total_bugs': len(data_filtered),
        'total_components': len(component_counts),
        'top_component': component_counts.index[0] if len(component_counts) > 0 else None,
        'top_count': component_counts.iloc[0] if len(component_counts) > 0 else 0,
        'avg_bugs_per_component': component_counts.mean(),
        'components_with_multiple_bugs': len(component_counts[component_counts > 1])
    } 