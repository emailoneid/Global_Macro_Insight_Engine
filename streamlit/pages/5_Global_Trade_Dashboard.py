import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime
import sys
import os
from functools import lru_cache
import warnings
warnings.filterwarnings('ignore')

# Add the parent directory to Python path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.data_loader import load_global_trade_data

# Page Config
st.set_page_config(
    page_title="Global Trade Dashboard",
    page_icon="🌏",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }
    .metric-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #e9ecef;
        margin: 0.5rem 0;
        height: 180px;
        min-width: 150px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
    }
    .metric-value {
        font-size: 1.3rem;
        font-weight: 700;
        margin: 0.5rem 0;
        word-wrap: break-word;
        max-width: 100%;
        line-height: 1.3;
        overflow-wrap: break-word;
        hyphens: auto;
        padding: 0 0.5rem;
    }
    .metric-label {
        font-size: 0.85rem;
        color: #6c757d;
        font-weight: 500;
        margin-bottom: 0.5rem;
    }
    .metric-subtitle {
        font-size: 0.8rem;
        color: #6c757d;
        font-weight: 400;
        margin-top: 0.5rem;
    }
    .section-header {
        background: linear-gradient(135deg, #495057 0%, #6c757d 100%);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 10px;
        margin: 1.5rem 0 1rem 0;
        font-weight: 600;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .insight-card {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #007bff;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .alert-box {
        background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
        border: 1px solid #ffc107;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .success-box {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        border: 1px solid #28a745;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .stDataFrame {
        border-radius: 8px;
        overflow: hidden;
    }
    .stSelectbox > div > div {
        border-radius: 8px;
    }
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Title with enhanced styling
st.markdown("""
<div class="main-header">
    <h1>🌏 Global Trade Dashboard</h1>
    <p>Comprehensive analysis of global trade flows, shipping indices, and strategic insights</p>
</div>
""", unsafe_allow_html=True)

# Cache data loading for better performance
@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_cached_global_trade_data():
    try:
        data = load_global_trade_data()
        return data
    except Exception as e:
        st.error(f"Error loading global trade data: {str(e)}")
        return {}

# Helper Functions
def create_metric_card(title, value, subtitle="", color="#007bff"):
    # Truncate long values for better display
    if isinstance(value, str) and len(value) > 40:
        value = value[:37] + "..."
    
    return f"""
    <div class="metric-card">
        <div class="metric-label">{title}</div>
        <div class="metric-value" style="color: {color};">{value}</div>
        <div class="metric-subtitle">{subtitle}</div>
    </div>
    """

def format_currency(value):
    """Format currency values with appropriate units"""
    if value >= 1e9:
        return f"${value/1e9:.1f}B"
    elif value >= 1e6:
        return f"${value/1e6:.1f}M"
    elif value >= 1e3:
        return f"${value/1e3:.1f}K"
    else:
        return f"${value:.0f}"

def truncate_text(text, max_length=35):
    """Truncate text to fit in metric cards"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."

def truncate_chart_labels(text, max_length=30):
    """Truncate text for chart labels"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."

def apply_chart_styling(fig, title_color="#1e3c72"):
    fig.update_layout(
        title_font_size=18,
        title_font_color=title_color,
        xaxis_title_font_size=14,
        yaxis_title_font_size=14,
        template="plotly_white",
        margin=dict(l=50, r=50, t=80, b=120),  # Increased bottom margin
        height=550  # Increased height
    )
    fig.update_xaxes(
        showgrid=True, 
        gridwidth=1, 
        gridcolor='rgba(0,0,0,0.1)',
        tickangle=-30,  # Reduced rotation angle
        tickfont=dict(size=12)  # Increased font size
    )
    fig.update_yaxes(
        showgrid=True, 
        gridwidth=1, 
        gridcolor='rgba(0,0,0,0.1)',
        tickfont=dict(size=12)
    )
    return fig

def extract_section(text, start, end=None):
    if start not in text:
        return ""
    section = text.split(start)[1]
    if end and end in section:
        section = section.split(end)[0]
    return section.strip()

def format_insight_text(text):
    if not text:
        return ""
    lines = text.strip().split('\n')
    formatted = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.startswith("•"):
            clean_line = line[1:].strip()
            if clean_line and clean_line[0].isdigit() and len(clean_line) > 1 and clean_line[1] == '.':
                formatted.append(clean_line)
            elif ":" in line:
                parts = line.split(":", 1)
                if len(parts) == 2:
                    label = parts[0].strip()
                    content = parts[1].strip()
                    formatted.append(f"**{label}:** {content}")
                else:
                    formatted.append(line)
            else:
                formatted.append(line)
        elif any(emoji in line for emoji in ['🛠', '📊', '🎯', '⚠️', '📈', '📉', '🔄']) and ':' in line:
            formatted.append(line)
        elif any(emoji in line for emoji in ['🛠', '📊', '🎯', '⚠️', '📈', '📉', '🔄']) and not ':' in line:
            formatted.append(f"\n**{line}**")
        elif line and line[0].isdigit() and len(line) > 1 and line[1] == '.':
            formatted.append(line)
        elif line and not line.startswith("-"):
            formatted.append(f"• {line}")
        else:
            formatted.append(line)
    return "\n\n".join(formatted)

# Load Data
with st.spinner("Loading global trade intelligence data..."):
    data = load_cached_global_trade_data()

# Extract data
export_decrease_items_top5 = data.get("export_decrease_items_top5", pd.DataFrame())
export_increase_items_top5 = data.get("export_increase_items_top5", pd.DataFrame())
export_increase_countries_top5 = data.get("export_increase_countries_top5", pd.DataFrame())
trade_partners_top5 = data.get("trade_partners_top5", pd.DataFrame())
shipping_index_pivoted = data.get("shipping_index_pivoted", pd.DataFrame())
shipping_index_correlation = data.get("shipping_index_correlation", pd.DataFrame())
shipping_index_3m_volatility = data.get("shipping_index_3m_volatility", pd.DataFrame())
key_insights = data.get("insights", {})
gemini_insight = data.get("gemini_insight", "No AI insights found.")

# Sidebar for filters and controls
st.sidebar.markdown("## 🎛️ Dashboard Controls")

# Date range filter for shipping index
if not shipping_index_pivoted.empty and 'date' in shipping_index_pivoted.index:
    shipping_index_pivoted = shipping_index_pivoted.reset_index()
if not shipping_index_pivoted.empty and 'date' in shipping_index_pivoted.columns:
    try:
        min_date = pd.to_datetime(shipping_index_pivoted['date']).min()
        max_date = pd.to_datetime(shipping_index_pivoted['date']).max()
        st.sidebar.markdown("### 📅 Date Range")
        date_range = st.sidebar.date_input(
            "Select date range:",
            value=(min_date.date(), max_date.date()),
            min_value=min_date.date(),
            max_value=max_date.date()
        )
        if len(date_range) == 2:
            start_date, end_date = date_range
            shipping_index_pivoted = shipping_index_pivoted[(pd.to_datetime(shipping_index_pivoted['date']).dt.date >= start_date) & (pd.to_datetime(shipping_index_pivoted['date']).dt.date <= end_date)]
    except Exception as e:
        st.sidebar.warning(f"Date filtering error: {str(e)}")

# Filter status indicator
st.sidebar.markdown("### 📊 Filter Status")
active_filters = []
if 'date_range' in locals() and len(date_range) == 2:
    if 'min_date' in locals() and 'max_date' in locals():
        if date_range[0] != min_date.date() or date_range[1] != max_date.date():
            active_filters.append(f"Date: {date_range[0]} to {date_range[1]}")
if active_filters:
    st.sidebar.success(f"✅ Active filters: {len(active_filters)}")
    for filter_info in active_filters:
        st.sidebar.info(f"• {filter_info}")
else:
    st.sidebar.info("ℹ️ No filters applied")

# Key Metrics with enhanced styling and better text formatting
st.markdown('<div class="section-header"><h2>📊 Key Trade Metrics</h2></div>', unsafe_allow_html=True)
if key_insights and "summary_statistics" in key_insights:
    stats = key_insights["summary_statistics"]
    top5_decrease = stats.get("Top 5 YoY Decrease Items", [])
    top5_increase = stats.get("Top 5 YoY Increase Items", [])
    top5_countries = stats.get("Top 5 Export Increase Countries", [])
    top5_partners = stats.get("Top Trade Partners by Export Value", [])
else:
    top5_decrease = top5_increase = top5_countries = top5_partners = []

# Get volatility metrics
volatility_metrics = {}
if not shipping_index_3m_volatility.empty:
    volatility_data = shipping_index_3m_volatility.dropna()
    if not volatility_data.empty:
        volatility_metrics = {
            "current": volatility_data['value'].iloc[-1],
            "average": volatility_data['value'].mean(),
            "max": volatility_data['value'].max(),
            "min": volatility_data['value'].min()
        }

# First row: 3 cards
col1, col2, col3 = st.columns(3)
with col1:
    decrease_name = truncate_text(top5_decrease[0]["commodity_full_name"], 30) if top5_decrease else "N/A"
    decrease_pct = f"{top5_decrease[0]['yoy_change_percent']:.1f}%" if top5_decrease else ""
    st.markdown(create_metric_card(
        "⬇️ Top Decrease Item",
        decrease_name,
        f"YoY: {decrease_pct}",
        "#dc3545"
    ), unsafe_allow_html=True)

with col2:
    increase_name = truncate_text(top5_increase[0]["commodity_full_name"], 30) if top5_increase else "N/A"
    increase_pct = f"{top5_increase[0]['yoy_change_percent']:.1f}%" if top5_increase else ""
    st.markdown(create_metric_card(
        "⬆️ Top Increase Item",
        increase_name,
        f"YoY: {increase_pct}",
        "#28a745"
    ), unsafe_allow_html=True)

with col3:
    if top5_countries:
        country_pair = f"{top5_countries[0]['country']} → {top5_countries[0]['partner']}"
        country_display = truncate_text(country_pair, 30)
        country_pct = f"{top5_countries[0]['yoy_change_percent']:.1f}%"
    else:
        country_display = "N/A"
        country_pct = ""
    st.markdown(create_metric_card(
        "🌍 Top Increase Country",
        country_display,
        f"YoY: {country_pct}",
        "#007bff"
    ), unsafe_allow_html=True)

# Second row: 3 cards
col4, col5, col6 = st.columns(3)
with col4:
    if top5_partners:
        partner_pair = f"{top5_partners[0]['country']} → {top5_partners[0]['partner']}"
        partner_display = truncate_text(partner_pair, 30)
        export_value = format_currency(top5_partners[0]['export_value_thousand_usd'] * 1000)  # Convert to actual USD
    else:
        partner_display = "N/A"
        export_value = ""
    st.markdown(create_metric_card(
        "🤝 Top Trade Partner",
        partner_display,
        f"Export: {export_value}",
        "#ffc107"
    ), unsafe_allow_html=True)

with col5:
    current_vol = f"{volatility_metrics.get('current', 0):.1f}" if volatility_metrics else "N/A"
    avg_vol = f"Avg: {volatility_metrics.get('average', 0):.1f}" if volatility_metrics else ""
    st.markdown(create_metric_card(
        "📊 Current Volatility",
        current_vol,
        avg_vol,
        "#e74c3c"
    ), unsafe_allow_html=True)

with col6:
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
    st.markdown(create_metric_card(
        "🕒 Last Update",
        current_time,
        "Data refresh time",
        "#6c757d"
    ), unsafe_allow_html=True)

# Top 5 Export Decrease Items
st.markdown('<div class="section-header"><h2>⬇️ Top 5 Export Decrease Items (YoY)</h2></div>', unsafe_allow_html=True)
if not export_decrease_items_top5.empty:
    # Sort by YoY change (ascending - lowest decrease first)
    decrease_data = export_decrease_items_top5.head(5).sort_values('yoy_change_percent', ascending=True)
    
    # Truncate labels for better display
    decrease_data = decrease_data.copy()
    decrease_data['commodity_display'] = decrease_data['commodity_full_name'].apply(truncate_chart_labels)
    
    # Create bar chart for top 5 decrease items
    fig_decrease = px.bar(
        decrease_data,
        x='commodity_display',
        y='yoy_change_percent',
        title="Top 5 Export Items with Largest YoY Decrease",
        labels={'commodity_display': 'Commodity', 'yoy_change_percent': 'YoY Change (%)'},
        color='yoy_change_percent',
        color_continuous_scale='Reds_r',  # Darker reds for larger decreases
        template="plotly_white"
    )
    
    # Add data labels on bars
    fig_decrease.update_traces(
        textposition='outside',
        texttemplate='%{y:.1f}%',
        textfont=dict(size=12, color='black'),
        width=0.7  # Increase bar width
    )
    
    # Add hover template with full commodity names
    fig_decrease.update_traces(
        hovertemplate='<b>%{fullData.name}</b><br>' +
                     'Commodity: %{customdata}<br>' +
                     'YoY Change: %{y:.1f}%<br>' +
                     '<extra></extra>',
        customdata=decrease_data['commodity_full_name']
    )
    
    fig_decrease = apply_chart_styling(fig_decrease)
    
    # Customize y-axis to show increments of 10
    fig_decrease.update_layout(
        yaxis=dict(
            dtick=10,  # Set tick interval to 10
            tickmode='linear',
            range=[-45, 0]  # Set range from -45 to 0 for better spacing
        )
    )
    
    st.plotly_chart(fig_decrease, use_container_width=True)
    
    # Display detailed table
    st.subheader("📋 Detailed Information")
    display_decrease = decrease_data[['commodity_full_name', 'export_value_thousand_usd', 'yoy_change_percent', 'country']].copy()
    display_decrease['export_value_thousand_usd'] = display_decrease['export_value_thousand_usd'].apply(lambda x: f"${x:,.0f}")
    display_decrease['yoy_change_percent'] = display_decrease['yoy_change_percent'].apply(lambda x: f"{x:.1f}%")
    display_decrease.columns = ['Commodity', 'Export Value (USD)', 'YoY Change (%)', 'Country']
    st.dataframe(display_decrease, use_container_width=True)
else:
    st.markdown("""
    <div class="alert-box">
        <h4>⚠️ No Export Decrease Data Available</h4>
        <p>No export decrease data is currently available.</p>
    </div>
    """, unsafe_allow_html=True)

# Top 5 Export Increase Items
st.markdown('<div class="section-header"><h2>⬆️ Top 5 Export Increase Items (YoY)</h2></div>', unsafe_allow_html=True)
if not export_increase_items_top5.empty:
    # Sort by YoY change (descending - highest increase first)
    increase_data = export_increase_items_top5.head(5).sort_values('yoy_change_percent', ascending=False)
    
    # Truncate labels for better display
    increase_data = increase_data.copy()
    increase_data['commodity_display'] = increase_data['commodity_full_name'].apply(truncate_chart_labels)
    
    # Create bar chart for top 5 increase items
    fig_increase = px.bar(
        increase_data,
        x='commodity_display',
        y='yoy_change_percent',
        title="Top 5 Export Items with Largest YoY Increase",
        labels={'commodity_display': 'Commodity', 'yoy_change_percent': 'YoY Change (%)'},
        color='yoy_change_percent',
        color_continuous_scale='Greens',  # Lighter greens for larger increases (reversed)
        template="plotly_white"
    )
    
    # Add data labels on bars
    fig_increase.update_traces(
        textposition='outside',
        texttemplate='%{y:.1f}%',
        textfont=dict(size=12, color='black'),
        width=0.7  # Increase bar width
    )
    
    # Add hover template with full commodity names
    fig_increase.update_traces(
        hovertemplate='<b>%{fullData.name}</b><br>' +
                     'Commodity: %{customdata}<br>' +
                     'YoY Change: %{y:.1f}%<br>' +
                     '<extra></extra>',
        customdata=increase_data['commodity_full_name']
    )
    
    fig_increase = apply_chart_styling(fig_increase)
    st.plotly_chart(fig_increase, use_container_width=True)
    
    # Display detailed table
    st.subheader("📋 Detailed Information")
    display_increase = increase_data[['commodity_full_name', 'export_value_thousand_usd', 'yoy_change_percent', 'country']].copy()
    display_increase['export_value_thousand_usd'] = display_increase['export_value_thousand_usd'].apply(lambda x: f"${x:,.0f}")
    display_increase['yoy_change_percent'] = display_increase['yoy_change_percent'].apply(lambda x: f"{x:.1f}%")
    display_increase.columns = ['Commodity', 'Export Value (USD)', 'YoY Change (%)', 'Country']
    st.dataframe(display_increase, use_container_width=True)
else:
    st.markdown("""
    <div class="alert-box">
        <h4>⚠️ No Export Increase Data Available</h4>
        <p>No export increase data is currently available.</p>
    </div>
    """, unsafe_allow_html=True)

# Top 5 Export Increase Countries
st.markdown('<div class="section-header"><h2>🌍 Top 5 Export Increase Countries (YoY)</h2></div>', unsafe_allow_html=True)
if not export_increase_countries_top5.empty:
    # Sort by YoY change (descending - highest increase first)
    countries_data = export_increase_countries_top5.head(5).sort_values('yoy_change_percent', ascending=False)
    
    # Truncate labels for better display
    countries_data = countries_data.copy()
    countries_data['country_display'] = countries_data['country'].apply(truncate_chart_labels)
    
    # Create bar chart for top 5 increase countries
    fig_countries = px.bar(
        countries_data,
        x='country_display',
        y='yoy_change_percent',
        title="Top 5 Countries with Largest Export YoY Increase",
        labels={'country_display': 'Country', 'yoy_change_percent': 'YoY Change (%)'},
        color='yoy_change_percent',
        color_continuous_scale='Oranges',  # Orange scale for better distinction
        template="plotly_white"
    )
    
    # Add data labels on bars
    fig_countries.update_traces(
        textposition='outside',
        texttemplate='%{y:.1f}%',
        textfont=dict(size=12, color='black'),
        width=0.7  # Increase bar width
    )
    
    # Add hover template with full country names and partner info
    fig_countries.update_traces(
        hovertemplate='<b>%{fullData.name}</b><br>' +
                     'Country: %{customdata[0]}<br>' +
                     'Partner: %{customdata[1]}<br>' +
                     'YoY Change: %{y:.1f}%<br>' +
                     '<extra></extra>',
        customdata=list(zip(countries_data['country'], countries_data['partner']))
    )
    
    fig_countries = apply_chart_styling(fig_countries)
    st.plotly_chart(fig_countries, use_container_width=True)
    
    # Display detailed table
    st.subheader("📋 Detailed Information")
    display_countries = export_increase_countries_top5.head(5)[['country', 'partner', 'export_value_thousand_usd', 'yoy_change_percent']].copy()
    display_countries['export_value_thousand_usd'] = display_countries['export_value_thousand_usd'].apply(lambda x: f"${x:,.0f}")
    display_countries['yoy_change_percent'] = display_countries['yoy_change_percent'].apply(lambda x: f"{x:.1f}%")
    display_countries.columns = ['Country', 'Trade Partner', 'Export Value (USD)', 'YoY Change (%)']
    st.dataframe(display_countries, use_container_width=True)
else:
    st.markdown("""
    <div class="alert-box">
        <h4>⚠️ No Export Countries Data Available</h4>
        <p>No export countries data is currently available.</p>
    </div>
    """, unsafe_allow_html=True)

# Top 5 Trading Partners
st.markdown('<div class="section-header"><h2>🤝 Top 5 Trading Partners by Export Value</h2></div>', unsafe_allow_html=True)
if not trade_partners_top5.empty:
    # Sort by export value (descending - highest value first)
    partners_data = trade_partners_top5.head(5).sort_values('export_value_thousand_usd', ascending=False)
    
    # Create country pair labels
    partners_data = partners_data.copy()
    partners_data['country_pair'] = partners_data['country'] + ' → ' + partners_data['partner']
    
    # Create horizontal bar chart for top 5 trading partners
    fig_partners = px.bar(
        partners_data,
        x='export_value_thousand_usd',
        y='country_pair',
        orientation='h',  # Horizontal orientation
        title="Top 5 Trading Partners by Export Value",
        labels={'export_value_thousand_usd': 'Export Value (USD)', 'country_pair': 'Country Pair'},
        color='export_value_thousand_usd',
        color_continuous_scale='Reds',  # Red scale to highlight importance
        template="plotly_white"
    )
    
    # Add data labels on bars
    fig_partners.update_traces(
        textposition='outside',
        texttemplate='$%{x:,.0f}B',
        textfont=dict(size=12, color='black'),
        width=0.7  # Increase bar width
    )
    
    # Add hover template with full country names and partner info
    fig_partners.update_traces(
        hovertemplate='<b>%{fullData.name}</b><br>' +
                     'Country Pair: %{y}<br>' +
                     'Export Value: $%{x:,.0f}B<br>' +
                     '<extra></extra>'
    )
    
    # Custom styling for horizontal chart
    fig_partners.update_layout(
        title_font_size=18,
        title_font_color="#1e3c72",
        xaxis_title_font_size=14,
        yaxis_title_font_size=14,
        template="plotly_white",
        margin=dict(l=50, r=50, t=80, b=50),
        height=550,
        xaxis=dict(
            showgrid=True, 
            gridwidth=1, 
            gridcolor='rgba(0,0,0,0.1)',
            tickfont=dict(size=12),
            tickformat=',.0f',  # Format x-axis ticks with commas
            tickprefix='$',
            ticksuffix='B',
            range=[0, partners_data['export_value_thousand_usd'].max() * 1.1]  # Add 10% padding
        ),
        yaxis=dict(
            showgrid=True, 
            gridwidth=1, 
            gridcolor='rgba(0,0,0,0.1)',
            tickfont=dict(size=12)
        )
    )
    
    st.plotly_chart(fig_partners, use_container_width=True)
    
    # Display detailed table
    st.subheader("📋 Detailed Information")
    display_partners = trade_partners_top5.head(5)[['country', 'partner', 'export_value_thousand_usd', 'yoy_change_percent']].copy()
    display_partners['export_value_thousand_usd'] = display_partners['export_value_thousand_usd'].apply(lambda x: f"${x:,.0f}")
    display_partners['yoy_change_percent'] = display_partners['yoy_change_percent'].apply(lambda x: f"{x:.1f}%" if pd.notna(x) else "N/A")
    display_partners.columns = ['Country', 'Trade Partner', 'Export Value (USD)', 'YoY Change (%)']
    st.dataframe(display_partners, use_container_width=True)
else:
    st.markdown("""
    <div class="alert-box">
        <h4>⚠️ No Trading Partners Data Available</h4>
        <p>No trading partners data is currently available.</p>
    </div>
    """, unsafe_allow_html=True)

# Shipping Index Trends - FIXED VERSION
st.markdown('<div class="section-header"><h2>🚢 Shipping Index Trends</h2></div>', unsafe_allow_html=True)
if not shipping_index_pivoted.empty:
    indicators = [col for col in shipping_index_pivoted.columns if col != "date"]
    
    # Check data availability for each indicator
    data_availability = {}
    for indicator in indicators:
        non_null_count = shipping_index_pivoted[indicator].dropna().shape[0]
        total_count = shipping_index_pivoted.shape[0]
        availability_pct = (non_null_count / total_count) * 100
        data_availability[indicator] = {
            'count': non_null_count,
            'percentage': availability_pct
        }
    
    # Display data availability info
    st.subheader("📊 Data Availability")
    availability_cols = st.columns(len(indicators))
    for i, indicator in enumerate(indicators):
        with availability_cols[i]:
            st.metric(
                f"{indicator}",
                f"{data_availability[indicator]['count']} points",
                f"{data_availability[indicator]['percentage']:.1f}% coverage"
            )
    
    selected_indicators = st.multiselect(
        "Select shipping indices:",
        options=["All Indices"] + indicators,
        default=["All Indices"]
    )
    
    if selected_indicators:
        if "All Indices" in selected_indicators:
            indices_to_plot = indicators
        else:
            indices_to_plot = selected_indicators
        
        # Create tabs for different chart views
        tab1, tab2, tab3 = st.tabs(["📈 Relative Change", "📊 Absolute Values", "🔍 Data Points"])
        
        with tab1:
            # Calculate relative changes (percentage change from first available value)
            shipping_relative = shipping_index_pivoted.copy()
            
            fig_relative = go.Figure()
            
            colors = px.colors.qualitative.Set3
            
            for i, indicator in enumerate(indices_to_plot):
                # Get only non-null values
                indicator_data = shipping_relative[[indicator, 'date']].dropna()
                
                if not indicator_data.empty:
                    # Get the first non-null value for this indicator
                    first_value = indicator_data[indicator].iloc[0]
                    
                    # Calculate percentage change from the first value
                    relative_values = ((indicator_data[indicator] - first_value) / first_value) * 100
                    
                    fig_relative.add_trace(go.Scatter(
                        x=indicator_data['date'],
                        y=relative_values,
                        mode='lines+markers',
                        name=indicator,
                        line=dict(color=colors[i % len(colors)], width=3),
                        marker=dict(size=6),
                        hovertemplate=f'<b>{indicator}</b><br>' +
                                    'Date: %{x}<br>' +
                                    'Relative Change: %{y:.1f}%<br>' +
                                    '<extra></extra>'
                    ))
            
            # Add horizontal line at 0% for reference
            fig_relative.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
            
            fig_relative.update_layout(
                title="Shipping Indices Relative Change Over Time",
                xaxis_title="Date",
                yaxis_title="Relative Change (%)",
                template="plotly_white",
                height=600,
                hovermode='x unified'
            )
            
            st.plotly_chart(fig_relative, use_container_width=True)
            st.info("📊 **Relative Change**: Shows percentage change from the first available value for each index. A value of 0% represents the starting point, positive values show growth, and negative values show decline.")
        
        with tab2:
            # Show absolute values
            fig_absolute = go.Figure()
            
            for i, indicator in enumerate(indices_to_plot):
                # Get only non-null values
                indicator_data = shipping_index_pivoted[[indicator, 'date']].dropna()
                
                if not indicator_data.empty:
                    fig_absolute.add_trace(go.Scatter(
                        x=indicator_data['date'],
                        y=indicator_data[indicator],
                        mode='lines+markers',
                        name=indicator,
                        line=dict(color=colors[i % len(colors)], width=3),
                        marker=dict(size=6),
                        hovertemplate=f'<b>{indicator}</b><br>' +
                                    'Date: %{x}<br>' +
                                    'Value: %{y:.2f}<br>' +
                                    '<extra></extra>'
                    ))
            
            fig_absolute.update_layout(
                title="Shipping Indices Absolute Values Over Time",
                xaxis_title="Date",
                yaxis_title="Index Value",
                template="plotly_white",
                height=600,
                hovermode='x unified'
            )
            
            st.plotly_chart(fig_absolute, use_container_width=True)
            st.info("📊 **Absolute Values**: Shows the actual index values without normalization.")
        
        with tab3:
            # Show data points summary
            st.subheader("📋 Data Points Summary")
            
            summary_data = []
            for indicator in indices_to_plot:
                indicator_data = shipping_index_pivoted[[indicator, 'date']].dropna()
                if not indicator_data.empty:
                    summary_data.append({
                        'Index': indicator,
                        'Data Points': len(indicator_data),
                        'First Date': indicator_data['date'].min().strftime('%Y-%m-%d'),
                        'Last Date': indicator_data['date'].max().strftime('%Y-%m-%d'),
                        'Min Value': indicator_data[indicator].min(),
                        'Max Value': indicator_data[indicator].max(),
                        'Latest Value': indicator_data[indicator].iloc[-1],
                        'Data Coverage': f"{(len(indicator_data) / len(shipping_index_pivoted)) * 100:.1f}%"
                    })
            
            if summary_data:
                summary_df = pd.DataFrame(summary_data)
                st.dataframe(summary_df, use_container_width=True)
            else:
                st.warning("No data available for selected indices.")
                
            # Show missing data pattern
            st.subheader("🔍 Missing Data Pattern")
            
            # Create a heatmap showing data availability
            availability_matrix = shipping_index_pivoted[['date'] + indices_to_plot].copy()
            availability_matrix = availability_matrix.set_index('date')
            
            # Convert to binary (1 for data, 0 for missing)
            availability_binary = availability_matrix.notna().astype(int)
            
            if not availability_binary.empty:
                fig_availability = px.imshow(
                    availability_binary.T,
                    title="Data Availability Heatmap (White = Data Available, Dark = Missing)",
                    color_continuous_scale="Greys",
                    aspect="auto"
                )
                fig_availability.update_layout(
                    height=300,
                    xaxis_title="Date",
                    yaxis_title="Index"
                )
                st.plotly_chart(fig_availability, use_container_width=True)
    else:
        st.warning("Please select at least one index to view trends.")
else:
    st.markdown("""
    <div class="alert-box">
        <h4>⚠️ No Shipping Index Data Available</h4>
        <p>No shipping index data is currently available.</p>
    </div>
    """, unsafe_allow_html=True)

# Shipping Index Correlation
st.markdown('<div class="section-header"><h2>🔗 Shipping Index Correlation</h2></div>', unsafe_allow_html=True)
if not shipping_index_correlation.empty:
    corr_matrix = shipping_index_correlation.set_index(shipping_index_correlation.columns[0])
    corr_min = corr_matrix.min().min()
    corr_max = corr_matrix.max().max()
    if corr_max - corr_min < 0.1:
        corr_min = max(-1, corr_min - 0.1)
        corr_max = min(1, corr_max + 0.1)
    fig_corr = px.imshow(
        corr_matrix,
        title="Shipping Index Correlation Matrix",
        color_continuous_scale="RdBu_r",
        zmin=corr_min,
        zmax=corr_max,
        aspect="auto",
        template="plotly_white"
    )
    fig_corr = apply_chart_styling(fig_corr)
    fig_corr.update_layout(height=500)
    fig_corr.update_xaxes(tickangle=-45)
    st.plotly_chart(fig_corr, use_container_width=True)
    st.info(f"💡 **Correlation Insights**: Values range from {corr_min:.2f} to {corr_max:.2f}. Values closer to {corr_max:.2f} indicate strong positive correlation, while values closer to {corr_min:.2f} indicate strong negative correlation.")
else:
    st.markdown("""
    <div class="alert-box">
        <h4>⚠️ No Correlation Data Available</h4>
        <p>No shipping index correlation data is currently available.</p>
    </div>
    """, unsafe_allow_html=True)

# Shipping Index Volatility Analysis
st.markdown('<div class="section-header"><h2>📊 Shipping Index Volatility Analysis</h2></div>', unsafe_allow_html=True)
if not shipping_index_3m_volatility.empty:
    # Clean the data - remove empty rows
    volatility_data = shipping_index_3m_volatility.dropna()
    
    if not volatility_data.empty:
        # Convert date column to datetime if not already
        if 'date' in volatility_data.columns:
            volatility_data['date'] = pd.to_datetime(volatility_data['date'])
            
        # Create volatility trend chart
        fig_vol = px.line(
            volatility_data,
            x="date",
            y="value",
            title="3-Month Rolling Volatility of Shipping Indices",
            labels={"value": "Volatility (Standard Deviation)", "date": "Date"},
            template="plotly_white"
        )
        fig_vol = apply_chart_styling(fig_vol)
        fig_vol.update_traces(line_color='#e74c3c', line_width=3)
        st.plotly_chart(fig_vol, use_container_width=True)
        
        # Volatility statistics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Current Volatility", f"{volatility_data['value'].iloc[-1]:.1f}")
        with col2:
            st.metric("Average Volatility", f"{volatility_data['value'].mean():.1f}")
        with col3:
            st.metric("Max Volatility", f"{volatility_data['value'].max():.1f}")
        with col4:
            st.metric("Min Volatility", f"{volatility_data['value'].min():.1f}")
        
        # Volatility insights
        current_vol = volatility_data['value'].iloc[-1]
        avg_vol = volatility_data['value'].mean()
        
        if current_vol > avg_vol * 1.2:
            st.warning("⚠️ **High Volatility Alert**: Current volatility is significantly above average, indicating increased market uncertainty.")
        elif current_vol < avg_vol * 0.8:
            st.success("✅ **Low Volatility**: Current volatility is below average, suggesting relative market stability.")
        else:
            st.info("ℹ️ **Normal Volatility**: Current volatility is within normal range.")
            
    else:
        st.markdown("""
        <div class="alert-box">
            <h4>⚠️ No Volatility Data Available</h4>
            <p>No valid volatility data is currently available.</p>
        </div>
        """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div class="alert-box">
        <h4>⚠️ No Volatility Data Available</h4>
        <p>No shipping index volatility data is currently available.</p>
    </div>
    """, unsafe_allow_html=True)

# AI-Powered Strategic Analysis
st.markdown('<div class="section-header"><h2>🌟 AI-Powered Strategic Intelligence</h2></div>', unsafe_allow_html=True)
if gemini_insight and gemini_insight != "No AI insights found.":
    sections = {
        "Core Trend": extract_section(gemini_insight, "### Core Trend", "### Hidden Effects"),
        "Hidden Effects": extract_section(gemini_insight, "### Hidden Effects", "### Strategic Recommendations"),
        "Strategic Recommendations": extract_section(gemini_insight, "### Strategic Recommendations", "### Risk Assessment"),
        "Risk Assessment": extract_section(gemini_insight, "### Risk Assessment", "### Market Intelligence"),
        "Market Intelligence": extract_section(gemini_insight, "### Market Intelligence")
    }
    tab_labels = ["📊 Core Trends", "🔍 Hidden Effects", "🎯 Strategic Recommendations", "⚠️ Risk Assessment", "📈 Market Intelligence"]
    tabs = st.tabs(tab_labels)
    for tab, (label, content) in zip(tabs, sections.items()):
        with tab:
            if content:
                st.markdown(f"### {label}")
                st.markdown(format_insight_text(content))
            else:
                st.info(f"No {label} insights available.")
    st.subheader("📊 AI Insight Summary")
    insight_metrics = {
        "Sections Available": len([s for s in sections.values() if s]),
        "Total Insight Length": len(gemini_insight),
        "Last Updated": datetime.now().strftime("%Y-%m-%d")
    }
    col1, col2, col3 = st.columns(3)
    for i, (key, value) in enumerate(insight_metrics.items()):
        with [col1, col2, col3][i]:
            st.metric(key, value)
else:
    st.markdown("""
    <div class="alert-box">
        <h4>🌟 AI Insights Unavailable</h4>
        <p>No AI-powered strategic insights are currently available. This could be due to:</p>
        <ul>
            <li>Insufficient data for analysis</li>
            <li>AI service configuration issues</li>
            <li>Data quality concerns</li>
        </ul>
        <p>Please check your data sources and AI service setup.</p>
    </div>
    """, unsafe_allow_html=True)

# Data Explorer
st.markdown('<div class="section-header"><h2>📄 Data Explorer</h2></div>', unsafe_allow_html=True)
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "⬇️ Top 5 Decrease Items", "⬆️ Top 5 Increase Items", "🌍 Top 5 Increase Countries", "🤝 Top 5 Trade Partners", "🚢 Shipping Index", "📊 Volatility Analysis"
])
with tab1:
    if not export_decrease_items_top5.empty:
        st.dataframe(export_decrease_items_top5, use_container_width=True)
        csv = export_decrease_items_top5.to_csv(index=False)
        st.download_button("Download CSV", csv, "export_decrease_items_top5.csv", "text/csv")
    else:
        st.info("No data available.")
with tab2:
    if not export_increase_items_top5.empty:
        st.dataframe(export_increase_items_top5, use_container_width=True)
        csv = export_increase_items_top5.to_csv(index=False)
        st.download_button("Download CSV", csv, "export_increase_items_top5.csv", "text/csv")
    else:
        st.info("No data available.")
with tab3:
    if not export_increase_countries_top5.empty:
        st.dataframe(export_increase_countries_top5, use_container_width=True)
        csv = export_increase_countries_top5.to_csv(index=False)
        st.download_button("Download CSV", csv, "export_increase_countries_top5.csv", "text/csv")
    else:
        st.info("No data available.")
with tab4:
    if not trade_partners_top5.empty:
        st.dataframe(trade_partners_top5, use_container_width=True)
        csv = trade_partners_top5.to_csv(index=False)
        st.download_button("Download CSV", csv, "trade_partners_top5.csv", "text/csv")
    else:
        st.info("No data available.")
with tab5:
    if not shipping_index_pivoted.empty:
        st.dataframe(shipping_index_pivoted, use_container_width=True)
        csv = shipping_index_pivoted.to_csv(index=False)
        st.download_button("Download CSV", csv, "shipping_index_pivoted.csv", "text/csv")
    else:
        st.info("No data available.")
with tab6:
    if not shipping_index_3m_volatility.empty:
        volatility_display = shipping_index_3m_volatility.dropna()
        if not volatility_display.empty:
            st.dataframe(volatility_display, use_container_width=True)
            csv = volatility_display.to_csv(index=False)
            st.download_button("Download CSV", csv, "shipping_index_3m_volatility.csv", "text/csv")
        else:
            st.info("No valid volatility data available.")
    else:
        st.info("No volatility data available.")

# Enhanced Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); border-radius: 15px; margin-top: 2rem;">
    <h3>🌏 Global Trade Intelligence Platform</h3>
    <p><strong>Data Sources:</strong> UN Comtrade, BDI, etc. | <strong>AI Powered by:</strong> Gemini AI</p>
    <p style="color: #6c757d; font-size: 0.9rem;">Comprehensive global trade analysis and strategic intelligence</p>
    <p style="color: #6c757d; font-size: 0.8rem;">Last updated: {}</p>
</div>
""".format(datetime.now().strftime("%Y-%m-%d %H:%M")), unsafe_allow_html=True)