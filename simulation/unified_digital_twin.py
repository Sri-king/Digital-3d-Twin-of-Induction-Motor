import numpy as np
from scipy.integrate import solve_ivp
import core.motor_parameters as p
from core.mechanical_model import calculate_load_torque, mechanical_derivative
from core.electro_thermal_model import calculate_slip, calculate_electrical_state, thermal_derivative
from faults.fault_engine import FaultEngine
from sensors.virtual_sensors import generate_virtual_sensor_data

class UnifiedDigitalTwin:
    def __init__(self):
        self.fault_engine = FaultEngine()
        
        # State Vector: [omega_r (rad/s), T_stator (C)]
        self.state = [0.0, p.T_AMB]
        self.t = 0.0

    def _odes(self, t, y, current_params):
        """
        Derivatives for scipy.integrate
        """
        omega_r, T_stator = y
        
        # 1. Physical Parameters
        V_phase = current_params["V_PHASE"]
        T_rated = current_params["T_RATED"]
        R_th = current_params["R_TH"]
        B = current_params["B"]
        
        # 3. Compute Slip
        slip = calculate_slip(omega_r, p.OMEGA_S_RAD)
        
        # 4. Compute Electrical State
        I_s, T_e, P_loss = calculate_electrical_state(slip, V_phase)
        if V_phase <= 0.1:
            I_s, T_e, P_loss = 0.0, 0.0, 0.0
            
        # 2. Solve Mechanical ODE
        T_L = calculate_load_torque(omega_r, T_rated, p.OMEGA_RATED)
        dom_dt = mechanical_derivative(omega_r, T_e, T_L, p.J_TOTAL, B)
        if omega_r <= 0 and dom_dt < 0:
            dom_dt = 0.0
        omega_r = max(omega_r, 0.0)
            
        # 5. Update Thermal State
        dT_dt = thermal_derivative(T_stator, P_loss, R_th, p.C_TH, p.T_AMB)
        
        return [dom_dt, dT_dt]

    def step(self, dt):
        """
        STRICT SIMULATION LOOP ORDER:    This shouldnt be broken, so handle it cautiously, else...
        1. Apply injected physical fault parameters
        2. Solve mechanical ODE (omega update)
        3. Compute slip
        4. Compute electrical state (current, torque)
        5. Update thermal state (temperature, dT/dt)
        6. Run Physics Rule Engine detection (Layer 1)
        7. Generate noisy virtual sensor outputs
        8. (AI Classifier Prediction is done in main runner using this output)
        9. Log full dataset row
        """
        # 1. Get Params
        current_params = self.fault_engine.get_params()
        
        # Capture pre-step temp for dT/dt approximation
        pre_T = self.state[1]

        # 2-5. SciPy ODE Integration
        sol = solve_ivp(
            fun=lambda t, y: self._odes(t, y, current_params),
            t_span=(self.t, self.t + dt),
            y0=self.state,
            method='RK45'
        )
        
        self.t += dt
        self.state = sol.y[:, -1]
        
        omega_r, T_stator = self.state
        
        # Recalculate discrete states at exactly this timestep
        slip = calculate_slip(omega_r, p.OMEGA_S_RAD)
        I_s, T_e, P_loss = calculate_electrical_state(slip, current_params["V_PHASE"])
        if current_params["V_PHASE"] <= 0:
            I_s, T_e, P_loss = 0.0, 0.0, 0.0
            
        T_L = calculate_load_torque(omega_r, current_params["T_RATED"], p.OMEGA_RATED)
        
        # Approximate true dT/dt
        dT_dt = (T_stator - pre_T) / dt
        rpm = omega_r * (60.0 / (2 * np.pi))

        # 6. Run Physics Rule Engine Detection (Layer 1)
        detected_fault = self.fault_engine.detect_fault_rules(
            rpm=rpm,
            slip=slip,
            current=I_s,
            temperature=T_stator,
            dT_dt=dT_dt,
            load_torque=T_L,
            voltage=current_params["V_PHASE"],
            dt=dt
        )

        ground_truth = {
            'time': self.t,
            'rpm': rpm,
            'slip': slip,
            'current': I_s,
            'temperature': T_stator,
            'electric_torque': T_e,
            'load_torque': T_L,
            'voltage': current_params["V_PHASE"],
            'injected_cause': self.fault_engine.injected_cause,
            'detected_fault': detected_fault
        }

        # 7. Generate Noisy Virtual Sensors
        sensor_data = generate_virtual_sensor_data(ground_truth)
        
        return sensor_data

    def inject_fault(self, fault_type):
        self.fault_engine.inject_fault(fault_type)
