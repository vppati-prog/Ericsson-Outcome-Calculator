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
# 1. KPI DEFINITIONS + TARGETS (Y1 simplified, 4 per tower)
# -------------------------

# Application Operations
ao_kpis = {
    "AO - Ticket Automation Rate (%)": 30,
    "AO - Agentic Deflection (%)": 30,
    "AO - MTTR Improvement (%)": 20,
    "AO - Incident Reduction (%)": 30,
}

# Application Development
ad_kpis = {
    "AD - Story Generation Accuracy (%)": 70,
    "AD - Backlog Preparation Speed Improvement (%)": 20,
    "AD - Cycle Time Reduction (%)": 20,
    "AD - Automated Test Generation Coverage (%)": 40,
}

# Transformation
tr_kpis = {
    "TR - GenAI Utilization Rate (%)": 50,
    "TR - Landscape Rationalization (%)": 20,
    "TR - Technical Debt Reduction (%)": 20,
    "TR - TCO Optimization (%)": 15,
}

# AI Governance
ai_kpis = {
    "AI - Bias Monitoring Pass Rate (%)": 95,
    "AI - Guardrail Efficacy (%)": 95,
    "AI - Availability and Resiliency (%)": 99.9,
    "AI - Human-in-the-loop Coverage (%)": 100,
}

tower_kpis = {
    "Application Operations": ao_kpis,
    "Application Development": ad_kpis,
    "Transformation": tr_kpis,
    "AI Governance": ai_kpis,
}

all_targets = {**ao_kpis, **ad_kpis, **tr_kpis, **ai_kpis}
all_kpis = list(all_targets.keys())

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
            35, 32, 18, 28,   # AO
            72, 24, 22, 42,   # AD
            55, 25, 21, 18,   # TR
            96, 96, 99.8, 100 # AI
        ],
        [
            "Digital Commerce",
            42, 36, 24, 38,
            78, 29, 30, 48,
            62, 28, 24, 22,
            97, 97, 99.9, 100
        ],
        [
            "Supply Chain Platforms",
            24, 26, 11, 25,
            68, 18, 19, 35,
            50, 22, 18, 16,
            95, 95, 99.7, 100
        ],
        [
            "Customer Experience Apps",
            28, 21, 20, 27,
            82, 31, 29, 52,
            66, 30, 26, 24,
            96, 96, 99.8, 100
        ],
        [
            "Network Services",
            44, 30, 22, 40,
            70, 20, 18, 38,
            58, 24, 20, 19,
            98, 97, 99.9, 100
        ],
        [
            "Enterprise Platforms",
            41, 39, 19, 34,
            76, 27, 26, 45,
            63, 29, 25, 21,
            97, 96, 99.9, 100
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

            if "Availability and Resiliency" in col:
                new_val = max(95, min(100, new_val))
            elif "Human-in-the-loop Coverage" in col:
                new_val = max(85, min(100, new_val))
            else:
                new_val = max(0, min(100, new_val))

            return round(new_val, 1)

        out[col] = out[col].apply(simulate)

    out.to_csv("outcome_observations.csv", index=False)

def get_status(value, target, strictness=1.0):
    adjusted_target = target * strictness

    if value >= adjusted_target:
        return "🟢 Green"
    elif value >= adjusted_target * 0.75:
        return "🟡 Amber"
    else:
        return "🔴 Red"

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
        "Operational telemetry indicates improvement in service automation and resilience.",
        "Application development signals show stronger cycle time and test coverage outcomes.",
        "Transformation telemetry reflects accelerated GenAI utilization and debt reduction.",
        "AI governance monitoring highlights changes in compliance and resiliency posture.",
        "Business-unit outcome profile has shifted based on latest observability signals.",
    ]

    rng = random.Random(5000 + st.session_state.agent_run_id)
    st.info(f"Observability Insight: {rng.choice(events)}")
    st.rerun()

df = load_observed_scores()

# -------------------------
# 5. KPI TARGETS (STATIC TABLE)
# -------------------------
st.markdown("## KPI Targets")
st.markdown("These are the outcome targets against which live KPI performance is evaluated.")

targets_df = pd.DataFrame(
    [(tower, kpi, target) for tower, kpis in tower_kpis.items() for kpi, target in kpis.items()],
    columns=["Tower", "KPI", "Target"]
)

st.dataframe(targets_df, use_container_width=True, hide_index=True)

# -------------------------
# 6. OBSERVED KPI PERFORMANCE (EDITABLE)
# -------------------------
st.markdown("## Observed KPI Performance")
st.markdown(
    "These are the current observed KPI values by business unit. The observability agent can update them in real time."
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
# 7. KPI STATUS + SCORE LOGIC
# -------------------------
st.markdown("## How KPI Values Translate to Tower Scores")
st.info(
    "Each KPI is compared against its target. "
    "Green = target met/exceeded = Score 5, "
    "Amber = near target = Score 3–4, "
    "Red = below threshold = Score 1–2."
)

for tower_name, kpis in tower_kpis.items():
    st.markdown(f"### {tower_name}")

    # Actual observed KPI values
    observed_cols = ["Business Unit"] + list(kpis.keys())
    observed_view = edited_df[observed_cols].copy()
    st.markdown("**Observed KPI Values**")
    st.dataframe(observed_view, use_container_width=True, hide_index=True)

    # RAG status view
    status_view = edited_df[["Business Unit"]].copy()
    for kpi_name, target in kpis.items():
        status_view[kpi_name] = edited_df[kpi_name].apply(
            lambda v: f"{v:.1f}% | {get_status(v, target, scoring_strictness)}"
        )

    st.markdown("**Performance vs Target (RAG Status)**")
    st.dataframe(status_view, use_container_width=True, hide_index=True)

    # KPI to 1-5 score view
    score_view = edited_df[["Business Unit"]].copy()
    score_cols = []
    for kpi_name, target in kpis.items():
        score_col = f"{kpi_name} Score"
        edited_df[score_col] = edited_df[kpi_name].apply(
            lambda v: kpi_to_score(v, target, scoring_strictness)
        )
        score_view[kpi_name] = edited_df[score_col]
        score_cols.append(score_col)

    st.markdown("**Converted 1–5 KPI Scores**")
    st.dataframe(score_view, use_container_width=True, hide_index=True)

    # Tower score
    edited_df[tower_name] = edited_df[score_cols].mean(axis=1)

# -------------------------
# 8. OUTCOME SCORE
# -------------------------
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

# -------------------------
# 9. EXECUTIVE SNAPSHOT
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
# 10. TOWER PERFORMANCE OVERVIEW
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
# 11. RANKED BUSINESS UNITS
# -------------------------
st.markdown("## Ranked Business Units by Outcome Score")

display_df = sorted_df[
    [
        "Business Unit",
        "Application Operations",
        "Application Development",
        "Transformation",
        "AI Governance",
        "Outcome Score",
        "Outcome Status",
    ]
].copy()

display_df.index = range(1, len(display_df) + 1)

st.dataframe(display_df, use_container_width=True)

st.markdown("---")
st.markdown("""
### How to use this dashboard

1. Start with the **KPI Targets** to establish expected business outcomes.
2. Review **Observed KPI Performance** captured from observability signals.
3. Use **Performance vs Target (RAG Status)** to show Green / Amber / Red evaluation.
4. Translate KPI performance into standardized **1–5 KPI Scores**.
5. Roll KPI scores into tower scores, then into an overall **Outcome Score**.
6. Use the simulation controls to show how outcome posture changes in real time.
""")
