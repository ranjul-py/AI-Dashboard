import streamlit as st
import pandas as pd
import numpy as np
from database.db_manager import DBManager
from components.styles import inject_styles
from components.charts import plot_revenue_profit_trend, plot_profit_margin_trend, plot_revenue_forecast
from utils.helpers import format_currency

def get_forecast(historical_df: pd.DataFrame, horizon: int = 3, growth_modifier: float = 0.0) -> pd.DataFrame:
    """
    Performs a simple linear regression forecasting on revenue data.
    Allows adjustment using a growth modifier (percentage change to the slope).
    """
    df = historical_df.sort_values('month').reset_index(drop=True)
    n = len(df)
    if n < 2:
        return pd.DataFrame(columns=['month', 'revenue'])
        
    x = np.arange(n)
    y = df['revenue'].values
    
    # Fit linear regression line: y = mx + c
    slope, intercept = np.polyfit(x, y, 1)
    
    # Apply user-selected growth modifier to the slope
    adjusted_slope = slope * (1 + growth_modifier)
    
    # Generate future dates
    last_month_str = df.iloc[-1]['month']
    last_date = pd.to_datetime(last_month_str + "-01")
    
    future_months = []
    future_revenues = []
    future_low = []
    future_high = []
    
    # Standard error for confidence interval
    residuals = y - (slope * x + intercept)
    std_error = np.std(residuals) if len(residuals) > 2 else y.mean() * 0.05
    
    for i in range(1, horizon + 1):
        future_date = last_date + pd.DateOffset(months=i)
        future_months.append(future_date.strftime('%Y-%m'))
        
        # Calculate forecasted revenue
        future_idx = n + i - 1
        predicted_rev = adjusted_slope * future_idx + intercept
        # Keep revenue positive
        predicted_rev = max(500000.0, predicted_rev)
        future_revenues.append(predicted_rev)
        
        # 95% Confidence Interval bounds
        future_low.append(max(200000.0, predicted_rev - 1.96 * std_error * np.sqrt(1 + 1/n)))
        future_high.append(predicted_rev + 1.96 * std_error * np.sqrt(1 + 1/n))
        
    forecast_df = pd.DataFrame({
        'month': future_months,
        'revenue': future_revenues,
        'low_bound': future_low,
        'high_bound': future_high
    })
    
    return forecast_df

def show_revenue_page():
    if not st.session_state.get("authenticated", False):
        st.warning("⚠️ Access Denied. Please authenticate via the Main Portal.")
        st.stop()

    inject_styles()
    
    st.title("📊 Revenue Analytics")
    st.markdown("### Historical Financials & Predictive Revenue Forecasts")
    
    db = DBManager()
    df_rev = db.get_table_dataframe("revenue").sort_values('month')
    
    if df_rev.empty:
        st.warning("No revenue data found in the database. Run the ETL pipeline first.")
        return
        
    # Filters
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("⚙️ Scenario Modeling Filters")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        date_range = st.multiselect(
            "Filter Months",
            options=df_rev['month'].tolist(),
            default=df_rev['month'].tolist(),
            help="Select months to include in trends."
        )
    with col2:
        forecast_horizon = st.slider(
            "Forecast Horizon (Months)",
            min_value=1,
            max_value=6,
            value=3,
            help="Number of future months to project."
        )
    with col3:
        growth_modifier = st.slider(
            "Growth Adjustment (%)",
            min_value=-15,
            max_value=15,
            value=0,
            step=1,
            help="Simulates scaling factors (market growth/retraction) on the forecast slope."
        ) / 100.0
        
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Apply date range filter
    filtered_df = df_rev[df_rev['month'].isin(date_range)].sort_values('month')
    
    if filtered_df.empty:
        st.warning("No data matches the selected month filter.")
        return
        
    # 1. Main Charts Row
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    fig_trend = plot_revenue_profit_trend(filtered_df)
    st.plotly_chart(fig_trend, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        # Profit Margins
        fig_margin = plot_profit_margin_trend(filtered_df)
        st.plotly_chart(fig_margin, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col_b:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("Quarterly Aggregation Table")
        
        # Calculate Quarterly trends
        df_q = filtered_df.copy()
        # Parse month to Date, extract Quarter
        dates = pd.to_datetime(df_q['month'] + "-01")
        df_q['quarter'] = dates.dt.to_period('Q').astype(str)
        
        q_summary = df_q.groupby('quarter').agg({
            'revenue': 'sum',
            'profit': 'sum'
        }).reset_index()
        
        q_summary['profit_margin'] = (q_summary['profit'] / q_summary['revenue']) * 100
        
        # Format table for display
        q_disp = q_summary.copy()
        q_disp['revenue'] = q_disp['revenue'].apply(format_currency)
        q_disp['profit'] = q_disp['profit'].apply(format_currency)
        q_disp['profit_margin'] = q_disp['profit_margin'].apply(lambda x: f"{x:.2f}%")
        q_disp.columns = ["Quarter", "Total Revenue", "Net Profit", "Avg Margin"]
        
        st.dataframe(q_disp, hide_index=True, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
    # 2. Forecasting Section
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("🔮 Predictive Revenue Forecasting Scenario")
    
    forecast_df = get_forecast(filtered_df, horizon=forecast_horizon, growth_modifier=growth_modifier)
    fig_forecast = plot_revenue_forecast(filtered_df, forecast_df)
    st.plotly_chart(fig_forecast, use_container_width=True)
    
    # Display forecast summary data
    cols = st.columns(len(forecast_df))
    for idx, row in forecast_df.iterrows():
        with cols[idx]:
            m = row['month']
            v = row['revenue']
            l = row['low_bound']
            h = row['high_bound']
            st.metric(
                label=f"Projected: {m}",
                value=format_currency(v),
                delta=f"Range: {format_currency(l)} - {format_currency(h)}",
                delta_color="normal"
            )
            
    st.markdown('</div>', unsafe_allow_html=True)

show_revenue_page()
