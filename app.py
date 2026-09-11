import streamlit as st
import pandas as pd
import plotly.express as px
import json
import os

# Page configuration
st.set_page_config(
    page_title="SAFAR - Tourist Profile & Budget Planner",
    page_icon="🇵🇰",
    layout="wide"
)

# Custom header styling
st.title("🇵🇰 SAFAR: AI Travel Companion for Pakistan")
st.subheader("Member 2: Tourist Profile & Dynamic Budget Planner")
st.markdown("Enter trip parameters below to generate an AI-assisted budget allocation and pass structured data to the Hotel and Itinerary modules.")

st.divider()

# ----------------------------------------------------
# 1. USER INPUT SECTION (Tourist Profile & Parameters)
# ----------------------------------------------------
st.header("1. Tourist Requirements & Trip Parameters")

col1, col2, col3 = st.columns(3)

with col1:
    travelers = st.number_input(
        "Number of Travelers",
        min_value=1,
        max_value=50,
        value=2,
        step=1,
        help="Total adults and children traveling together."
    )
    trip_duration = st.number_input(
        "Trip Duration (Days)",
        min_value=1,
        max_value=60,
        value=7,
        step=1,
        help="Total number of days for the itinerary."
    )

with col2:
    currency = st.selectbox(
        "Input Currency",
        options=["PKR", "USD"],
        index=0,
        help="Currency for entering total budget."
    )
    
    default_budget = 350000 if currency == "PKR" else 1300
    min_budget = 10000 if currency == "PKR" else 50
    
    total_budget_input = st.number_input(
        f"Total Trip Budget ({currency})",
        min_value=min_budget,
        value=default_budget,
        step=5000 if currency == "PKR" else 50
    )

with col3:
    travel_style = st.selectbox(
        "Travel Preference / Style",
        options=["Budget / Backpacker", "Standard / Balanced", "Luxury / Premium"],
        index=1,
        help="Determines percentage allocation across expenses."
    )
    destinations = st.multiselect(
        "Planned Destinations",
        options=[
            "Islamabad", "Rawalpindi", "Lahore", "Hunza Valley", 
            "Skardu", "Swat", "Peshawar", "Karachi", "Gwadar", "Naran & Kaghan"
        ],
        default=["Islamabad", "Hunza Valley"],
        help="Select one or more cities/regions to visit."
    )

# ----------------------------------------------------
# 2. BUDGET ALLOCATION LOGIC (Rule & Preference Engine)
# ----------------------------------------------------
# Base conversion rate
USD_TO_PKR_RATE = 280.0
total_budget_pkr = float(total_budget_input if currency == "PKR" else total_budget_input * USD_TO_PKR_RATE)

# Style-driven allocation ratios
allocation_ratios = {
    "Budget / Backpacker": {
        "hotels": 0.30,
        "transport": 0.30,
        "food": 0.25,
        "activities": 0.15
    },
    "Standard / Balanced": {
        "hotels": 0.35,
        "transport": 0.25,
        "food": 0.20,
        "activities": 0.20
    },
    "Luxury / Premium": {
        "hotels": 0.45,
        "transport": 0.25,
        "food": 0.15,
        "activities": 0.15
    }
}

active_ratios = allocation_ratios[travel_style]

alloc_hotels = total_budget_pkr * active_ratios["hotels"]
alloc_transport = total_budget_pkr * active_ratios["transport"]
alloc_food = total_budget_pkr * active_ratios["food"]
alloc_activities = total_budget_pkr * active_ratios["activities"]

# Feasibility heuristic (Minimum ~5,000 PKR per person per day)
min_recommended_budget_pkr = travelers * trip_duration * 5000.0
is_budget_feasible = total_budget_pkr >= min_recommended_budget_pkr

st.divider()

# ----------------------------------------------------
# 3. VISUALIZATION & BREAKDOWN SECTION
# ----------------------------------------------------
st.header("2. Budget Allocation & Feasibility Analysis")

if is_budget_feasible:
    st.success(f"Trip Budget is feasible: Total allocated budget ({total_budget_pkr:,.0f} PKR) meets the baseline estimation standard.")
else:
    st.warning(
        f"Budget Alert: Estimated baseline required is ~{min_recommended_budget_pkr:,.0f} PKR "
        f"({travelers} travelers x {trip_duration} days x 5,000 PKR/day). Current budget is tight."
    )

# Summary Metric Cards
m_col1, m_col2, m_col3, m_col4 = st.columns(4)
m_col1.metric("Hotels & Stay", f"PKR {alloc_hotels:,.0f}", f"{active_ratios['hotels']*100:.0f}%")
m_col2.metric("Transport & Transit", f"PKR {alloc_transport:,.0f}", f"{active_ratios['transport']*100:.0f}%")
m_col3.metric("Food & Dining", f"PKR {alloc_food:,.0f}", f"{active_ratios['food']*100:.0f}%")
m_col4.metric("Activities & Buffer", f"PKR {alloc_activities:,.0f}", f"{active_ratios['activities']*100:.0f}%")

st.write("")

viz_col1, viz_col2 = st.columns([1, 1])

with viz_col1:
    breakdown_data = pd.DataFrame({
        "Expense Category": ["Hotels & Accommodation", "Transportation", "Food & Dining", "Activities & Sightseeing"],
        "Allocation (%)": [f"{v * 100:.0f}%" for v in active_ratios.values()],
        "Amount (PKR)": [alloc_hotels, alloc_transport, alloc_food, alloc_activities],
        "Amount (USD)": [alloc_hotels / USD_TO_PKR_RATE, alloc_transport / USD_TO_PKR_RATE, alloc_food / USD_TO_PKR_RATE, alloc_activities / USD_TO_PKR_RATE]
    })
    st.dataframe(
        breakdown_data.style.format({
            "Amount (PKR)": "{:,.0f}",
            "Amount (USD)": "${:,.2f}"
        }),
        use_container_width=True,
        hide_index=True
    )

with viz_col2:
    fig = px.pie(
        breakdown_data,
        names="Expense Category",
        values="Amount (PKR)",
        hole=0.45,
        title="Expenditure Distribution",
        color_discrete_sequence=["#1b4332", "#2d6a4f", "#52b788", "#74c69d"]
    )
    fig.update_layout(margin=dict(t=40, b=20, l=20, r=20))
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# ----------------------------------------------------
# 4. EXPORT / PIPELINE HANDOFF (To Members 3 & 4)
# ----------------------------------------------------
st.header("3. Integration Handoff Payload")
st.caption("Generate unified JSON payload for Member 3 (Hotels) and Member 4 (Itinerary).")

payload = {
    "user_profile": {
        "travelers": int(travelers),
        "duration_days": int(trip_duration),
        "travel_style": travel_style,
        "input_currency": currency
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
    "is_feasible": bool(is_budget_feasible)
}

btn_col1, btn_col2 = st.columns([1, 3])

with btn_col1:
    if st.button("💾 Export Payload (budget_data.json)", use_container_width=True):
        with open("budget_data.json", "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=4)
        st.toast("budget_data.json successfully updated!", icon="✅")

st.json(payload)
