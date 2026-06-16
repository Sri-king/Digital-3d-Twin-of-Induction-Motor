import sys
import os
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# Fix module path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from simulation.unified_digital_twin import UnifiedDigitalTwin

st.set_page_config(layout="wide")

st.title(" Induction Motor Digital Twin")

# ---------------------------
# Session Initialization
# ---------------------------

if "motor" not in st.session_state:
    st.session_state.motor = UnifiedDigitalTwin()

if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(
        columns=["time", "rpm", "current", "temperature", "fault"]
    )

if "running" not in st.session_state:
    st.session_state.running = False


# ---------------------------
# Control Panel
# ---------------------------
col1, col2, col3 = st.columns(3)

# Initialize stored fault selection
if "selected_fault" not in st.session_state:
    st.session_state.selected_fault = "NORMAL_OPERATION"

with col1:
    if st.button("▶ Start Simulation"):
        st.session_state.running = True

with col2:
    if st.button("⏹ Stop"):
        st.session_state.running = False

with col3:
    st.session_state.selected_fault = st.selectbox(
        "Inject Fault",
        [
            "NORMAL_OPERATION",
            "OVERLOAD",
            "VOLTAGE_DROP",
            "MECHANICAL_JAM",
            "COOLING_FAILURE",
            "THERMAL_TRIP"
        ],
        index=[
            "NORMAL_OPERATION",
            "OVERLOAD",
            "VOLTAGE_DROP",
            "MECHANICAL_JAM",
            "COOLING_FAILURE",
            "THERMAL_TRIP"
        ].index(st.session_state.selected_fault)
    )

if st.button("Inject Fault"):
    st.session_state.motor.inject_fault(st.session_state.selected_fault)
    st.success(f"Injected: {st.session_state.selected_fault}")

# ---------------------------
# Auto Refresh Loop
# ---------------------------

st_autorefresh(interval=300, key="twinloop")

if st.session_state.running:

    result = st.session_state.motor.step(0.1)

    new_row = {
        "time": result["Time"],
        "rpm": result["RPM"],
        "current": result["Current"],
        "temperature": result["Temperature"],
        "fault": result["Detected_Fault"]
    }

    st.session_state.data = pd.concat(
        [st.session_state.data, pd.DataFrame([new_row])],
        ignore_index=True
    )

# Limit stored data
df = st.session_state.data.tail(300)


# ---------------------------
# Dashboard Layout
# ---------------------------

left, right = st.columns([1,2])


# ---------------------------
# Digital Twin Panel
# ---------------------------

with left:

    st.subheader(" Motor Digital Twin")

    if len(df) > 0:

        latest = df.iloc[-1]

        st.metric("RPM", f"{latest['rpm']:.0f}")
        st.metric("Current (A)", f"{latest['current']:.2f}")
        st.metric("Temperature (°C)", f"{latest['temperature']:.1f}")

        st.markdown("### Fault Information")

        st.write("Injected Fault:", st.session_state.motor.fault_engine.injected_cause)

        st.write("Detected Fault:", latest["fault"])

    else:

        st.info("Simulation not started")


# ---------------------------
# Live Charts
# ---------------------------

with right:

    st.subheader(" Motor Telemetry")

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df["time"],
        y=df["rpm"],
        name="RPM"
    ))

    fig.add_trace(go.Scatter(
        x=df["time"],
        y=df["current"],
        name="Current"
    ))

    fig.add_trace(go.Scatter(
        x=df["time"],
        y=df["temperature"],
        name="Temperature"
    ))

    fig.update_layout(
        height=500,
        template="plotly_dark"
    )

    st.plotly_chart(fig, use_container_width=True)