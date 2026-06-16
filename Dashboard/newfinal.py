import sys
import os
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# Fix module path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from simulation.unified_digital_twin import UnifiedDigitalTwin


# ---------------------------------------------------
# Page Configuration
# ---------------------------------------------------

st.set_page_config(
    page_title="Induction Motor Digital Twin",
    page_icon="⚙",
    layout="wide"
)

st.title("⚙ Induction Motor Digital Twin")
st.markdown("### Real-Time Monitoring • Fault Injection • Predictive Analytics")
st.markdown("---")


# ---------------------------------------------------
# Sidebar (Professional Info Panel)
# ---------------------------------------------------

with st.sidebar:

    st.title("System Information")

    st.write("Motor Type: **Induction Motor**")
    st.write("System Mode: **Digital Twin Monitoring**")

    st.markdown("---")

    st.subheader("Tracked Parameters")

    st.write("• RPM")
    st.write("• Current")
    st.write("• Temperature")
    st.write("• Fault Status")

    st.markdown("---")

    st.caption("Predictive Maintenance Dashboard")


# ---------------------------------------------------
# Session Initialization
# ---------------------------------------------------

if "motor" not in st.session_state:
    st.session_state.motor = UnifiedDigitalTwin()

if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(
        columns=["time", "rpm", "current", "temperature", "fault"]
    )

if "running" not in st.session_state:
    st.session_state.running = False

if "selected_fault" not in st.session_state:
    st.session_state.selected_fault = "NORMAL_OPERATION"


# ---------------------------------------------------
# System Status
# ---------------------------------------------------

status_col1, status_col2 = st.columns(2)

with status_col1:
    if st.session_state.running:
        st.success("🟢 Simulation Running")
    else:
        st.warning("🟡 Simulation Stopped")

with status_col2:
    st.info("Digital Twin Model Active")


# ---------------------------------------------------
# Control Panel
# ---------------------------------------------------

st.markdown("## ⚙ Control Panel")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("▶ Start Simulation", use_container_width=True):
        st.session_state.running = True

with col2:
    if st.button("⏹ Stop Simulation", use_container_width=True):
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


# ---------------------------------------------------
# Auto Refresh Loop
# ---------------------------------------------------

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


# ---------------------------------------------------
# Dashboard Layout
# ---------------------------------------------------

left, right = st.columns([1,2])


# ---------------------------------------------------
# Digital Twin Panel
# ---------------------------------------------------

with left:

    st.subheader("Motor Digital Twin")

    if len(df) > 0:

        latest = df.iloc[-1]

        metric1, metric2, metric3 = st.columns(3)

        with metric1:
            st.metric("⚡ RPM", f"{latest['rpm']:.0f}")

        with metric2:
            st.metric("🔌 Current (A)", f"{latest['current']:.2f}")

        with metric3:
            st.metric("🌡 Temperature (°C)", f"{latest['temperature']:.1f}")

        st.markdown("### Fault Information")

        injected = st.session_state.motor.fault_engine.injected_cause
        detected = latest["fault"]

        if injected != "NORMAL_OPERATION":
            st.error(f"⚠ Injected Fault: {injected}")
        else:
            st.success("✔ Injected Fault: Normal Operation")

        if detected != "NORMAL_OPERATION":
            st.error(f"🚨 Detected Fault: {detected}")
        else:
            st.success("✔ System Operating Normally")

    else:

        st.info("Simulation not started")

    st.markdown("### ⚠ System Alerts")

alerts = []

# Temperature warning
if latest["temperature"] > 80:
    alerts.append(("warning", "Temperature approaching critical limit"))

# Current warning
if latest["current"] > 15:
    alerts.append(("warning", "Current overload detected"))

# Fault detected
if latest["fault"] != "NORMAL_OPERATION":
    alerts.append(("error", f"Fault detected: {latest['fault']}"))

# Display alerts
if alerts:
    for level, message in alerts:

        if level == "warning":
            st.warning(f"⚠ {message}")

        elif level == "error":
            st.error(f"🚨 {message}")

else:
    st.success("✔ System operating within safe limits")


# ---------------------------------------------------
# Live Charts
# ---------------------------------------------------

with right:

    st.subheader("Motor Telemetry")

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df["time"],
        y=df["rpm"],
        name="RPM",
        mode="lines"
    ))

    fig.add_trace(go.Scatter(
        x=df["time"],
        y=df["current"],
        name="Current",
        mode="lines"
    ))

    fig.add_trace(go.Scatter(
        x=df["time"],
        y=df["temperature"],
        name="Temperature",
        mode="lines"
    ))

    fig.update_layout(
        height=520,
        template="plotly_dark",
        title="Real-Time Motor Telemetry",
        xaxis_title="Time",
        yaxis_title="Sensor Values",
        legend_title="Parameters",
        hovermode="x unified"
    )

    st.plotly_chart(fig, use_container_width=True)


# ---------------------------------------------------
# Recent Data Table
# ---------------------------------------------------

st.markdown("### Recent Sensor Data")

st.dataframe(
    df.tail(10),
    use_container_width=True
)


# ---------------------------------------------------
# Footer
# ---------------------------------------------------

st.markdown("---")
st.caption("Digital Twin Monitoring System • Real-Time Fault Detection")