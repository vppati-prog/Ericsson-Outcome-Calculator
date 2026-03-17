import streamlit as st
import pandas as pd
import numpy as np
import os
import random

st.set_page_config(page_title="Ericsson Outcome Calculator", layout="wide")

st.markdown("""
# Ericsson Outcome Intelligence Dashboard
### Observability-driven Outcome KPI Calculator
""")
st.markdown("---")

# -------------------------
# 1. KPI DEFINITIONS + TARGETS (Y1 simplified)
# -------------------------

# Application Development (AD)
ad_kpis = {
    "AD - Story Generation Accuracy (%)": 70,
    "AD - Backlog Preparation Speed Improvement (%)": 20,
    "AD - Cycle Time Reduction (%)": 20,
    "AD - AI-assisted Code Contribution (%)": 25,
    "AD - Automated Test Generation Coverage (%)": 40,
    "AD - Defect Reduction (%)": 30,
}

# Application Operations (AO)
ao_kpis = {
    "AO - Service Ticket Automation Rate (%)": 30,
    "AO - Service Request Deflection to Agentic Solutions (%)": 30,
    "AO - Ticket Reduction (%)": 30,
    "AO - MTTR Improvement (%)": 20,
    "AO - Incident Reduction (%)": 30,
    "AO - FCR Improvement (%)": 30,
}

# Transformation (TR)
tr_kpis = {
    "TR - GenAI Utilization Rate (%)": 50,
    "TR - Landscape Rationalization (%)": 20,
    "TR - Technical Debt Reduction (%)": 20,
    "TR - Employee Satisfaction (%)": 80,
    "TR - Autonomous Task Completion Rate (%)": 30,
    "TR - TCO Optimization (%)": 15,
}

# AI Governance (AI)
ai_kpis = {
    "AI - Bias Monitoring Pass Rate (%)": 95,
    "AI - Guardrail Efficacy (%)": 95,
    "AI - Sensitive Data Protection (%)": 100,
    "AI - Availability and Resiliency (%)": 99.9,
    "AI - Model Change Control Success (%)": 95,
    "AI - Human-in-the-loop Coverage (%)": 100,
}

all_kpis = list(ao_kpis.keys()) + list(ad_kpis.keys()) + list(tr_kpis.keys()) + list(ai_kpis.keys())
all_targets = {**ao_kpis, **ad_kpis, **tr_kpis, **ai_kpis}

# -------------------------
# 2. SIDEBAR – GLOBAL SETTINGS
# -------------------------
st.sidebar.title("Outcome Control Panel")

st.sidebar.markdown("### Outcome Tower Weights (sum ≈ 100%)")
w_ao = st.sidebar.slider("Application Operations %", 0, 50, 30, 1)
w_ad = st.sidebar.slider("Application Development %", 0, 50, 25, 1)
w_tr = st.sidebar.slider("Transformation %", 0, 50, 25, 1)
w_ai = st.sidebar.slider("AI Governance %", 0, 50, 20, 1)

weight_sum = w_ao + w_ad + w_tr + w_ai
if weight_sum == 0:
    weight_sum = 1

tower_weights = {
    "Application Operations": w_ao / weight_sum,
    "Application Development": w_ad / weight_sum,
    "Transformation": w_tr / weight_sum,
    "AI Governance": w_ai / weight_sum,
}

st.sidebar.markdown("---")
outcome_threshold = st.sidebar.slider("Minimum Outcome Score", 1.0, 5.0, 3.5, 0.1)
simulation_intensity = st.sidebar.slider("Simulation Intensity", 5, 30, 15, 1)
scoring_strictness = st.sidebar.slider("Scoring Strictness", 0.7, 1.3, 1.0, 0.05)

st.sidebar.markdown(
    "Business Units with Outcome Score ≥ threshold will be flagged as **Strong**."
)

