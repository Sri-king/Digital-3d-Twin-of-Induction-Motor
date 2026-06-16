import sys
import os
import time
import streamlit as st
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from simulation.unified_digital_twin import UnifiedDigitalTwin


st.set_page_config(layout="wide")

st.title("⚡ Induction Motor Digital Twin Dashboard")

# -----------------------------
# SESSION STATE (IMPORTANT)
# prevents simulation restart
# -----------------------------

if "motor" not in st.session_state:
    st.session_state.motor = UnifiedDigitalTwin()

if "running" not in st.session_state:
    st.session_state.running = False

if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=["rpm","temp","current","torque"])


motor = st.session_state.motor


# -----------------------------
# SIDEBAR CONTROLS
# -----------------------------

st.sidebar.title("Simulation Control")

load = st.sidebar.slider("Load Torque",0,100,20)
voltage = st.sidebar.slider("Voltage",180,260,220)

if st.sidebar.button("Start Simulation"):
    st.session_state.running = True

if st.sidebar.button("Stop Simulation"):
    st.session_state.running = False


# -----------------------------
# LAYOUT
# -----------------------------

col1, col2 = st.columns([1,1])


# -----------------------------
# 3D MOTOR PANEL
# -----------------------------

with col1:

    st.subheader("3D Digital Twin")

    st.components.v1.html("""
    <iframe src="http://localhost:58840"
    width="100%"
    height="500">
    </iframe>
    """,height=520)



# -----------------------------
# CHART PANEL
# -----------------------------

with col2:

    st.subheader("Live Motor Data")

    rpm_chart = st.line_chart(st.session_state.data["rpm"])
    temp_chart = st.line_chart(st.session_state.data["temp"])
    current_chart = st.line_chart(st.session_state.data["current"])
    torque_chart = st.line_chart(st.session_state.data["torque"])


# -----------------------------
# SIMULATION LOOP
# -----------------------------

placeholder = st.empty()

if st.session_state.running:

    result = motor.step(load)

    rpm = result.get("rpm",0)
    temp = result.get("temperature",0)
    current = result.get("current",0)
    torque = result.get("torque",0)

    new_row = pd.DataFrame([[rpm,temp,current,torque]],
        columns=["rpm","temp","current","torque"])

    st.session_state.data = pd.concat(
        [st.session_state.data,new_row],
        ignore_index=True
    )

    rpm_chart.add_rows(new_row[["rpm"]])
    temp_chart.add_rows(new_row[["temp"]])
    current_chart.add_rows(new_row[["current"]])
    torque_chart.add_rows(new_row[["torque"]])

    time.sleep(0.05)

    st.rerun()