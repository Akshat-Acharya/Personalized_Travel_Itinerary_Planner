"""
RoamCraft AI — Autonomous Luxury Travel Itinerary Designer.
Sleek, modern, and aesthetically elevated single-canvas travel platform.
Zero sidebar, zero API key clutter on frontend, 100% dynamic AI.
"""

import streamlit as st
from datetime import date, timedelta
import os

# Safely load local .env if python-dotenv is installed
try:
    from dotenv import load_dotenv
    load_dotenv(override=True)
except ImportError:
    pass

from config import (
    TRAVEL_VIBES,
    BUDGET_LEVELS,
    TRAVEL_PARTIES,
    TRAVEL_PACES,
    TRAVEL_INTERESTS,
    DIETARY_PREFERENCES,
    CURRENCY_SYMBOLS,
    get_secret,
)
from modules.ai_engine import AIEngine, get_available_groq_models
from modules.storage import load_all_trips, save_trip, delete_trip, get_trip
from modules.recommender import recommend_destinations
from modules.planner import generate_itinerary
from modules.modifier import swap_activity_slot, regenerate_single_day
from modules.pdf_generator import generate_itinerary_pdf
from modules.ui_components import (
    render_brand_header,
    render_budget_metric_tiles,
    render_interactive_map,
    render_slot_card
)

# Page Configuration (Wide layout, collapsed sidebar)
st.set_page_config(
    page_title="RoamCraft — Curated Travel Itinerary Planner",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Inject custom CSS
css_path = os.path.join(os.path.dirname(__file__), "styles", "main.css")
if os.path.exists(css_path):
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


# Initialize Session State
if "active_trip" not in st.session_state:
    all_trips = load_all_trips()
    if all_trips:
        first_trip_id = list(all_trips.keys())[0]
        st.session_state.active_trip = all_trips[first_trip_id]
    else:
        st.session_state.active_trip = None

if "recs" not in st.session_state:
    st.session_state.recs = []

if "custom_dest" not in st.session_state:
    st.session_state.custom_dest = "Kyoto, Japan"


# Silent Backend AI Engine Initialization (Compatible with local .env and Streamlit Cloud st.secrets)
groq_key = get_secret("GROQ_API_KEY")
gemini_key = get_secret("GEMINI_API_KEY")

@st.cache_data(show_spinner=False, ttl=3600)
def _cached_groq_models(key: str):
    return get_available_groq_models(key)

if groq_key and groq_key.startswith("gsk_"):
    # Detect accessible models quietly with caching for high performance
    available_models = _cached_groq_models(groq_key)
    chosen_model = available_models[0] if available_models else "openai/gpt-oss-120b"
    engine = AIEngine(provider="groq", api_key=groq_key, model_name=chosen_model)
elif gemini_key:
    engine = AIEngine(provider="gemini", api_key=gemini_key, model_name="gemini-1.5-flash")
else:
    engine = AIEngine(provider="demo")


# -------------------------------------------------------------
# TOP NAVIGATION BRAND HEADER
# -------------------------------------------------------------
render_brand_header()


# -------------------------------------------------------------
# MASTER JOURNEY PLANNER (AIRBNB-STYLE FLOATING COMMAND CARD)
# -------------------------------------------------------------
with st.container():
    st.markdown('<div class="planner-panel">', unsafe_allow_html=True)
    st.markdown('<div class="planner-title">🌍 Plan Your Next Journey</div>', unsafe_allow_html=True)

    row1_c1, row1_c2, row1_c3 = st.columns([2.5, 1.8, 1.2])
    with row1_c1:
        plan_destination = st.text_input(
            "Destination",
            value=st.session_state.custom_dest,
            placeholder="e.g. Rome, Italy or Tokyo, Japan or Swiss Alps",
            help="Enter any city, region, or country."
        )
    with row1_c2:
        plan_vibe = st.selectbox("Travel Vibe", TRAVEL_VIBES, index=2)
    with row1_c3:
        plan_duration = st.slider("Duration (Days)", min_value=1, max_value=7, value=4)

    row2_c1, row2_c2, row2_c3, row2_c4 = st.columns(4)
    with row2_c1:
        today = date.today()
        plan_start_date = st.date_input("Start Date", value=today + timedelta(days=14))
    with row2_c2:
        plan_party = st.selectbox("Travel Party", TRAVEL_PARTIES, index=1)
    with row2_c3:
        plan_budget = st.selectbox("Budget Tier", BUDGET_LEVELS, index=1)
    with row2_c4:
        plan_pace = st.selectbox("Travel Pace", TRAVEL_PACES, index=1)

    # Optional detailed customization drawer
    with st.expander("✨ Refine Interests & Dietary Preferences", expanded=False):
        exp_c1, exp_c2 = st.columns([3, 1])
        with exp_c1:
            plan_interests = st.multiselect(
                "Personalized Interests",
                TRAVEL_INTERESTS,
                default=["Street Food & Local Markets", "Iconic Landmarks & Architecture", "Art Galleries & Historic Museums"]
            )
        with exp_c2:
            plan_dietary = st.selectbox("Dietary Preference", DIETARY_PREFERENCES, index=0)

    # Action Button Row
    btn_col1, btn_col2 = st.columns([4, 1])
    with btn_col2:
        craft_btn = st.button("✨ Craft My Journey", type="primary", use_container_width=True)

    if craft_btn:
        with st.spinner(f"Curating a geographically clustered route for {plan_destination}..."):
            new_plan = generate_itinerary(
                destination=plan_destination,
                duration_days=plan_duration,
                start_date=plan_start_date,
                budget_level=plan_budget,
                travel_party=plan_party,
                pace=plan_pace,
                interests=plan_interests,
                dietary=plan_dietary,
                ai_engine=engine
            )
            st.session_state.active_trip = new_plan
            save_trip(new_plan)
            st.success(f"Journey created for {plan_destination}!")
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)


