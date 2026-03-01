# Hybrid Physics-Informed Digital Twin

An industrial-grade, multi-domain Digital Twin of a 3-Phase Induction Motor coupled with an industrial compressor load. 

This repository was designed specifically for MSME predict maintenance and automatic downtime classification. It is a true physics-informed simulation driven dynamically by ODE integration, producing high-fidelity synthetic IoT sensor data, and leveraging a Hybrid Fault Detection Engine (Deterministic Rules + Machine Learning).

## Key Features

1. **Multi-Physics ODE Core**: Operates using `scipy.integrate.solve_ivp` across electrical, mechanical ($J \frac{d\omega}{dt}$), and thermal ($C_{th} \frac{dT}{dt}$) domains.
2. **Hybrid Fault Detection Core**: 
   - **Layer 1 (Physics Rules)**: Diagnoses slip, temperature delta ($dT/dt$), and current vectors mathematically.
   - **Layer 2 (AI Intelligence)**: A Scikit-Learn `RandomForestClassifier` trained on rolling timeseries features of the physical outputs.
3. **Physical Fault Parameter Mutation**: Faults are injected by manipulating absolute ground-truth constraints (e.g., Friction Coeff, Stator Resistance, Load Torque) – outputs are *never* mocked or forced.
4. **Real-Time 3D Digital Twin Visualizer**: A VPython 3D Dashboard coupled strictly to the physics variables. Rotor spins precisely via $\Delta \theta = RPM \frac{2\pi}{60} dt$. Stator dynamically maps color to Temperature (°C). Motor jitters precisely to Vibration RMS.
5. **Live Analytics Dashboard**: A non-blocking Matplotlib 2x2 grid displaying continuous sliding-window timeseries data for diagnostics at >30 FPS.

## Installation

This project is built purely in Python and optimized for lightweight edge-hardware or standard laptops. No heavy 3D game engines are required.

```bash
# Install required dependencies
pip install numpy scipy pandas scikit-learn matplotlib vpython
```

## System Architecture

```text
/digital_twin
├── core/
│   ├── motor_parameters.py       # Constants, rated configs
│   ├── mechanical_model.py       # Inertia, load torque curves
│   └── electro_thermal_model.py  # Equivalent circuit, heating
├── faults/
│   └── fault_engine.py           # Ground-truth injection & Layer 1 Rules
├── sensors/
│   └── virtual_sensors.py        # Adds Gaussian noise, synthetic vibration
├── simulation/
│   └── unified_digital_twin.py   # The Master Clock (ODE step integrator)
├── ai/
│   └── fault_classifier.py       # Layer 2 Random Forest (Rolling features)
├── visualization/
│   ├── 3d_dashboard.py           # VPython true-physics 3D model
│   └── live_plots.py             # Matplotlib real-time timeseries
└── main.py                       # Dual-Mode application entrypoint
```

## Execution Modes

Run the digital twin via the orchestration script:
```bash
python main.py
```

### Mode 1: Bulk Dataset Generation
Executes an offline, ultra-fast simulation stepping through predefined physical anomalies (Normal → Overload → Voltage Drop → Jam → Thermal Trip). 
- Generates a ~10,000+ row dataset (`synthetic_dataset.csv`) of pristine IoT sensor data.
- Includes labels for `Injected_Physics_Cause`, `Detected_Fault` (Rule Engine), and `AI_Predicted_Fault`.

### Mode 2: Real-Time Interactive Simulation
Bootstraps the Live 3D Digital Twin environment.
1. Trains the AI Random Forest on the `synthetic_dataset.csv`.
2. Starts the continuous 50ms timestep Physics Engine integration.
3. Opens the Live Matplotlib Dashboard (2x2 Grid).
4. Opens the 3D VPython Engine (in your browser).

You can interactively inject physical disturbances via the terminal while the simulation runs:
- `normal`
- `overload`
- `temptrip`
- `voltdrop`
- `jam`
- `coolingfail`

Watch as the physical equations dynamically adapt, the real-time Matplotlib traces spike, the VPython 3D stator thermally shifts color from blue to red, and the AI HUD predicts the downtime!
