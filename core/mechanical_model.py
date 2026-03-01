import numpy as np

def calculate_load_torque(omega_r, t_rated, omega_rated):
    """
    Non-linear compressor load torque.
    TL = T_rated * (0.3 + 0.7*(w/w_rated)^2) + disturbance(t)
    """
    if omega_r <= 0.1:
        return 0.0 # Motor starting friction will dominate
        
    ratio = omega_r / omega_rated
    # Add a small aerodynamic disturbance 
    disturbance = np.random.normal(0, 0.5)
    return t_rated * (0.3 + 0.7 * (ratio ** 2)) + disturbance

def mechanical_derivative(omega_r, T_e, T_L, J, B):
    """
    d(omega_r)/dt = (1 / J_total) * (T_e - T_L - B*omega_r)
    """
    return (T_e - T_L - B * omega_r) / J