# -------------------------
# 3. BASELINE DATA
# -------------------------
@st.cache_data
def load_observed_scores():
    if os.path.exists("outcome_observations.csv"):
        return pd.read_csv("outcome_observations.csv")

    return pd.DataFrame([
        [
            "ERP Managed Services",
            35, 32, 28, 22, 30, 31,   # AO
            72, 24, 22, 28, 42, 34,   # AD
            55, 25, 21, 82, 35, 18,   # TR
            96, 96, 100, 99.9, 96, 100  # AI
        ],
        [
            "Digital Commerce",
            42, 36, 33, 24, 38, 35,
            78, 29, 30, 34, 48, 40,
            62, 28, 24, 84, 42, 22,
            97, 97, 100, 99.9, 97, 100
        ],
        [
            "Supply Chain Platforms",
            31, 28, 29, 18, 27, 30,
            68, 18, 19, 23, 35, 28,
            50, 22, 18, 80, 31, 16,
            95, 95, 100, 99.8, 95, 100
        ],
        [
            "Customer Experience Apps",
            39, 35, 31, 21, 34, 33,
            82, 31, 29, 37, 52, 43,
            66, 30, 26, 85, 46, 24,
            96, 96, 100, 99.9, 96, 100
        ],
        [
            "Network Services",
            44, 38, 36, 26, 41, 39,
            70, 20, 18, 25, 38, 30,
            58, 24, 20, 81, 33, 19,
            98, 97, 100, 99.9, 97, 100
        ],
        [
            "Enterprise Platforms",
            41, 37, 35, 23, 39, 36,
            76, 27, 26, 33, 45, 39,
            63, 29, 25, 83, 40, 21,
            97, 96, 100, 99.9, 96, 100
        ],
    ], columns=["Business Unit"] + all_kpis)

# -------------------------
# 4. OBSERVABILITY AGENT
# -------------------------
def run_observability_agent(run_id=0):
    rng = random.Random(1000 + run_id)
    out = load_observed_scores().copy()

    for col in all_kpis:
        def simulate(x):
            change = rng.uniform(-simulation_intensity, simulation_intensity)
            new_val = x + change

            # KPI-specific bounds
            if "Availability and Resiliency" in col:
                new_val = max(95, min(100, new_val))
            elif "Sensitive Data Protection" in col or "Human-in-the-loop Coverage" in col:
                new_val = max(85, min(100, new_val))
            else:
                new_val = max(0, min(100, new_val))

            return round(new_val, 1)

        out[col] = out[col].apply(simulate)

    out.to_csv("outcome_observations.csv", index=False)

def get_status(value, target, strictness=1.0):
    adjusted_target = target * strictness

    if value >= adjusted_target:
        return "🟢"
    elif value >= adjusted_target * 0.75:
        return "🟡"
    else:
        return "🔴"

def kpi_to_score(value, target, strictness=1.0):
    adjusted_target = target * strictness

    ratio = value / adjusted_target if adjusted_target != 0 else 0

    if ratio >= 1.0:
        return 5.0
    elif ratio >= 0.9:
        return 4.0
    elif ratio >= 0.75:
        return 3.0
    elif ratio >= 0.5:
        return 2.0
    else:
        return 1.0

if "agent_run_id" not in st.session_state:
    st.session_state.agent_run_id = 0

st.markdown("## Observability Agent")

if st.button("Simulate real-time observability update"):
    st.session_state.agent_run_id += 1
    run_observability_agent(st.session_state.agent_run_id)
    load_observed_scores.clear()

    events = [
        "Incident trends improved operational resilience in selected business units.",
        "Release telemetry indicates stronger development throughput.",
        "Transformation outcomes improved through automation acceleration.",
        "AI governance controls detected variance in compliance posture.",
        "Cross-unit service stability improved after change-risk reduction.",
    ]

    rng = random.Random(5000 + st.session_state.agent_run_id)
    st.info(f"Observability Insight: {rng.choice(events)}")
    st.rerun()

df = load_observed_scores()
df.index = df.index + 1

# -------------------------
# 5. EDITABLE KPI TABLE
# -------------------------
st.markdown("## Outcome KPI Metrics by Business Unit")
st.markdown(
    "Each KPI is outcome-centric and measurable. The observability agent simulates live KPI movements, "
    "and the dashboard compares actuals against targets using Green / Amber / Red logic."
)

column_config = {}
for col in all_kpis:
    column_config[col] = st.column_config.NumberColumn(min_value=0.0, max_value=100.0, step=1.0)

edited_df = st.data_editor(
    df,
    use_container_width=True,
    num_rows="fixed",
    column_config=column_config,
)

# -------------------------
# 6. KPI STATUS VIEW
# -------------------------
st.markdown("## KPI Target Status View")

status_df = edited_df.copy()

for col, target in all_targets.items():
    status_df[col] = status_df[col].apply(
        lambda v: f"{v:.1f}% {get_status(v, target, scoring_strictness)}"
    )

