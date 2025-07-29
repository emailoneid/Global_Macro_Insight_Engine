import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os
from functools import lru_cache
import warnings
warnings.filterwarnings('ignore')

# Add the parent directory to Python path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.data_loader import load_agriculture_data

# Page Config
st.set_page_config(
    page_title="Agriculture Production Dashboard",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #2E8B57, #3CB371);
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
        height: 160px;
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
        font-size: 2rem;
        font-weight: 700;
        margin: 0.5rem 0;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #6c757d;
        font-weight: 500;
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
        border-left: 4px solid #28a745;
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
    <h1>🌾 Agriculture Production Dashboard</h1>
    <p>Comprehensive analysis of crop production trends, growth rates, and strategic insights</p>
</div>
""", unsafe_allow_html=True)

# Cache data loading for better performance
@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_cached_agriculture_data():
    """Load and cache agriculture data with error handling"""
    try:
        data = load_agriculture_data()
        return data
    except Exception as e:
        st.error(f"Error loading agriculture data: {str(e)}")
        return {}

# Helper Functions
def format_dates_for_display(df):
    """Format date columns to show only date without time component"""
    if not df.empty and 'date' in df.columns:
        df = df.copy()
        df['date'] = pd.to_datetime(df['date']).dt.date
    return df

def extract_section(text, start, end=None):
    """Extract section between start and end markers."""
    if start not in text:
        return ""
    section = text.split(start)[1]
    if end and end in section:
        section = section.split(end)[0]
    return section.strip()

def format_insight_text(text):
    """Clean AI text for better markdown rendering in Streamlit."""
    if not text:
        return ""
    lines = text.strip().split('\n')
    formatted = []

    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Ensure all bullet points are properly formatted
        if line.startswith("•"):
            # Remove the bullet point and check if it starts with a number
            clean_line = line[1:].strip()
            # Check if the line starts with a number followed by a period (more robust check)
            if clean_line and clean_line[0].isdigit() and len(clean_line) > 1 and clean_line[1] == '.':
                # For numbered items like "1. Supply Chain Disruptions"
                formatted.append(clean_line)
            elif ":" in line:
                # Check if it contains a colon (like "Defence: Record global...")
                parts = line.split(":", 1)
                if len(parts) == 2:
                    label = parts[0].strip()
                    content = parts[1].strip()
                    formatted.append(f"**{label}:** {content}")
                else:
                    formatted.append(line)
            else:
                formatted.append(line)
        
        # Handle emoji headers (🛠, 📊, 🎯, ⚠️, 📈, 📉, 🔄) - only if they're standalone headers
        elif any(emoji in line for emoji in ['🛠', '📊', '🎯', '⚠️', '📈', '📉', '🔄']) and ':' in line:
            # This is content within a section, not a header - don't bold it
            formatted.append(line)
        elif any(emoji in line for emoji in ['🛠', '📊', '🎯', '⚠️', '📈', '📉', '🔄']) and not ':' in line:
            # This is a standalone header - bold it
            formatted.append(f"\n**{line}**")
        
        # Handle numbered lists (don't add bullet points to them)
        elif line and line[0].isdigit() and len(line) > 1 and line[1] == '.':
            formatted.append(line)
        # Handle other lines that might need bullet points
        elif line and not line.startswith("-"):
            formatted.append(f"• {line}")
        else:
            formatted.append(line)
    
    return "\n\n".join(formatted)

def apply_chart_styling(fig, title_color="#2E8B57"):
    """Apply consistent styling to charts"""
    fig.update_layout(
        title_font_size=18,
        title_font_color=title_color,
        xaxis_title_font_size=14,
        yaxis_title_font_size=14,
        template="plotly_white",
        margin=dict(l=50, r=50, t=80, b=50),
        height=400
    )
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.1)')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.1)')
    return fig

def create_metric_card(title, value, subtitle="", color="#28a745"):
    """Create a styled metric card"""
    return f"""
    <div class="metric-card">
        <div class="metric-label">{title}</div>
        <div class="metric-value" style="color: {color};">{value}</div>
        <div class="metric-label">{subtitle}</div>
    </div>
    """

# Load Data
with st.spinner("Loading agriculture intelligence data..."):
    data = load_cached_agriculture_data()

# Extract data with error handling
trend_data = format_dates_for_display(data.get("trend", pd.DataFrame()))
yoy_data = format_dates_for_display(data.get("yoy", pd.DataFrame()))
growth_data = data.get("growth", pd.DataFrame())
corr_data = data.get("corr", pd.DataFrame())
key_insights = data.get("insights", {})
gemini_insight = data.get("gemini_insight", "No AI insights found.")
ready_data = data.get("ready", pd.DataFrame())

# Create combined analysis dataframe for filtering
combined_analysis = pd.DataFrame()
if not ready_data.empty:
    combined_analysis = ready_data.copy()
elif not trend_data.empty:
    # If ready_data is empty, use trend_data as base
    combined_analysis = trend_data.copy()

# Store original data for filtering
original_trend_data = trend_data.copy()
original_yoy_data = yoy_data.copy()
original_growth_data = growth_data.copy()
original_corr_data = corr_data.copy()

# Sidebar for filters and controls
st.sidebar.markdown("## 🎛️ Dashboard Controls")

# Date range filter
if not combined_analysis.empty and 'date' in combined_analysis.columns:
    try:
        min_date = pd.to_datetime(combined_analysis['date']).min()
        max_date = pd.to_datetime(combined_analysis['date']).max()
        
        st.sidebar.markdown("### 📅 Date Range")
        date_range = st.sidebar.date_input(
            "Select date range:",
            value=(min_date.date(), max_date.date()),
            min_value=min_date.date(),
            max_value=max_date.date()
        )
        
        if len(date_range) == 2:
            start_date, end_date = date_range
            # Apply date filter to all relevant datasets
            combined_analysis = combined_analysis[
                (pd.to_datetime(combined_analysis['date']).dt.date >= start_date) &
                (pd.to_datetime(combined_analysis['date']).dt.date <= end_date)
            ]
            
            # Filter trend data
            if not trend_data.empty and 'date' in trend_data.columns:
                trend_data = trend_data[
                    (pd.to_datetime(trend_data['date']).dt.date >= start_date) &
                    (pd.to_datetime(trend_data['date']).dt.date <= end_date)
                ]
            
            # Filter YoY data
            if not yoy_data.empty and 'date' in yoy_data.columns:
                yoy_data = yoy_data[
                    (pd.to_datetime(yoy_data['date']).dt.date >= start_date) &
                    (pd.to_datetime(yoy_data['date']).dt.date <= end_date)
                ]
    except Exception as e:
        st.sidebar.warning(f"Date filtering error: {str(e)}")

# Commodity filter
if not combined_analysis.empty and 'commodity' in combined_analysis.columns:
    st.sidebar.markdown("### 🌾 Commodity Filter")
    all_commodities = list(combined_analysis['commodity'].unique())
    select_all_label = "Select All"
    multiselect_options = [select_all_label] + all_commodities

    # Default selection - only "Select All" is selected by default
    default_selection = [select_all_label]

    selected = st.sidebar.multiselect(
        "Select commodities:",
        options=multiselect_options,
        default=default_selection,
        key="commodity_multiselect"
    )

    if select_all_label in selected:
        # If "Select All" is selected, ignore individual selections and use all commodities
        selected_commodities = all_commodities
    else:
        # If "Select All" is not selected, use only the individually selected commodities
        selected_commodities = [c for c in selected if c in all_commodities]

    if selected_commodities:
        # Apply commodity filter to all relevant datasets
        combined_analysis = combined_analysis[combined_analysis['commodity'].isin(selected_commodities)]
        
        # Filter YoY data by commodity
        if not yoy_data.empty and 'commodity' in yoy_data.columns:
            yoy_data = yoy_data[yoy_data['commodity'].isin(selected_commodities)]
        
        # Filter growth data by commodity
        if not growth_data.empty and 'Commodity' in growth_data.columns:
            growth_data = growth_data[growth_data['Commodity'].isin(selected_commodities)]
        
        # Filter correlation data (keep only selected commodities and their correlations)
        if not corr_data.empty:
            # Keep only selected commodities
            available_commodities = [c for c in selected_commodities if c in corr_data.columns]
            if available_commodities:
                corr_data = corr_data[available_commodities].loc[available_commodities]

# Filter status indicator
st.sidebar.markdown("### 📊 Filter Status")
active_filters = []

# Check date filter
if 'date_range' in locals() and len(date_range) == 2:
    if 'min_date' in locals() and 'max_date' in locals():
        if date_range[0] != min_date.date() or date_range[1] != max_date.date():
            active_filters.append(f"Date: {date_range[0]} to {date_range[1]}")

# Check commodity filter
if 'selected_commodities' in locals() and selected_commodities:
    if len(selected_commodities) == len(all_commodities) + 1: # +1 for "Select All"
        active_filters.append(f"Commodities: All ({len(selected_commodities) - 1})")
    else:
        active_filters.append(f"Commodities: {len(selected_commodities) - 1} selected")

if active_filters:
    st.sidebar.success(f"✅ Active filters: {len(active_filters)}")
    for filter_info in active_filters:
        st.sidebar.info(f"• {filter_info}")
else:
    st.sidebar.info("ℹ️ No filters applied")

# Key Metrics with enhanced styling
st.markdown('<div class="section-header"><h2>📊 Key Performance Metrics</h2></div>', unsafe_allow_html=True)

# Dynamically calculate metrics from filtered growth_data
if not growth_data.empty and 'Commodity' in growth_data.columns and 'CAGR (%)' in growth_data.columns:
    # Top Performer
    top_performer_row = growth_data.loc[growth_data['CAGR (%)'].idxmax()]
    top_performer = top_performer_row['Commodity']
    peak_growth = top_performer_row['CAGR (%)']
    avg_growth = growth_data['CAGR (%)'].mean()
    total_commodities = len(growth_data)
else:
    top_performer = "N/A"
    peak_growth = 0
    avg_growth = 0
    total_commodities = 0

# Get last date from available data
last_date = "N/A"
if not combined_analysis.empty and 'date' in combined_analysis.columns:
    try:
        last_date = pd.to_datetime(combined_analysis['date']).max().strftime("%Y-%m-%d")
    except:
        last_date = "N/A"
elif not trend_data.empty and 'date' in trend_data.columns:
    try:
        last_date = pd.to_datetime(trend_data['date']).max().strftime("%Y-%m-%d")
    except:
        last_date = "N/A"
elif not yoy_data.empty and 'date' in yoy_data.columns:
    try:
        last_date = pd.to_datetime(yoy_data['date']).max().strftime("%Y-%m-%d")
    except:
        last_date = "N/A"

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown(create_metric_card(
        "🏆 Top Performer",
        top_performer,
        "Best performing commodity",
        "#28a745"
    ), unsafe_allow_html=True)

with col2:
    st.markdown(create_metric_card(
        "📈 Peak Growth",
        f"{peak_growth:.1f}%",
        "Maximum growth rate",
        "#007bff"
    ), unsafe_allow_html=True)

with col3:
    st.markdown(create_metric_card(
        "📊 Average Growth",
        f"{avg_growth:.1f}%",
        "Mean growth rate",
        "#ffc107"
    ), unsafe_allow_html=True)

with col4:
    st.markdown(create_metric_card(
        "🌾 Total Commodities",
        f"{total_commodities}",
        "Analyzed commodities",
        "#6f42c1"
    ), unsafe_allow_html=True)

with col5:
    st.markdown(create_metric_card(
        "📅 Last Update",
        last_date,
        "Most recent data",
        "#17a2b8"
    ), unsafe_allow_html=True)

# Production Trends with enhanced visualization
st.markdown('<div class="section-header"><h2>📈 Production Trends Analysis</h2></div>', unsafe_allow_html=True)

if not trend_data.empty and len(trend_data.columns) > 1:
    # Add "All Commodities" option
    all_options = ["All Commodities"] + list(trend_data.columns[1:])
    selected_commodities = st.multiselect(
        "Select Commodities for Trend Analysis",
        options=all_options,
        default=["All Commodities"]
    )
    
    if selected_commodities:
        if "All Commodities" in selected_commodities:
            # Show all commodities
            commodities_to_plot = trend_data.columns[1:]
        else:
            # Show selected commodities
            commodities_to_plot = selected_commodities
        
        # Enhanced line chart with better styling
        fig_trend = px.line(
            trend_data,
            x="date",
            y=commodities_to_plot,
            title="Commodity Production Trends Over Time",
            labels={"value": "Production Volume", "date": "Year"},
            color_discrete_sequence=px.colors.qualitative.Set3,
            template="plotly_white"
        )
        
        fig_trend = apply_chart_styling(fig_trend)
        fig_trend.update_layout(
            hovermode='x unified',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        st.plotly_chart(fig_trend, use_container_width=True)
    else:
        st.warning("Please select at least one commodity to view trends.")
else:
    st.markdown("""
    <div class="alert-box">
        <h4>⚠️ No Trend Data Available</h4>
        <p>No production trend data is currently available. Please check your data sources or try refreshing the dashboard.</p>
    </div>
    """, unsafe_allow_html=True)

# Growth Rate Analysis with enhanced visualization
st.markdown('<div class="section-header"><h2>🚀 Growth Performance Analysis</h2></div>', unsafe_allow_html=True)

if not growth_data.empty:
    sorted_growth = growth_data.sort_values("CAGR (%)", ascending=False)
    
    # Enhanced bar chart
    fig_growth = px.bar(
        sorted_growth,
        x="Commodity",
        y="CAGR (%)",
        title="Compound Annual Growth Rate (CAGR) by Commodity",
        color="CAGR (%)",
        color_continuous_scale="RdYlGn",
        template="plotly_white"
    )
    
    fig_growth = apply_chart_styling(fig_growth)
    st.plotly_chart(fig_growth, use_container_width=True)
    
    # Enhanced data table
    st.subheader("📋 Detailed Growth Statistics")
    styled_growth = sorted_growth.style.background_gradient(subset=['CAGR (%)'], cmap='RdYlGn')
    st.dataframe(styled_growth, use_container_width=True)
else:
    st.markdown("""
    <div class="alert-box">
        <h4>⚠️ No Growth Rate Data Available</h4>
        <p>No growth rate analysis data is currently available. This could be due to insufficient historical data or processing issues.</p>
    </div>
    """, unsafe_allow_html=True)

# YoY Changes with enhanced visualization
st.markdown('<div class="section-header"><h2>🔄 Year-over-Year Performance</h2></div>', unsafe_allow_html=True)

if not yoy_data.empty and 'commodity' in yoy_data.columns:
    # Enhanced multi-line chart showing all filtered commodities
    fig_yoy = px.line(
        yoy_data,
        x="date",
        y="yoy_change",
        color="commodity",
        title="Year-over-Year Change for Selected Commodities",
        labels={"yoy_change": "YoY Change (%)", "date": "Year"},
        color_discrete_sequence=px.colors.qualitative.Pastel,
        template="plotly_white"
    )
    
    fig_yoy = apply_chart_styling(fig_yoy)
    st.plotly_chart(fig_yoy, use_container_width=True)
    
    # Show YoY statistics for selected commodities
    if len(yoy_data['commodity'].unique()) > 1:
        st.subheader("📊 YoY Statistics by Commodity")
        yoy_stats = yoy_data.groupby('commodity')['yoy_change'].agg(['mean', 'std', 'min', 'max']).round(2)
        yoy_stats.columns = ['Average YoY (%)', 'Std Dev (%)', 'Min YoY (%)', 'Max YoY (%)']
        st.dataframe(yoy_stats, use_container_width=True)
else:
    st.markdown("""
    <div class="alert-box">
        <h4>⚠️ No YoY Data Available</h4>
        <p>No year-over-year comparison data is currently available. This could be due to insufficient historical data or processing issues.</p>
    </div>
    """, unsafe_allow_html=True)

# Correlation Matrix with enhanced visualization
st.markdown('<div class="section-header"><h2>🔗 Commodity Correlation Analysis</h2></div>', unsafe_allow_html=True)

if not corr_data.empty:
    # Calculate dynamic color scale based on actual data range
    corr_min = corr_data.min().min()
    corr_max = corr_data.max().max()
    
    # Ensure we have a reasonable range for visualization
    if corr_max - corr_min < 0.1:  # If range is too small, expand it
        corr_min = max(-1, corr_min - 0.1)
        corr_max = min(1, corr_max + 0.1)
    
    # Enhanced correlation heatmap with dynamic color scale
    fig_corr = px.imshow(
        corr_data,
        title="Correlation Matrix Between Commodities",
        color_continuous_scale="RdBu_r",
        zmin=corr_min,
        zmax=corr_max,
        aspect="auto",
        template="plotly_white"
    )
    
    fig_corr = apply_chart_styling(fig_corr)
    fig_corr.update_layout(height=600)
    fig_corr.update_xaxes(tickangle=-45)
    
    st.plotly_chart(fig_corr, use_container_width=True)
    
    # Enhanced correlation insights with actual data range
    st.info(f"💡 **Correlation Insights**: Values range from {corr_min:.2f} to {corr_max:.2f}. Values closer to {corr_max:.2f} indicate strong positive correlation, while values closer to {corr_min:.2f} indicate strong negative correlation.")
    
    # Add correlation statistics
    st.subheader("📊 Correlation Statistics")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Average Correlation", f"{corr_data.mean().mean():.3f}")
    with col2:
        st.metric("Min Correlation", f"{corr_min:.3f}")
    with col3:
        st.metric("Max Correlation", f"{corr_max:.3f}")
else:
    st.markdown("""
    <div class="alert-box">
        <h4>⚠️ No Correlation Data Available</h4>
        <p>No correlation analysis data is currently available. This could be due to insufficient data points or processing issues.</p>
    </div>
    """, unsafe_allow_html=True)

# AI-Powered Strategic Analysis with enhanced styling
st.markdown('<div class="section-header"><h2>🌟 AI-Powered Strategic Intelligence</h2></div>', unsafe_allow_html=True)

if gemini_insight and gemini_insight != "No AI insights found.":
    # Extract sections
    sections = {
        "Core Trend": extract_section(gemini_insight, "### Core Trend", "### Hidden Effects"),
        "Hidden Effects": extract_section(gemini_insight, "### Hidden Effects", "### Strategic Recommendations"),
        "Strategic Recommendations": extract_section(gemini_insight, "### Strategic Recommendations", "### Risk Assessment"),
        "Risk Assessment": extract_section(gemini_insight, "### Risk Assessment", "### Market Intelligence"),
        "Market Intelligence": extract_section(gemini_insight, "### Market Intelligence")
    }

    # Create tabs with enhanced styling
    tab_labels = ["📊 Core Trends", "🔍 Hidden Effects", "🎯 Strategic Recommendations", "⚠️ Risk Assessment", "📈 Market Intelligence"]
    tabs = st.tabs(tab_labels)

    for tab, (label, content) in zip(tabs, sections.items()):
        with tab:
            if content:
                st.markdown(f"### {label}")
                st.markdown(format_insight_text(content))
            else:
                st.info(f"No {label} insights available.")
    
    # Summary metrics
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

# Enhanced Raw Data Preview (Data Explorer) - moved below AI section
st.markdown('<div class="section-header"><h2>📄 Data Explorer</h2></div>', unsafe_allow_html=True)

if not ready_data.empty:
    ready_data_display = format_dates_for_display(ready_data)
    with st.expander("📊 Interactive Data Analysis", expanded=False):
        # Export functionality in top right corner
        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
        with col4:
            if st.button("📥 Export Data", type="primary"):
                csv = ready_data_display.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=f"agriculture_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
        
        # Add search and filter capabilities
        search_term = st.text_input("🔍 Search data:", placeholder="Enter commodity name...")
        
        if search_term:
            filtered_data = ready_data_display[
                ready_data_display.apply(lambda x: x.astype(str).str.contains(search_term, case=False, na=False)).any(axis=1)
            ]
        else:
            filtered_data = ready_data_display
        
        # Add pagination
        page_size = st.selectbox("📄 Records per page:", [10, 25, 50, 100], index=0)
        total_records = len(filtered_data)
        total_pages = (total_records + page_size - 1) // page_size
        
        if total_pages > 1:
            page = st.selectbox("📖 Page:", range(1, total_pages + 1), index=0) - 1
            start_idx = page * page_size
            end_idx = min(start_idx + page_size, total_records)
            display_data = filtered_data.iloc[start_idx:end_idx]
        else:
            display_data = filtered_data
        
        st.dataframe(display_data, use_container_width=True)
        st.caption(f"Showing {len(display_data)} of {total_records} records")
else:
    st.markdown("""
    <div class="alert-box">
        <h4>⚠️ No Raw Data Available</h4>
        <p>No raw agriculture data is currently available for preview. Please check your data sources or try refreshing the dashboard.</p>
    </div>
    """, unsafe_allow_html=True)

# Enhanced Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); border-radius: 15px; margin-top: 2rem;">
    <h3>🌾 Agriculture Intelligence Platform</h3>
    <p><strong>Data Sources:</strong> U.S. Department of Agriculture | <strong>AI Powered by:</strong> Gemini AI</p>
    <p style="color: #6c757d; font-size: 0.9rem;">Comprehensive agriculture production analysis and strategic intelligence</p>
    <p style="color: #6c757d; font-size: 0.8rem;">Last updated: {}</p>
</div>
""".format(datetime.now().strftime("%Y-%m-%d %H:%M")), unsafe_allow_html=True)
