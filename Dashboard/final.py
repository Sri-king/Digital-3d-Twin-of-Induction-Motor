import sys
import os

# Add project root to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


import streamlit as st
import plotly.graph_objects as go
import numpy as np
import time

from simulation.unified_digital_twin import UnifiedDigitalTwin

st.set_page_config(layout="wide")

st.title("⚡ Industrial Induction Motor Digital Twin")


# ---------------------------------------------------
# Initialize Simulation
# ---------------------------------------------------

if "motor" not in st.session_state:
    st.session_state.motor = UnifiedDigitalTwin()

if "history" not in st.session_state:
    st.session_state.history = {
        "time": [],
        "rpm": [],
        "current": [],
        "temperature": [],
        "vibration": []
    }

if "running" not in st.session_state:
    st.session_state.running = False


motor = st.session_state.motor


# ---------------------------------------------------
# Sidebar Controls
# ---------------------------------------------------

st.sidebar.header("Simulation Controls")

if st.sidebar.button("Start Simulation"):
    st.session_state.running = True

if st.sidebar.button("Stop Simulation"):
    st.session_state.running = False

fault = st.sidebar.selectbox(
    "Inject Fault",
    [
        "NORMAL_OPERATION",
        "OVERLOAD",
        "THERMAL_TRIP",
        "VOLTAGE_DROP",
        "MECHANICAL_JAM",
        "COOLING_FAILURE"
    ]
)

if st.sidebar.button("Apply Fault"):
    motor.inject_fault(fault)


# ---------------------------------------------------
# Layout
# ---------------------------------------------------

col1, col2 = st.columns([1,1])


# ---------------------------------------------------
# 3D DIGITAL TWIN
# ---------------------------------------------------

with col1:

    st.subheader("Motor Digital Twin")

    twin_placeholder = st.empty()


# ---------------------------------------------------
# CHARTS
# ---------------------------------------------------

with col2:

    st.subheader("Live Motor Telemetry")

    chart_placeholder = st.empty()


# ---------------------------------------------------
# Sensor Table
# ---------------------------------------------------

table_placeholder = st.empty()


# ---------------------------------------------------
# Simulation Loop
# ---------------------------------------------------

if st.session_state.running:

    sensor = motor.step(0.1)

    hist = st.session_state.history

    hist["time"].append(sensor["Time"])
    hist["rpm"].append(sensor["RPM"])
    hist["current"].append(sensor["Current"])
    hist["temperature"].append(sensor["Temperature"])
    hist["vibration"].append(sensor["Vibration"])


    # Limit history size (smooth charts)
    max_points = 200

    for key in hist:
        hist[key] = hist[key][-max_points:]


    # ---------------------------------------------------
    # DIGITAL TWIN (simple rotating rotor visual)
    # ---------------------------------------------------

    rpm = sensor["RPM"]

    angle = rpm * 0.05

    twin_fig = go.Figure()

    theta = np.linspace(0, 2*np.pi, 50)

    x = np.cos(theta)
    y = np.sin(theta)

    twin_fig.add_trace(go.Scatter(
        x=x,
        y=y,
        mode="lines",
        line=dict(width=6)
    ))

    rotor_x = [0, np.cos(angle)]
    rotor_y = [0, np.sin(angle)]

    twin_fig.add_trace(go.Scatter(
        x=rotor_x,
        y=rotor_y,
        mode="lines",
        line=dict(width=10)
    ))

    twin_fig.update_layout(
        height=400,
        showlegend=False,
        xaxis=dict(visible=False),
        yaxis=dict(visible=False)
    )

    twin_placeholder.plotly_chart(twin_fig, use_container_width=True)


    # ---------------------------------------------------
    # CHARTS
    # ---------------------------------------------------

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=hist["time"],
        y=hist["rpm"],
        name="RPM"
    ))

    fig.add_trace(go.Scatter(
        x=hist["time"],
        y=hist["current"],
        name="Current"
    ))

    fig.add_trace(go.Scatter(
        x=hist["time"],
        y=hist["temperature"],
        name="Temperature"
    ))

    fig.update_layout(height=400)

    chart_placeholder.plotly_chart(fig, use_container_width=True)


    # ---------------------------------------------------
    # SENSOR TABLE
    # ---------------------------------------------------

    table_placeholder.dataframe(sensor)


    time.sleep(0.1)
    st.rerun()