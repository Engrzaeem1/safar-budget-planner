import streamlit as st
import pandas as pd
import plotly.express as px
import json

# Page Setup & Configuration
st.set_page_config(
    page_title="SAFAR - AI Travel Companion for Pakistan",
    page_icon="🇵🇰",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for a clean modern UI
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1b4332;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #555;
        margin-bottom: 1.5rem;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.5rem !important;
        font-weight: 700 !important;
        color: #2d6a4f !important;
    }
    .card-box {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 1.2rem;
        border: 1px solid #e9ecef;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">🇵🇰 SAFAR: Pakistan Travel Budget Planner</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Plan your journey, optimize costs, and generate trip specifications for Pakistan.</div>', unsafe_allow_html=True)

# ----------------------------------------------------
# 1. TOURIST REQUIREMENTS & TRIP INPUTS
# ----------------------------------------------------
with st.container():
    st.subheader("1. Trip Parameters")
    
    col1, col2, col3 = st.columns(3)

    with col1:
        travelers = st.number_input(
            "Number of Travelers",
            min_value=1,
            max_value=50,
            value=2,
            step=1
        )
        trip_duration = st.number_input(
            "Trip Duration (Days)",
            min_value=1,
            max_value=60,
            value=7,
            step=1
        )

    with col2:
        currency = st.selectbox(
            "Input Currency",
            options=["PKR", "USD"],
            index=0
        )
        default_budget = 300000 if currency == "PKR" else 1100
        min_budget = 5000 if currency == "PKR" else 20
        
        total_budget_input = st.number_input(
            f"Total Budget ({currency})",
            min_value=min_budget,
            value=default_budget,
            step=5000 if currency == "PKR" else 50
        )

    with col3:
        travel_style = st.selectbox(
            "Travel Preference",
            options=["Budget / Backpacker", "Standard", "Luxury"],
            index=1
        )
        destinations = st.multiselect(
            "Planned Destinations",
            options=[
                "Islamabad", "Lahore", "Hunza Valley", "Skardu", 
                "Swat", "Murree", "Gilgit", "Peshawar", "Karachi"
            ],
            default=["Islamabad", "Hunza Valley"]
        )

st.divider()

# ----------------------------------------------------
# 2. BUDGET ENGINE & CALCULATIONS
# ----------------------------------------------------
USD_TO_PKR_RATE = 280.0
total_budget_pkr = float(total_budget_input if currency == "PKR" else total_budget_input * USD_TO_PKR_RATE)

allocation_ratios = {
    "Budget / Backpacker": {"hotels": 0.30, "transport": 0.30, "food": 0.25, "activities": 0.15},
    "Standard": {"hotels": 0.35, "transport": 0.25, "food": 0.20, "activities": 0.20},
    "Luxury": {"hotels": 0.45, "transport": 0.25, "food": 0.15, "activities": 0.15}
}

active_ratios = allocation_ratios[travel_style]
alloc_hotels = total_budget_pkr * active_ratios["hotels"]
alloc_transport = total_budget_pkr * active_ratios["transport"]
alloc_food = total_budget_pkr * active_ratios["food"]
alloc_activities = total_budget_pkr * active_ratios["activities"]

# Feasibility benchmark: ~5,000 PKR per person per day
min_required_budget = travelers * trip_duration * 5000.0
is_feasible = total_budget_pkr >= min_required_budget

# ----------------------------------------------------
# 3. EXPENSE ALLOCATION & VISUALIZATION
# ----------------------------------------------------
st.subheader("2. Expense Breakdown & Allocation")

if is_feasible:
    st.success(f"Budget is balanced: Total allocated budget ({total_budget_pkr:,.0f} PKR) is sufficient for {travelers} travelers across {trip_duration} days.")
else:
    st.warning(f"Budget Notice: Estimated standard baseline is ~{min_required_budget:,.0f} PKR ({travelers} travelers × {trip_duration} days). Costs may require adjustments.")

# Metric Cards
m1, m2, m3, m4 = st.columns(4)
m1.metric("Hotels & Stay", f"PKR {alloc_hotels:,.0f}", f"{active_ratios['hotels']*100:.0f}%")
m2.metric("Transportation", f"PKR {alloc_transport:,.0f}", f"{active_ratios['transport']*100:.0f}%")
m3.metric("Food & Dining", f"PKR {alloc_food:,.0f}", f"{active_ratios['food']*100:.0f}%")
m4.metric("Activities & Sightseeing", f"PKR {alloc_activities:,.0f}", f"{active_ratios['activities']*100:.0f}%")

st.write("")

viz_col1, viz_col2 = st.columns([1.1, 0.9])

with viz_col1:
    breakdown_df = pd.DataFrame({
        "Category": ["Hotels & Accommodation", "Transportation", "Food & Dining", "Activities & Sightseeing"],
        "Allocation": [f"{v * 100:.0f}%" for v in active_ratios.values()],
        "Cost (PKR)": [alloc_hotels, alloc_transport, alloc_food, alloc_activities],
        "Cost (USD)": [alloc_hotels / USD_TO_PKR_RATE, alloc_transport / USD_TO_PKR_RATE, alloc_food / USD_TO_PKR_RATE, alloc_activities / USD_TO_PKR_RATE]
    })
    st.dataframe(
        breakdown_df.style.format({
            "Cost (PKR)": "{:,.0f}",
            "Cost (USD)": "${:,.2f}"
        }),
        use_container_width=True,
        hide_index=True
    )

with viz_col2:
    fig = px.pie(
        breakdown_df,
        names="Category",
        values="Cost (PKR)",
        hole=0.45,
        color_discrete_sequence=["#1b4332", "#2d6a4f", "#52b788", "#74c69d"]
    )
    fig.update_layout(margin=dict(t=20, b=20, l=20, r=20), showlegend=True)
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# ----------------------------------------------------
# 4. STRUCTURED DATA EXPORT
# ----------------------------------------------------
st.subheader("3. Trip Payload")

payload = {
    "user_profile": {
        "travelers": int(travelers),
        "duration_days": int(trip_duration),
        "travel_style": travel_style
    },
    "destinations": destinations,
    "budget_pkr": {
        "total": float(total_budget_pkr),
        "hotels": float(alloc_hotels),
        "transport": float(alloc_transport),
        "food": float(alloc_food),
        "activities": float(alloc_activities)
    },
    "budget_usd": {
        "total": float(total_budget_pkr / USD_TO_PKR_RATE),
        "hotels": float(alloc_hotels / USD_TO_PKR_RATE),
        "transport": float(alloc_transport / USD_TO_PKR_RATE),
        "food": float(alloc_food / USD_TO_PKR_RATE),
        "activities": float(alloc_activities / USD_TO_PKR_RATE)
    },
    "is_feasible": bool(is_feasible)
}

payload_json = json.dumps(payload, indent=4)

st.download_button(
    label="📥 Download Trip Payload (budget_data.json)",
    data=payload_json,
    file_name="budget_data.json",
    mime="application/json"
)

with st.expander("View Payload Preview"):
    st.json(payload)
