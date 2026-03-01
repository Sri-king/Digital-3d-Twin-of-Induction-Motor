import numpy as np
import core.motor_parameters as p

def calculate_slip(omega_r, omega_s):
    """
    s = (Ns - Nr) / Ns
    Prevent slip from being exactly 0 to avoid division by zero in impedance.
    """
    slip = (omega_s - omega_r) / omega_s
    if abs(slip) < 1e-4:
        slip = 1e-4 * np.sign(slip) if slip != 0 else 1e-4
    return slip

def calculate_electrical_state(slip, V_phase):
    """
    Returns (I_s, T_e, P_loss)
    Uses the Motor Equivalent Circuit.
    """
    Z_rotor = (p.R_R / slip) + 1j * p.X_R
    Z_mag = 1j * p.X_M
    Z_f = (Z_mag * Z_rotor) / (Z_mag + Z_rotor)
    
    Z_eq = p.R_S + 1j * p.X_S + Z_f
    
    # Phase current
    I_s_complex = V_phase / Z_eq
    I_s_mag = np.abs(I_s_complex)
    
    # Air-gap power
    E_1 = V_phase - I_s_complex * (p.R_S + 1j * p.X_S)
    I_r_complex = E_1 / Z_rotor
    I_r_mag = np.abs(I_r_complex)
    
    P_ag = 3 * (I_r_mag**2) * (p.R_R / slip)
    T_e = P_ag / p.OMEGA_S_RAD
    
    # Copper Losses
    P_loss = 3 * (I_s_mag**2) * p.R_S + 3 * (I_r_mag**2) * p.R_R
    
    return I_s_mag, T_e, P_loss

def thermal_derivative(T_current, P_loss, R_th, C_th, T_amb):
    """
    dT/dt = (P_loss - (T - T_amb)/R_th) / C_th
    """
    return (P_loss - (T_current - T_amb) / R_th) / C_th
