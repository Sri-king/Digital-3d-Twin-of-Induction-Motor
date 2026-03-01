"""
core/motor_parameters.py
Params for a 3-phase Induction Motor coupled with an industrial compressor load.
Follows strict physical models.
"""
import numpy as np

# Electrical Parameters
POLES = 4
FREQ = 50.0  # Hz
V_PHASE_RATED = 230.0  # Volts (Stator phase voltage)
OMEGA_S_RPM = 120.0 * FREQ / POLES  # 1500 RPM
OMEGA_S_RAD = OMEGA_S_RPM * (2 * np.pi / 60.0)  # 157.08 rad/s

R_S = 1.0  # Stator resistance (Ohms)
R_R = 0.8  # Rotor resistance referred to stator (Ohms)
X_S = 2.0  # Stator leakage reactance (Ohms)
X_R = 2.0  # Rotor leakage reactance (Ohms)
X_M = 40.0 # Magnetizing reactance (Ohms)
I_RATED = 10.0 # Rated Stator Current (Amps)

# Mechanical Parameters
J_TOTAL = 0.2  # Inertia of motor + compressor load (kg*m^2)
B_FRICTION = 0.01  # Friction coefficient (N*m*s)

# Load Parameters (Compressor)
T_RATED = 25.0  # Rated torque (N*m)
OMEGA_RATED = 1440 * (2 * np.pi / 60.0)  # Rated speed in rad/s

# Thermal Parameters
C_TH = 500.0  # Thermal capacity (J/K)
R_TH = 0.1    # Thermal resistance (K/W)
T_AMB = 25.0  # Ambient temperature (C)
T_CRITICAL = 120.0 # Thermal Trip Threshold
