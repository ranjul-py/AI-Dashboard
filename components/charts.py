import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# Default chart layout configuration for transparent glassmorphic look
CHART_THEME_LAYOUT = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(family="Inter, sans-serif", color="#E2E8F0", size=11),
    margin=dict(l=40, r=20, t=40, b=40),
    xaxis=dict(
        gridcolor='rgba(255,255,255,0.05)',
        linecolor='rgba(255,255,255,0.1)',
        tickfont=dict(color="#94A3B8"),
        showgrid=True
    ),
    yaxis=dict(
        gridcolor='rgba(255,255,255,0.05)',
        linecolor='rgba(255,255,255,0.1)',
        tickfont=dict(color="#94A3B8"),
        showgrid=True
    ),
    legend=dict(
        font=dict(color="#E2E8F0"),
        bgcolor='rgba(15,23,42,0.6)',
        bordercolor='rgba(255,255,255,0.08)',
        borderwidth=1
    )
)

COLOR_PALETTE = {
    "blue": "#38BDF8",
    "cobalt": "#0284C7",
    "indigo": "#6366F1",
    "success": "#10B981",
    "warning": "#F59E0B",
    "danger": "#EF4444",
    "gray": "#64748B",
    "purple": "#A855F7"
}

def plot_revenue_profit_trend(df: pd.DataFrame) -> go.Figure:
    """Grouped bar (Revenue) and line (Profit) chart."""
    fig = go.Figure()
    
    # Revenue Bar
    fig.add_trace(go.Bar(
        x=df['month'],
        y=df['revenue'],
        name='Revenue',
        marker_color=COLOR_PALETTE['blue'],
        opacity=0.85,
        text=df['revenue'].apply(lambda x: f"${x/1e6:.2f}M"),
        textposition='outside'
    ))
    
    # Profit Line
    fig.add_trace(go.Scatter(
        x=df['month'],
        y=df['profit'],
        name='Profit',
        mode='lines+markers',
        line=dict(color=COLOR_PALETTE['success'], width=3),
        marker=dict(size=8, color=COLOR_PALETTE['success']),
        text=df['profit'].apply(lambda x: f"${x/1e6:.2f}M")
    ))
    
    fig.update_layout(
        title="Monthly Revenue & Profit Trend",
        barmode='group',
        **CHART_THEME_LAYOUT
    )
    # Increase y-axis limit slightly for text labels
    max_val = max(df['revenue'].max(), df['profit'].max()) * 1.15
    fig.update_yaxes(range=[0, max_val])
    return fig

def plot_profit_margin_trend(df: pd.DataFrame) -> go.Figure:
    """Line chart displaying profit margin percentage over time."""
    df_copy = df.copy()
    df_copy['margin_pct'] = (df_copy['profit'] / df_copy['revenue']) * 100
    
    fig = px.line(
        df_copy,
        x='month',
        y='margin_pct',
        title='Monthly Profit Margin Trend (%)',
        markers=True
    )
    fig.update_traces(
        line=dict(color=COLOR_PALETTE['purple'], width=3),
        marker=dict(size=8)
    )
    fig.update_layout(**CHART_THEME_LAYOUT)
    fig.update_yaxes(ticksuffix="%", range=[0, 100])
    return fig

def plot_revenue_forecast(historical_df: pd.DataFrame, forecast_df: pd.DataFrame) -> go.Figure:
    """Historical vs Forecast Revenue Line Chart."""
    fig = go.Figure()
    
    # Historical Revenue
    fig.add_trace(go.Scatter(
        x=historical_df['month'],
        y=historical_df['revenue'],
        name='Historical Revenue',
        mode='lines+markers',
        line=dict(color=COLOR_PALETTE['blue'], width=3),
        marker=dict(size=6)
    ))
    
    # Forecast Revenue (Dashed)
    fig.add_trace(go.Scatter(
        x=forecast_df['month'],
        y=forecast_df['revenue'],
        name='Forecast Revenue',
        mode='lines+markers',
        line=dict(color=COLOR_PALETTE['indigo'], width=3, dash='dash'),
        marker=dict(size=6, color=COLOR_PALETTE['indigo'])
    ))
    
    # Optional Forecast Range (Confidence interval)
    if 'low_bound' in forecast_df.columns and 'high_bound' in forecast_df.columns:
        fig.add_trace(go.Scatter(
            x=pd.concat([forecast_df['month'], forecast_df['month'][::-1]]),
            y=pd.concat([forecast_df['high_bound'], forecast_df['low_bound'][::-1]]),
            fill='toself',
            fillcolor='rgba(99, 102, 241, 0.15)',
            line=dict(color='rgba(255,255,255,0)'),
            hoverinfo="skip",
            showlegend=False,
            name='Confidence Interval'
        ))
        
    fig.update_layout(
        title="Revenue Performance Forecast",
        **CHART_THEME_LAYOUT
    )
    return fig

def plot_project_completion_status(df: pd.DataFrame) -> go.Figure:
    """Horizontal bar chart showing project completion % and delay indicators."""
    fig = go.Figure()
    
    # Completion Bar
    fig.add_trace(go.Bar(
        y=df['project_name'],
        x=df['completion_pct'],
        name='Completion %',
        orientation='h',
        marker_color=df['status'].map({
            'On Track': COLOR_PALETTE['success'],
            'At Risk': COLOR_PALETTE['warning'],
            'Delayed': COLOR_PALETTE['danger']
        }).fillna(COLOR_PALETTE['blue']),
        text=df['completion_pct'].apply(lambda x: f"{x}%"),
        textposition='inside'
    ))
    
    fig.update_layout(
        title="Project Completion Status (%)",
        **CHART_THEME_LAYOUT
    )
    fig.update_xaxes(range=[0, 100], ticksuffix="%")
    return fig

