"""
Custom UI components, styling helpers, and PyDeck interactive map visualization.
Sleek, luxury travel design system.
"""

import streamlit as st
import pandas as pd
import pydeck as pdk
from typing import Dict, Any, List


# Color palette for PyDeck day markers & routes
DAY_COLORS = [
    [224, 90, 71, 230],    # Day 1: Terracotta
    [15, 118, 110, 230],   # Day 2: Emerald Teal
    [217, 119, 6, 230],    # Day 3: Golden Amber
    [99, 102, 241, 230],   # Day 4: Indigo
    [236, 72, 153, 230],   # Day 5: Rose
    [14, 165, 233, 230],   # Day 6: Sky Blue
    [139, 92, 246, 230],   # Day 7: Violet
]


def render_brand_header():
    """Renders the top luxury brand navigation header."""
    st.markdown(
        """
        <div class="brand-header">
            <div>
                <div class="brand-logo">✈️ Roam<span>Craft</span></div>
                <div class="brand-tagline">Curated Luxury Journeys • Zero-Backtracking Geographic Clusters</div>
            </div>
            <div class="header-status-pill">
                <span>✨</span> AI Itinerary Concierge Active
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_budget_metric_tiles(itinerary: Dict[str, Any]):
    """Renders sleek consumer metric cards."""
    total_usd = itinerary.get("total_estimated_usd", 0.0)
    total_inr = itinerary.get("total_estimated_inr", 0.0)
    duration = max(1, itinerary.get("duration_days", 1))
    daily_usd = total_usd / duration
    daily_inr = total_inr / duration

    total_activities = sum(len(d.get("slots", {})) for d in itinerary.get("days", []))

    st.markdown(
        f"""
        <div class="metric-container">
            <div class="metric-card">
                <div class="metric-label">Estimated Trip Cost</div>
                <div class="metric-value" style="color: #e05a47;">${total_usd:,.0f}</div>
                <div class="metric-sub">₹{total_inr:,.0f} INR total</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Average Daily Spend</div>
                <div class="metric-value" style="color: #0f766e;">${daily_usd:,.0f}</div>
                <div class="metric-sub">₹{daily_inr:,.0f} / day</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Curated Activities</div>
                <div class="metric-value">{total_activities}</div>
                <div class="metric-sub">4 balanced slots per day</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Transit Efficiency</div>
                <div class="metric-value" style="color: #059669; font-size: 1.4rem;">Optimized</div>
                <div class="metric-sub">Geographically clustered</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_interactive_map(itinerary: Dict[str, Any]):
    """Renders a clean PyDeck map plotting activities and sequential cluster paths."""
    days = itinerary.get("days", [])
    records = []
    path_records = []

    for idx, day in enumerate(days):
        day_num = day.get("day_number", idx + 1)
        day_color = DAY_COLORS[(day_num - 1) % len(DAY_COLORS)]
        slots = day.get("slots", {})
        day_coords = []

        for slot_key, slot_name in [
            ("morning", "Morning"),
            ("lunch", "Lunch"),
            ("afternoon", "Afternoon"),
            ("evening", "Evening")
        ]:
            if slot_key in slots:
                s = slots[slot_key]
                lat = float(s.get("lat", 0.0))
                lng = float(s.get("lng", 0.0))
                if lat != 0.0 and lng != 0.0:
                    records.append({
                        "lat": lat,
                        "lng": lng,
                        "day": f"Day {day_num}",
                        "slot": slot_name,
                        "title": s.get("title", ""),
                        "category": s.get("category", ""),
                        "cost_usd": s.get("cost_usd", 0.0),
                        "cost_inr": s.get("cost_inr", 0.0),
                        "color": day_color,
                        "tooltip_text": f"<b>Day {day_num} • {slot_name}</b><br/>{s.get('title')}<br/><b>Est. Cost:</b> ${s.get('cost_usd', 0):.0f} USD (₹{s.get('cost_inr', 0):.0f})"
                    })
                    day_coords.append([lng, lat])

        if len(day_coords) >= 2:
            path_records.append({
                "path": day_coords,
                "day": f"Day {day_num}",
                "color": [day_color[0], day_color[1], day_color[2], 190]
            })

    if not records:
        return

    df = pd.DataFrame(records)
    avg_lat = df["lat"].mean()
    avg_lng = df["lng"].mean()

    scatter_layer = pdk.Layer(
        "ScatterplotLayer",
        data=df,
        get_position=["lng", "lat"],
        get_color="color",
        get_radius=180,
        radius_min_pixels=7,
        radius_max_pixels=18,
        pickable=True,
        auto_highlight=True,
    )

    layers = [scatter_layer]

    if path_records:
        path_df = pd.DataFrame(path_records)
        path_layer = pdk.Layer(
            "PathLayer",
            data=path_df,
            get_path="path",
            get_color="color",
            width_min_pixels=3,
            pickable=True
        )
        layers.append(path_layer)

    view_state = pdk.ViewState(
        latitude=avg_lat,
        longitude=avg_lng,
        zoom=12.2,
        pitch=25,
    )

    deck = pdk.Deck(
        layers=layers,
        initial_view_state=view_state,
        tooltip={
            "html": "{tooltip_text}",
            "style": {
                "backgroundColor": "#0f172a",
                "color": "#ffffff",
                "fontSize": "12px",
                "borderRadius": "10px",
                "padding": "10px 14px",
                "boxShadow": "0 8px 20px rgba(0,0,0,0.2)"
            }
        },
        map_style="light",
    )

    st.markdown("#### 🗺️ Route Map & Activity Trail")
    st.caption("Points and route lines are color-coded by day to demonstrate local walking and transit loops.")
    st.pydeck_chart(deck, use_container_width=True)


def render_slot_card(slot_key: str, slot_data: Dict[str, Any]):
    """Renders a sleek, elevated activity card."""
    time_str = slot_data.get("time", "")
    title = slot_data.get("title", "Activity")
    desc = slot_data.get("description", "")
    loc = slot_data.get("location_name", "")
    cost_usd = slot_data.get("cost_usd", 0.0)
    cost_inr = slot_data.get("cost_inr", 0.0)
    pro_tip = slot_data.get("pro_tip", "")
    dietary = slot_data.get("dietary_tags", "")

    slot_icons = {
        "morning": ("🌅", "Morning Sightseeing"),
        "lunch": ("🍽️", "Lunch Recommendation"),
        "afternoon": ("🏛️", "Afternoon Leisure & Immersion"),
        "evening": ("🌆", "Evening Dining & Nightlife"),
    }
    icon, label = slot_icons.get(slot_key, ("📍", slot_key.capitalize()))

    tip_html = f'<div class="tip-pill">💡 <b>Insider Tip:</b> {pro_tip}</div>' if pro_tip else ''
    diet_html = f'<div class="diet-pill">🥗 <b>Dining Note:</b> {dietary}</div>' if dietary else ''

    st.markdown(
        f"""
        <div class="slot-tile {slot_key}">
            <div class="slot-top-row">
                <div class="slot-phase-pill">
                    <span>{icon}</span> {label} • {time_str}
                </div>
                <div class="slot-price-pill">
                    ${cost_usd:,.0f} <span style="font-size: 0.8rem; font-weight: 500; color: #64748b;">(₹{cost_inr:,.0f})</span>
                </div>
            </div>
            <div class="slot-activity-title">{title}</div>
            <div class="slot-activity-desc">{desc}</div>
            <div class="slot-location-row">
                <b>📍 Location:</b>&nbsp;{loc}
            </div>
            {tip_html}
            {diet_html}
        </div>
        """,
        unsafe_allow_html=True
    )