st.dataframe(status_df, use_container_width=True, hide_index=True)

# -------------------------
# 7. TOWER SCORE CALCULATION
# -------------------------
for col, target in ao_kpis.items():
    edited_df[f"{col} Score"] = edited_df[col].apply(lambda v: kpi_to_score(v, target, scoring_strictness))

for col, target in ad_kpis.items():
    edited_df[f"{col} Score"] = edited_df[col].apply(lambda v: kpi_to_score(v, target, scoring_strictness))

for col, target in tr_kpis.items():
    edited_df[f"{col} Score"] = edited_df[col].apply(lambda v: kpi_to_score(v, target, scoring_strictness))

for col, target in ai_kpis.items():
    edited_df[f"{col} Score"] = edited_df[col].apply(lambda v: kpi_to_score(v, target, scoring_strictness))

edited_df["Application Operations"] = edited_df[[f"{c} Score" for c in ao_kpis.keys()]].mean(axis=1)
edited_df["Application Development"] = edited_df[[f"{c} Score" for c in ad_kpis.keys()]].mean(axis=1)
edited_df["Transformation"] = edited_df[[f"{c} Score" for c in tr_kpis.keys()]].mean(axis=1)
edited_df["AI Governance"] = edited_df[[f"{c} Score" for c in ai_kpis.keys()]].mean(axis=1)

edited_df["Outcome Score"] = (
    edited_df["Application Operations"] * tower_weights["Application Operations"] +
    edited_df["Application Development"] * tower_weights["Application Development"] +
    edited_df["Transformation"] * tower_weights["Transformation"] +
    edited_df["AI Governance"] * tower_weights["AI Governance"]
)

edited_df["Outcome Status"] = np.where(
    edited_df["Outcome Score"] >= outcome_threshold,
    "🟢 Strong",
    "🔴 At Risk"
)

sorted_df = edited_df.sort_values("Outcome Score", ascending=False).reset_index(drop=True)
sorted_df.index = sorted_df.index + 1

# -------------------------
# 8. EXECUTIVE SNAPSHOT
# -------------------------
st.markdown("## Executive Outcome Snapshot")

strong_units = (sorted_df["Outcome Status"] == "🟢 Strong").sum()
at_risk_units = (sorted_df["Outcome Status"] == "🔴 At Risk").sum()
avg_outcome = sorted_df["Outcome Score"].mean()
top_outcome = sorted_df["Outcome Score"].max()

k1, k2, k3, k4 = st.columns(4)
with k1:
    st.metric("Average Outcome Score", f"{avg_outcome:.2f}")
with k2:
    st.metric("Top Outcome Score", f"{top_outcome:.2f}")
with k3:
    st.metric("Strong Units", f"{strong_units}")
with k4:
    st.metric("At Risk Units", f"{at_risk_units}")

# -------------------------
# 9. TOWER PERFORMANCE OVERVIEW
# -------------------------
st.markdown("## Tower Performance Overview")

tower_avg = pd.DataFrame({
    "Tower": [
        "Application Operations",
        "Application Development",
        "Transformation",
        "AI Governance",
    ],
    "Average Score": [
        sorted_df["Application Operations"].mean(),
        sorted_df["Application Development"].mean(),
        sorted_df["Transformation"].mean(),
        sorted_df["AI Governance"].mean(),
    ]
})

st.bar_chart(tower_avg.set_index("Tower"))

# -------------------------
# 10. RANKED OUTPUT
# -------------------------
st.markdown("## Ranked Business Units by Outcome Score")

st.dataframe(
    sorted_df[
        [
            "Business Unit",
            "Application Operations",
            "Application Development",
            "Transformation",
            "AI Governance",
            "Outcome Score",
            "Outcome Status",
        ]
    ],
    use_container_width=True,
    hide_index=True,
)

st.markdown("---")
st.markdown("""
### How to use this dashboard

1. The observability agent simulates live KPI changes across 24 measurable outcome KPIs.
2. Each business unit is assessed across four outcome towers: Application Operations, Application Development, Transformation, and AI Governance.
3. KPI values are compared against targets and translated into Green / Amber / Red status, then rolled up into tower scores.
4. Tower scores are combined into an overall weighted Outcome Score.
5. Leadership can identify strong vs at-risk business units in real time.
""")