# -------------------------------------------------------------
# MAIN VIEW TABS
# -------------------------------------------------------------
tab_itinerary, tab_discover, tab_customize, tab_vault = st.tabs([
    "🗺️ Curated Itinerary & Map",
    "✨ Discover & Match Destinations",
    "🪄 Tailor & Swap Activities",
    "🧳 Trip Vault & Offline Guide"
])


# =============================================================
# TAB 1: CURATED ITINERARY & INTERACTIVE MAP
# =============================================================
with tab_itinerary:
    active_itin = st.session_state.active_trip

    if not active_itin:
        st.info("👋 Select or craft a journey above to see your day-by-day itinerary and interactive map.")
    else:
        # Trip Header
        head_c1, head_c2 = st.columns([3, 1])
        with head_c1:
            st.markdown(f"## 📍 {active_itin.get('trip_title', 'Curated Journey')}")
            st.markdown(
                f"<div style='font-size: 0.95rem; color: #64748b; margin-top: -6px; margin-bottom: 12px;'>"
                f"<b>{active_itin.get('destination')}</b> • {active_itin.get('duration_days')} Days "
                f"({active_itin.get('start_date')} to {active_itin.get('end_date')}) • "
                f"{active_itin.get('travel_party')} • {active_itin.get('budget_level', '').split('(')[0]}"
                f"</div>",
                unsafe_allow_html=True
            )
        with head_c2:
            currency_pref = st.radio("Currency Display", ["USD ($)", "INR (₹)"], horizontal=True)

        # Overview Quote
        overview = active_itin.get("overview", "")
        if overview:
            st.markdown(
                f"<div style='background: #f1f5f9; border-left: 4px solid #0f766e; padding: 14px 18px; border-radius: 0 12px 12px 0; margin-bottom: 20px; font-size: 0.95rem; color: #334155; line-height: 1.5;'>"
                f"<b>🧭 Trip Strategy:</b> {overview}"
                f"</div>",
                unsafe_allow_html=True
            )

        # Metrics Row
        render_budget_metric_tiles(active_itin)

        # Interactive Map
        render_interactive_map(active_itin)

        st.markdown("<hr style='margin: 32px 0 24px 0; border: none; border-top: 1px solid #e2e8f0;'/>", unsafe_allow_html=True)
        st.markdown("### 🗓️ Day-by-Day Geographically Clustered Schedule")

        days = active_itin.get("days", [])
        for day in days:
            day_num = day.get("day_number", 1)
            day_theme = day.get("day_theme", f"Day {day_num}")
            cluster = day.get("cluster_neighborhood", "City Center")
            fatigue = day.get("transit_fatigue_score", "Low (Walking distance)")
            day_usd = day.get("day_total_usd", 0.0)
            day_inr = day.get("day_total_inr", 0.0)
            running_usd = day.get("running_total_usd", day_usd)

            with st.expander(f"Day {day_num}: {day_theme} (${day_usd:,.0f} USD)", expanded=(day_num == 1)):
                st.markdown(
                    f"""
                    <div class="cluster-header-bar">
                        <div class="cluster-name">
                            <span>📍</span> <b>Neighborhood Cluster:</b> {cluster}
                        </div>
                        <div class="fatigue-badge">
                            ✨ {fatigue}
                        </div>
                        <div style="font-size: 0.92rem; font-weight: 700; color: #f8fafc;">
                            Day Total: ${day_usd:,.0f} USD (₹{day_inr:,.0f}) • Running: ${running_usd:,.0f}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                slots = day.get("slots", {})
                for slot_key in ["morning", "lunch", "afternoon", "evening"]:
                    if slot_key in slots:
                        render_slot_card(slot_key, slots[slot_key])


# =============================================================
# TAB 2: DISCOVER & MATCH DESTINATIONS
# =============================================================
with tab_discover:
    st.markdown("### ✨ Smart Destination Inspiration")
    st.markdown("Looking for ideas? Filter by travel mood, budget, and season to discover destinations tailored to your style.")

    f_col1, f_col2, f_col3, f_col4 = st.columns([2, 1.5, 1.5, 1.2])
    with f_col1:
        disc_vibe = st.selectbox("Preferred Vibe", TRAVEL_VIBES, index=0, key="disc_vibe")
    with f_col2:
        disc_budget = st.selectbox("Budget Level", BUDGET_LEVELS, index=1, key="disc_budg")
    with f_col3:
        disc_season = st.selectbox("Ideal Season", ["Spring (Mar - May)", "Summer (Jun - Aug)", "Autumn (Sep - Nov)", "Winter (Dec - Feb)"], index=0, key="disc_seas")
    with f_col4:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        disc_btn = st.button("🔍 Recommend", type="primary", use_container_width=True)

    if disc_btn or not st.session_state.recs:
        with st.spinner("Finding matching destinations..."):
            st.session_state.recs = recommend_destinations(
                vibe=disc_vibe,
                budget_level=disc_budget,
                season=disc_season,
                party=plan_party,
                interests=plan_interests,
                ai_engine=engine
            )

    recs = st.session_state.recs[:3]
    cols = st.columns(3)
    for idx, r in enumerate(recs):
        with cols[idx]:
            c_name = r.get("city", "City")
            country = r.get("country", "Country")
            score = r.get("match_score", "95%")
            why = r.get("why_matched", "")
            d_usd = r.get("avg_daily_usd", 120)
            d_inr = r.get("avg_daily_inr", 10380)
            tags = r.get("highlight_tags", [])
            highlights = r.get("signature_experiences", [])

            st.markdown(
                f"""
                <div class="destination-card">
                    <div>
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span class="dest-country-name">{country}</span>
                            <span class="dest-badge-match">★ {score} Match</span>
                        </div>
                        <div class="dest-city-name">{c_name}</div>
                        <div class="dest-why-text">{why}</div>
                        <div style="margin-bottom: 14px;">
                            {' '.join([f'<span class="tag-chip">{t}</span>' for t in tags[:3]])}
                        </div>
                        <div class="dest-spend-box">
                            <div style="font-size: 0.76rem; font-weight: 700; color: #64748b; text-transform: uppercase;">Average Daily Spend</div>
                            <div style="font-family: 'Outfit', sans-serif; font-size: 1.35rem; font-weight: 800; color: #0f172a;">${d_usd} <span style="font-size: 0.85rem; font-weight: 500; color: #64748b;">(₹{d_inr:,.0f} INR)</span></div>
                        </div>
                        <div style="margin-bottom: 18px;">
                            <div style="font-size: 0.82rem; font-weight: 700; color: #0f172a; margin-bottom: 6px;">Iconic Experiences:</div>
                            {''.join([f'<div style="font-size: 0.82rem; color: #475569; margin-bottom: 4px;">• {h}</div>' for h in highlights[:2]])}
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
            if st.button(f"🎯 Plan Trip to {c_name}", key=f"rec_pick_{idx}", use_container_width=True):
                st.session_state.custom_dest = f"{c_name}, {country}"
                st.success(f"Selected {c_name}! Ready to craft your journey.")
                st.rerun()


# =============================================================
# TAB 3: TAILOR & SWAP ACTIVITIES
# =============================================================
with tab_customize:
    st.markdown("### 🪄 Dynamic Activity Customization")
    st.markdown("Swap or customize individual slots **without losing the rest of your itinerary**. The AI automatically keeps replacement activities inside the same neighborhood cluster to avoid backtracking.")

    active_itin = st.session_state.active_trip
    if not active_itin:
        st.info("Craft an itinerary first to unlock dynamic activity swapping.")
    else:
        days = active_itin.get("days", [])
        day_nums = [d.get("day_number", i+1) for i, d in enumerate(days)]

        swap_c1, swap_c2 = st.columns([1.5, 2.5])
        with swap_c1:
            sel_day = st.selectbox("Select Day to Modify", day_nums, index=0)
            sel_slot = st.selectbox(
                "Select Time Slot",
                ["morning", "lunch", "afternoon", "evening"],
                format_func=lambda x: {
                    "morning": "🌅 Morning Sightseeing",
                    "lunch": "🍽️ Lunch Recommendation",
                    "afternoon": "🏛️ Afternoon Leisure",
                    "evening": "🌆 Evening Dining & Nightlife"
                }[x]
            )

        current_day = next((d for d in days if d.get("day_number") == sel_day), days[0])
        current_slot = current_day.get("slots", {}).get(sel_slot, {})

        with swap_c2:
            st.markdown(
                f"""
                <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 14px; padding: 18px; margin-top: 4px;">
                    <div style="font-size: 0.8rem; font-weight: 700; color: #64748b; text-transform: uppercase;">Current Activity</div>
                    <div style="font-family: 'Outfit', sans-serif; font-size: 1.2rem; font-weight: 700; color: #0f172a; margin: 4px 0;">{current_slot.get('title', 'N/A')}</div>
                    <div style="font-size: 0.88rem; color: #475569; line-height: 1.4;">{current_slot.get('description', '')}</div>
                    <div style="margin-top: 8px; font-size: 0.82rem; font-weight: 600; color: #0f766e;">📍 {current_day.get('cluster_neighborhood')} • Est. ${current_slot.get('cost_usd', 0):,.0f} USD</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        st.markdown("<hr style='margin: 20px 0;'/>", unsafe_allow_html=True)
        st.markdown("#### Choose a Quick Transformation or Type Custom Wish:")

        p_col1, p_col2, p_col3 = st.columns(3)
        with p_col1:
            btn_market = st.button("🛍️ Artisan / Outdoor Market", use_container_width=True)
            btn_rain = st.button("☔ Indoor Cultural Alternative", use_container_width=True)
        with p_col2:
            btn_veg = st.button("🥗 Plant-Based / Organic Dining", use_container_width=True)
            btn_kid = st.button("👨‍👩‍👧 Family & Kid-Friendly Activity", use_container_width=True)
        with p_col3:
            btn_adv = st.button("🏃 Scenic Hike & Viewpoint", use_container_width=True)
            btn_cafe = st.button("☕ Scenic Coffee & Stroll", use_container_width=True)

        user_custom_wish = st.text_input("Or enter a custom modification:", placeholder="e.g. Find a romantic hidden rooftop or photography viewpoint")

        action_prompt = None
        if btn_market:
            action_prompt = "Swap for an authentic outdoor artisan and farmers market"
        elif btn_veg:
            action_prompt = "Find a delicious organic vegetarian and vegan dining spot"
        elif btn_adv:
            action_prompt = "Swap for an energetic outdoor adventure or scenic viewpoint hike"
        elif btn_rain:
            action_prompt = "Replace with an inspiring indoor covered museum or heritage pavilion"
        elif btn_kid:
            action_prompt = "Swap for a fun, interactive family and kid-friendly attraction"
        elif btn_cafe:
            action_prompt = "Swap for a relaxed scenic coffee spot and leisurely promenade"
        elif user_custom_wish:
            if st.button("✨ Apply Custom Wish", type="primary"):
                action_prompt = user_custom_wish

        if action_prompt:
            with st.spinner(f"Customizing {sel_slot} on Day {sel_day} within {current_day.get('cluster_neighborhood')}..."):
                up_itin, success, msg = swap_activity_slot(
                    itinerary=active_itin,
                    day_number=sel_day,
                    slot_key=sel_slot,
                    modification_prompt=action_prompt,
                    ai_engine=engine
                )
                if success:
                    st.session_state.active_trip = up_itin
                    save_trip(up_itin)
                    st.success(f"Customized Day {sel_day}: {msg}")
                    st.rerun()


# =============================================================
# TAB 4: TRIP VAULT & OFFLINE PDF GUIDE
# =============================================================
with tab_vault:
    st.markdown("### 🧳 Trip Vault & Offline Travel Guide")

    active_itin = st.session_state.active_trip

    if active_itin:
        st.markdown(
            f"""
            <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 18px; padding: 24px; margin-bottom: 24px; box-shadow: 0 4px 12px rgba(0,0,0,0.03);">
                <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 14px;">
                    <div>
                        <div style="font-family: 'Outfit', sans-serif; font-size: 1.4rem; font-weight: 700; color: #0f172a;">{active_itin.get('trip_title')}</div>
                        <div style="font-size: 0.88rem; color: #64748b; margin-top: 4px;">Print-ready offline travel guide with day schedules, neighborhood maps, and emergency checklists.</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        pdf_col1, pdf_col2 = st.columns([3, 1.2])
        with pdf_col2:
            try:
                pdf_bytes = generate_itinerary_pdf(active_itin)
                dest_clean = active_itin.get("destination", "trip").replace(" ", "_").replace(",", "")
                st.download_button(
                    label="📥 Download Offline PDF",
                    data=pdf_bytes,
                    file_name=f"{dest_clean}_Travel_Guide.pdf",
                    mime="application/pdf",
                    type="primary",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"Error compiling PDF: {e}")

        # Rename / save trip
        with st.expander("💾 Save or Rename Trip in Vault", expanded=False):
            save_c1, save_c2 = st.columns([3, 1])
            with save_c1:
                new_title = st.text_input("Trip Label", value=active_itin.get("trip_title", "My Journey"))
            with save_c2:
                st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
                if st.button("Save", use_container_width=True):
                    active_itin["trip_title"] = new_title
                    save_trip(active_itin)
                    st.success("Trip updated!")
                    st.rerun()

    st.markdown("<hr style='margin: 28px 0 20px 0; border: none; border-top: 1px solid #e2e8f0;'/>", unsafe_allow_html=True)
    st.markdown("#### 📁 Saved Journeys")

    saved_trips = load_all_trips()
    if not saved_trips:
        st.info("Your vault is currently empty.")
    else:
        for t_id, t_data in list(saved_trips.items()):
            st.markdown(
                f"""
                <div class="vault-card">
                    <div>
                        <div style="font-family: 'Outfit', sans-serif; font-size: 1.2rem; font-weight: 700; color: #0f172a;">{t_data.get('title', 'Journey')}</div>
                        <div style="font-size: 0.85rem; color: #64748b; margin-top: 2px;">
                            📍 <b>{t_data.get('destination')}</b> • {t_data.get('duration_days')} Days • {t_data.get('travel_party')} • {t_data.get('budget_level', '').split('(')[0]}
                        </div>
                    </div>
                    <div style="text-align: right;">
                        <div style="font-family: 'Outfit', sans-serif; font-size: 1.35rem; font-weight: 800; color: #e05a47;">${t_data.get('total_estimated_usd', 0):,.0f} USD</div>
                        <div style="font-size: 0.8rem; color: #64748b;">₹{t_data.get('total_estimated_inr', 0):,.0f} INR</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
            v_c1, v_c2 = st.columns([1, 1])
            with v_c1:
                if st.button("📂 Load This Trip", key=f"load_vault_{t_id}", use_container_width=True):
                    st.session_state.active_trip = t_data
                    st.session_state.custom_dest = t_data.get("destination", "Tokyo, Japan")
                    st.success(f"Loaded {t_data.get('title')}!")
                    st.rerun()
            with v_c2:
                if st.button("🗑️ Delete", key=f"del_vault_{t_id}", use_container_width=True):
                    delete_trip(t_id)
                    st.warning("Trip removed from vault.")
                    st.rerun()
