import streamlit as st

def render_kpi_card(title: str, value: str, delta: str = "", delta_type: str = "neutral", icon: str = "📈", status: str = "normal"):
    """
    Returns the HTML string for a single glassmorphic, animated KPI card.
    
    Parameters:
    - title: The label/title of the metric.
    - value: The main number/metric string to display.
    - delta: Small supporting trend text (e.g. "+12% vs last month").
    - delta_type: "positive" (green), "negative" (red), or "neutral" (gray) for trend coloring.
    - icon: Emoji icon to display in the top right.
    - status: Accent border styling -> "normal" (blue), "success" (green), "warning" (amber), "danger" (red).
    """
    status_class = ""
    if status == "success":
        status_class = "success"
    elif status == "warning":
        status_class = "warning"
    elif status == "danger":
        status_class = "danger"
        
    delta_class = "neutral"
    if delta_type == "positive":
        delta_class = "positive"
    elif delta_type == "negative":
        delta_class = "negative"
        
    delta_symbol = ""
    if delta_type == "positive":
        delta_symbol = "▲ "
    elif delta_type == "negative":
        delta_symbol = "▼ "

    html = f"""
    <div class="kpi-card {status_class}">
        <div class="kpi-icon">{icon}</div>
        <div class="kpi-title">{title}</div>
        <div class="kpi-value">{value}</div>
        {f'<div class="kpi-delta {delta_class}">{delta_symbol}{delta}</div>' if delta else ''}
    </div>
    """
    return html

def render_kpi_grid(cards_list: list, cols_per_row: int = 3):
    """
    Renders a list of KPI cards in a responsive grid using Streamlit layout columns.
    
    Each card dict in cards_list should contain:
    - title, value
    - delta (optional)
    - delta_type (optional)
    - icon (optional)
    - status (optional)
    """
    # Group cards by cols_per_row
    for i in range(0, len(cards_list), cols_per_row):
        row_cards = cards_list[i:i+cols_per_row]
        cols = st.columns(len(row_cards))
        for idx, card in enumerate(row_cards):
            with cols[idx]:
                card_html = render_kpi_card(
                    title=card.get("title", ""),
                    value=card.get("value", ""),
                    delta=card.get("delta", ""),
                    delta_type=card.get("delta_type", "neutral"),
                    icon=card.get("icon", "📈"),
                    status=card.get("status", "normal")
                )
                st.markdown(card_html, unsafe_allow_html=True)
