import numpy as np

def generate_virtual_sensor_data(ground_truth):
    """
    Applies Gaussian noise to TRUE physical states to mimic an IoT edge node.
    vibration = base + k1*slip + k2*load + N(0, sigma)
    """
    rpm = ground_truth['rpm']
    slip = ground_truth['slip']
    load_torque = ground_truth['load_torque']
    
    # Synthetic Vibration Physics Model
    base_vib = 1.0
    k1 = 50.0  # Slip multiplier factor
    k2 = 0.5   # Torque strain factor
    true_vibration = base_vib + (k1 * slip) + (k2 * load_torque)
    
    sensor_data = {
        'Time': ground_truth['time'],
        'RPM': np.clip(rpm + np.random.normal(0, 5.0), 0, None),
        'Current': max(ground_truth['current'] + np.random.normal(0, 0.4), 0),
        'Temperature': ground_truth['temperature'] + np.random.normal(0, 1.0),
        'Slip': slip + np.random.normal(0, 0.005),
        'Torque': ground_truth['electric_torque'] + np.random.normal(0, 1.0),
        'Load_Torque': load_torque + np.random.normal(0, 1.0),
        'Voltage': ground_truth['voltage'] + np.random.normal(0, 2.0),
        'Vibration': max(true_vibration + np.random.normal(0, 1.5), 0),
        
        # Keep ground truths pristine for dataset logging
        'Injected_Physics_Cause': ground_truth['injected_cause'],
        'Detected_Fault': ground_truth['detected_fault']
    }
    
    return sensor_data