def plot_project_risk_bubble(df: pd.DataFrame) -> go.Figure:
    """Bubble chart: Completion (X) vs Delay Days (Y), Budget (Size), Risk Score (Color)."""
    # Calculate Risk Score
    df_copy = df.copy()
    df_copy['risk_score'] = (df_copy['delay_days'] * 1.5) + (100 - df_copy['completion_pct']) * 0.5
    df_copy.loc[df_copy['status'] == 'At Risk', 'risk_score'] += 30
    df_copy.loc[df_copy['status'] == 'Delayed', 'risk_score'] += 50
    df_copy['risk_score'] = df_copy['risk_score'].clip(upper=100)
    
    fig = px.scatter(
        df_copy,
        x="completion_pct",
        y="delay_days",
        size="budget",
        color="risk_score",
        hover_name="project_name",
        title="Project Risk Mapping Portfolio",
        labels={
            "completion_pct": "Completion (%)",
            "delay_days": "Delay (Days)",
            "risk_score": "Risk Level Score",
            "budget": "Budget ($)"
        },
        size_max=40,
        color_continuous_scale=[
            [0.0, COLOR_PALETTE['success']],
            [0.5, COLOR_PALETTE['warning']],
            [1.0, COLOR_PALETTE['danger']]
        ]
    )
    
    fig.update_layout(**CHART_THEME_LAYOUT)
    fig.update_coloraxes(colorbar=dict(title=dict(text="Risk Score", font=dict(color="#E2E8F0")), tickfont=dict(color="#E2E8F0")))
    return fig

def plot_workforce_distribution(df: pd.DataFrame) -> go.Figure:
    """Donut chart for department headcount distribution."""
    dept_counts = df[df['status'] == 'Active']['department'].value_counts().reset_index()
    dept_counts.columns = ['department', 'count']
    
    fig = px.pie(
        dept_counts,
        names='department',
        values='count',
        hole=0.45,
        title='Departmental Headcount Distribution',
        color_discrete_sequence=[
            COLOR_PALETTE['blue'], 
            COLOR_PALETTE['indigo'], 
            COLOR_PALETTE['success'],
            COLOR_PALETTE['purple'],
            COLOR_PALETTE['warning']
        ]
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(**CHART_THEME_LAYOUT)
    return fig

def plot_workforce_utilization(df: pd.DataFrame) -> go.Figure:
    """Horizontal bar chart showing average utilization rate by department."""
    active_df = df[df['status'] == 'Active']
    dept_util = active_df.groupby('department')['utilization_pct'].mean().reset_index()
    
    fig = px.bar(
        dept_util,
        x='utilization_pct',
        y='department',
        orientation='h',
        title='Average Department Utilization Rate (%)',
        labels={'utilization_pct': 'Avg Utilization %', 'department': 'Department'},
        text='utilization_pct'
    )
    
    fig.update_traces(
        marker_color=COLOR_PALETTE['indigo'],
        texttemplate='%{x:.1f}%',
        textposition='outside'
    )
    fig.update_layout(**CHART_THEME_LAYOUT)
    fig.update_xaxes(range=[0, 110], ticksuffix="%")
    return fig

def plot_partner_funnel(df: pd.DataFrame) -> go.Figure:
    """Plotly funnel chart representing partner sales pipeline stages."""
    # Process stage order: Qualified -> Proposal Sent -> Negotiation -> Won/Lost
    stage_order = ['Qualified', 'Proposal Sent', 'Negotiation', 'Won', 'Lost']
    
    # Aggregate values per stage
    stage_val = df.groupby('status')['pipeline_value'].sum().reindex(stage_order).fillna(0.0).reset_index()
    
    fig = go.Figure(go.Funnel(
        y=stage_val['status'],
        x=stage_val['pipeline_value'],
        textinfo="value+percent initial",
        marker=dict(color=[
            COLOR_PALETTE['blue'],
            COLOR_PALETTE['indigo'],
            COLOR_PALETTE['purple'],
            COLOR_PALETTE['success'],
            COLOR_PALETTE['gray']
        ]),
        connector=dict(fillcolor="rgba(255,255,255,0.05)")
    ))
    
    fig.update_layout(
        title="Partner Sales Funnel Value Distribution",
        **CHART_THEME_LAYOUT
    )
    return fig

def plot_client_satisfaction(df: pd.DataFrame) -> go.Figure:
    """Scatter matrix mapping NPS (X) vs CSAT (Y), showing retention risks."""
    fig = px.scatter(
        df,
        x="nps",
        y="csat",
        color="retention_status",
        hover_name="client_name",
        text="client_name",
        title="Client Satisfaction & Sentiment Matrix (NPS vs CSAT)",
        labels={"nps": "Net Promoter Score (NPS)", "csat": "CSAT (out of 10)", "retention_status": "Retention Status"},
        color_discrete_map={
            "Retained": COLOR_PALETTE['success'],
            "At Risk": COLOR_PALETTE['danger']
        }
    )
    fig.update_traces(marker=dict(size=14), textposition="top center")
    
    # Add quadrants/reference lines
    fig.add_vline(x=50, line_dash="dash", line_color="rgba(255,255,255,0.2)", line_width=1)
    fig.add_hline(y=7.5, line_dash="dash", line_color="rgba(255,255,255,0.2)", line_width=1)
    
    fig.update_layout(**CHART_THEME_LAYOUT)
    fig.update_xaxes(range=[20, 85])
    fig.update_yaxes(range=[5.0, 10.0])
    return fig
