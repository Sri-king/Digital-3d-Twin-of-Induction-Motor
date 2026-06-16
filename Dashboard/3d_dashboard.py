import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from simulation.unified_digital_twin import UnifiedDigitalTwin
from streamlit_autorefresh import st_autorefresh


# ------------------------------------------------
# PAGE CONFIG
# ------------------------------------------------

st.set_page_config(layout="wide")

st.title("⚙️ Real-Time Motor Digital Twin")

# ------------------------------------------------
# INITIALIZE SYSTEM
# ------------------------------------------------

if "twin" not in st.session_state:
    st.session_state.twin = UnifiedDigitalTwin()

if "data" not in st.session_state:
    st.session_state.data = []

if "running" not in st.session_state:
    st.session_state.running = False

twin = st.session_state.twin


# ------------------------------------------------
# SIDEBAR CONTROL
# ------------------------------------------------

st.sidebar.header("Control Panel")

fault = st.sidebar.selectbox(
    "Inject Fault",
    [
        "NORMAL_OPERATION",
        "OVERLOAD",
        "THERMAL_TRIP",
        "VOLTAGE_DROP",
        "MECHANICAL_JAM",
        "COOLING_FAILURE",
    ],
)

start = st.sidebar.button("Start Simulation")
stop = st.sidebar.button("Stop Simulation")

if start:
    st.session_state.running = True

if stop:
    st.session_state.running = False


# ------------------------------------------------
# AUTO REFRESH (Every 200 ms)
# ------------------------------------------------

if st.session_state.running:
    st_autorefresh(interval=200, key="twin_refresh")


# ------------------------------------------------
# RUN ONE STEP OF SIMULATION
# ------------------------------------------------

if st.session_state.running:

    dt = 0.05

    twin.inject_fault(fault)

    sensor = twin.step(dt)

    st.session_state.data.append(sensor)


# ------------------------------------------------
# DATAFRAME
# ------------------------------------------------

if len(st.session_state.data) > 0:

    df = pd.DataFrame(st.session_state.data)

else:

    df = pd.DataFrame()


# ------------------------------------------------
# KPI DISPLAY
# ------------------------------------------------

col1, col2, col3, col4 = st.columns(4)

if len(df) > 0:

    last = df.iloc[-1]

    col1.metric("RPM", f"{last['RPM']:.0f}")
    col2.metric("Current", f"{last['Current']:.2f} A")
    col3.metric("Temperature", f"{last['Temperature']:.1f} °C")
    col4.metric("Detected Fault", last["Detected_Fault"])


# ------------------------------------------------
# DIGITAL TWIN AREA
# ------------------------------------------------

st.subheader("3D Motor Digital Twin")

st.info(
"""
The 3D motor twin runs in a separate browser window from VPython.

If it hasn't opened yet, run the main simulation once:

python main.py → Mode 2

Then return here and run the dashboard.
"""
)

# ------------------------------------------------
# CHARTS
# ------------------------------------------------

if len(df) > 5:

    c1, c2 = st.columns(2)

    fig_rpm = go.Figure()

    fig_rpm.add_trace(
        go.Scatter(
            y=df["RPM"],
            mode="lines",
            name="RPM",
        )
    )

    fig_rpm.update_layout(title="Motor Speed")

    c1.plotly_chart(fig_rpm, use_container_width=True)


    fig_temp = go.Figure()

    fig_temp.add_trace(
        go.Scatter(
            y=df["Temperature"],
            mode="lines",
            name="Temperature",
        )
    )

    fig_temp.update_layout(title="Temperature")

    c2.plotly_chart(fig_temp, use_container_width=True)


    c3, c4 = st.columns(2)

    fig_current = go.Figure()

    fig_current.add_trace(
        go.Scatter(
            y=df["Current"],
            mode="lines",
            name="Current",
        )
    )

    fig_current.update_layout(title="Motor Current")

    c3.plotly_chart(fig_current, use_container_width=True)


    fig_slip = go.Figure()

    fig_slip.add_trace(
        go.Scatter(
            y=df["Slip"],
            mode="lines",
            name="Slip",
        )
    )

    fig_slip.update_layout(title="Motor Slip")

    c4.plotly_chart(fig_slip, use_container_width=True)


# ------------------------------------------------
# DATA EXPORT
# ------------------------------------------------

if len(df) > 0:

    st.download_button(
        "Download Sensor Data",
        df.to_csv(index=False),
        "motor_dataset.csv"
    )