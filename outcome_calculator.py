import streamlit as st
import pandas as pd
import numpy as np
import os
import random

st.set_page_config(page_title="Ericsson Outcome Calculator", layout="wide")

st.markdown("""
# Ericsson Outcome Intelligence Dashboard
### Observability-driven Outcome Calculator
""")
st.markdown("---")

# -------------------------
# 1. SIDEBAR – GLOBAL SETTINGS
# -------------------------
st.sidebar.title("Outcome Control Panel")

st.sidebar.markdown("### Outcome Tower Weights (sum ≈ 100%)")
w_ops = st.sidebar.slider("Application Operations %", 0, 50, 30, 1)
w_dev = st.sidebar.slider("Application Development %", 0, 50, 25, 1)
w_trans = st.sidebar.slider("Transformation %", 0, 50, 25, 1)
w_ai_gov = st.sidebar.slider("AI Governance %", 0, 50, 20, 1)

weight_sum = w_ops + w_dev + w_trans + w_ai_gov
if weight_sum == 0:
    weight_sum = 1

tower_weights = {
    "Application Operations": w_ops / weight_sum,
    "Application Development": w_dev / weight_sum,
    "Transformation": w_trans / weight_sum,
    "AI Governance": w_ai_gov / weight_sum,
}

st.sidebar.markdown("---")
outcome_threshold = st.sidebar.slider("Minimum Outcome Score", 0.0, 5.0, 3.5, 0.1)
st.sidebar.markdown("Delivery Units with Outcome Score ≥ threshold will be flagged as **Strong**.")

# -------------------------
# 2. SAMPLE BASELINE DATA
# -------------------------
@st.cache_data
def load_observed_scores():
    if os.path.exists("outcome_observations.csv"):
        return pd.read_csv("outcome_observations.csv")

    return pd.DataFrame(
        [
            ["ERP Managed Services", 4.0, 3.5, 3.0, 4.5],
            ["Digital Commerce", 3.5, 4.0, 4.5, 3.5],
            ["Supply Chain Platforms", 4.5, 3.0, 3.5, 4.0],
            ["Customer Experience Apps", 3.0, 4.5, 4.0, 3.0],
            ["Network Services", 4.0, 3.0, 4.0, 4.5],
            ["Business Support Systems", 3.5, 3.5, 3.0, 4.0],
            ["Enterprise Platforms", 4.5, 4.0, 4.5, 4.5],
            ["Field Operations Apps", 3.0, 3.5, 3.5, 3.0],
        ],
        columns=[
            "Delivery Unit",
            "Application Operations",
            "Application Development",
            "Transformation",
            "AI Governance",
        ],
    )

def run_observability_agent(run_id=0):
    rng = random.Random(1000 + run_id)

    out = load_observed_scores().copy()

    score_cols = [
        "Application Operations",
        "Application Development",
        "Transformation",
        "AI Governance",
    ]

    for col in score_cols:
        if col not in out.columns:
            out[col] = 3.0

    def dramatic_score(x):
        if rng.random() < 0.9:
            return rng.choice([1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0])
        return x

    for col in score_cols:
        out[col] = out[col].apply(dramatic_score)

    out.to_csv("outcome_observations.csv", index=False)

if "agent_run_id" not in st.session_state:
    st.session_state.agent_run_id = 0

st.markdown("### Observability Agent")

if st.button("Simulate new outcome telemetry (run agent)"):
    st.session_state.agent_run_id += 1
    run_observability_agent(st.session_state.agent_run_id)
    load_observed_scores.clear()

    events = [
        "Incident spike detected in Application Operations telemetry",
        "Release acceleration improved Application Development outcomes",
        "Transformation momentum increased due to automation adoption",
        "AI Governance variance identified in compliance and audit controls",
        "Operational stability improved due to reduced failure rates",
    ]

    rng = random.Random(5000 + st.session_state.agent_run_id)
    st.info(f"Observability Insight: {rng.choice(events)}")

    st.rerun()

df = load_observed_scores()
df.index = df.index + 1

# -------------------------
# 3. EDITABLE TABLE
# -------------------------
st.markdown("## Ericsson Outcome Metrics – Delivery Units")
st.markdown(
    "You can fine-tune 1–5 outcome scores below. The Outcome engine recomputes weighted scores in real time."
)

edited_df = st.data_editor(
    df,
    use_container_width=True,
    num_rows="fixed",
    column_config={
        "Application Operations": st.column_config.NumberColumn(min_value=1.0, max_value=5.0, step=0.5),
        "Application Development": st.column_config.NumberColumn(min_value=1.0, max_value=5.0, step=0.5),
        "Transformation": st.column_config.NumberColumn(min_value=1.0, max_value=5.0, step=0.5),
        "AI Governance": st.column_config.NumberColumn(min_value=1.0, max_value=5.0, step=0.5),
    },
)

# -------------------------
# 4. OUTCOME CALCULATION
# -------------------------
def compute_outcome_score(row, w):
    return (
        row["Application Operations"] * w["Application Operations"] +
        row["Application Development"] * w["Application Development"] +
        row["Transformation"] * w["Transformation"] +
        row["AI Governance"] * w["AI Governance"]
    )

edited_df["Outcome Score"] = edited_df.apply(
    lambda r: compute_outcome_score(r, tower_weights), axis=1
)

edited_df["Outcome Status"] = np.where(
    edited_df["Outcome Score"] >= outcome_threshold,
    "🟢 Strong",
    "🔴 At Risk"
)

sorted_df = edited_df.sort_values("Outcome Score", ascending=False).reset_index(drop=True)
sorted_df.index = sorted_df.index + 1

# -------------------------
# 5. EXECUTIVE SNAPSHOT
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
# 6. MAIN LAYOUT
# -------------------------
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### Ranked Delivery Units by Outcome Score")
    st.dataframe(
        sorted_df[
            [
                "Delivery Unit",
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

with col2:
    st.markdown("### Outcome Summary")

    col_a, col_b, col_c = st.columns(3)

    with col_a:
        st.metric("Minimum Outcome Score", f"{outcome_threshold:.1f}")

    with col_b:
        st.metric("Strong Units", f"{strong_units} / {len(sorted_df)}")

    with col_c:
        st.metric("Top Outcome Score", f"{top_outcome:.2f}")

    st.markdown("### Tower Weights")
    st.write(
        {
            "Application Operations": round(tower_weights["Application Operations"], 2),
            "Application Development": round(tower_weights["Application Development"], 2),
            "Transformation": round(tower_weights["Transformation"], 2),
            "AI Governance": round(tower_weights["AI Governance"], 2),
        }
    )

st.markdown("---")
st.markdown("""
### How to use the Outcome Calculator

1. Use the **Observability Agent** to simulate live telemetry changes.
2. Adjust the **tower weights** to reflect Ericsson priorities.
3. Fine-tune **Delivery Unit scores** directly in the editable table.
4. Review the **Outcome Score, status, and ranking** in real time.
5. Use the **Executive Snapshot** and **Tower Performance Overview** for leadership storytelling.
""")
