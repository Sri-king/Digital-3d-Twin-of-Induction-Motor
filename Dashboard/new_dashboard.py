import sys
import os
import numpy as np
import streamlit as st
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# Fix module path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from simulation.unified_digital_twin import UnifiedDigitalTwin

# -----------------------
# PAGE SETTINGS
# -----------------------

st.set_page_config(
    page_title="Industrial Motor Digital Twin",
    layout="wide"
)

st.title("⚙️ Industrial Induction Motor Digital Twin")

# -----------------------
# SESSION STATE
# -----------------------

if "motor" not in st.session_state:
    st.session_state.motor = UnifiedDigitalTwin()

if "history" not in st.session_state:
    st.session_state.history = {
        "RPM": [],
        "Temperature": [],
        "Current": [],
        "Vibration": [],
        "Voltage": []
    }

# -----------------------
# SIDEBAR CONTROLS
# -----------------------

st.sidebar.title("Control Panel")

run = st.sidebar.toggle("Run Simulation")

fault_type = st.sidebar.selectbox(
    "Inject Physical Fault",
    [
        "NORMAL_OPERATION",
        "OVERLOAD",
        "THERMAL_TRIP",
        "VOLTAGE_DROP",
        "MECHANICAL_JAM",
        "COOLING_FAILURE"
    ]
)

if st.sidebar.button("Inject Fault"):
    st.session_state.motor.inject_fault(fault_type)

# -----------------------
# SIMULATION STEP
# -----------------------

if run:

    result = st.session_state.motor.step(0.05)

    rpm = result["RPM"]
    temp = result["Temperature"]
    current = result["Current"]
    vib = result["Vibration"]
    volt = result["Voltage"]

    st.session_state.history["RPM"].append(rpm)
    st.session_state.history["Temperature"].append(temp)
    st.session_state.history["Current"].append(current)
    st.session_state.history["Vibration"].append(vib)
    st.session_state.history["Voltage"].append(volt)

    # keep history size manageable
    for key in st.session_state.history:
        if len(st.session_state.history[key]) > 200:
            st.session_state.history[key].pop(0)

# -----------------------
# CURRENT VALUES
# -----------------------

rpm = st.session_state.history["RPM"][-1] if st.session_state.history["RPM"] else 0
temp = st.session_state.history["Temperature"][-1] if st.session_state.history["Temperature"] else 0
current = st.session_state.history["Current"][-1] if st.session_state.history["Current"] else 0
vib = st.session_state.history["Vibration"][-1] if st.session_state.history["Vibration"] else 0

# -----------------------
# METRICS
# -----------------------

c1,c2,c3,c4 = st.columns(4)

c1.metric("RPM", round(rpm,1))
c2.metric("Temperature °C", round(temp,1))
c3.metric("Current A", round(current,2))
c4.metric("Vibration", round(vib,2))

st.divider()

# -----------------------
# MAIN LAYOUT
# -----------------------

left,right = st.columns([1,1])

# -----------------------
# MOTOR DIGITAL TWIN
# -----------------------

with left:

    st.subheader("Motor Rotor Motion")

    angle = rpm * 0.002

    x = np.cos(angle)
    y = np.sin(angle)

    fig_motor = go.Figure()

    fig_motor.add_trace(
        go.Scatter(
            x=[0,x],
            y=[0,y],
            mode="lines+markers",
            line=dict(width=12),
            marker=dict(size=20)
        )
    )

    fig_motor.update_layout(
        xaxis=dict(range=[-1,1],visible=False),
        yaxis=dict(range=[-1,1],visible=False),
        height=450,
        title="Rotor Position"
    )

    st.plotly_chart(fig_motor,use_container_width=True)

# -----------------------
# TELEMETRY CHARTS
# -----------------------

with right:

    st.subheader("Motor Telemetry")

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        y=st.session_state.history["RPM"],
        mode="lines",
        name="RPM"
    ))

    fig.add_trace(go.Scatter(
        y=st.session_state.history["Temperature"],
        mode="lines",
        name="Temperature"
    ))

    fig.add_trace(go.Scatter(
        y=st.session_state.history["Current"],
        mode="lines",
        name="Current"
    ))

    fig.add_trace(go.Scatter(
        y=st.session_state.history["Vibration"],
        mode="lines",
        name="Vibration"
    ))

    fig.update_layout(
        height=450,
        title="Real-Time Monitoring"
    )

    st.plotly_chart(fig,use_container_width=True)

# -----------------------
# FAULT STATUS
# -----------------------

st.divider()

fault_col1,fault_col2 = st.columns(2)

if run:
    status = result["Detected_Fault"]
    injected = result["Injected_Physics_Cause"]
else:
    status = "N/A"
    injected = "N/A"

fault_col1.metric("Injected Fault", injected)
fault_col2.metric("Detected Fault", status)

# -----------------------
# AUTO REFRESH
# -----------------------

if run:
    st_autorefresh(interval=120, key="simloop")