import core.motor_parameters as p


class FaultEngine:
    def __init__(self):
        # Ground truth injected physical cause (Layer 0)
        self.injected_cause = "NORMAL_OPERATION"

        # Mutable physical parameters (used by simulator each step)
        self.params = self._get_baseline_params()

        # For sustained thermal detection (realistic protection logic)
        self.time_above_critical_temp = 0.0

    def _get_baseline_params(self):
        """
        Returns baseline physical parameters of the motor + system.
        These are the TRUE physics parameters that faults will mutate.
        """
        return {
            "V_PHASE": p.V_PHASE_RATED,
            "T_RATED": p.T_RATED,
            "R_TH": p.R_TH,
            "B": p.B_FRICTION
        }

    # ============================================================
    # LAYER 0: PHYSICAL FAULT INJECTION (GROUND TRUTH)
    # ============================================================
    def inject_fault(self, fault_type):
        """
        Modifies REAL physical parameters.
        NEVER directly changes RPM, current, or temperature.
        Only physics constraints are altered.
        """
        self.injected_cause = fault_type
        self.params = self._get_baseline_params()

        if fault_type == "NORMAL_OPERATION":
            pass

        elif fault_type == "OVERLOAD":
            # Increase rated load torque demand
            self.params["T_RATED"] = p.T_RATED * 1.5

        elif fault_type == "THERMAL_TRIP":
            # Breaker trip → voltage collapses
            self.params["V_PHASE"] = 0.0

        elif fault_type == "VOLTAGE_DROP":
            # 30% supply sag
            self.params["V_PHASE"] = p.V_PHASE_RATED * 0.70

        elif fault_type == "MECHANICAL_JAM":
            # Massive friction + load spike (realistic jam physics)
            self.params["B"] = p.B_FRICTION * 50.0
            self.params["T_RATED"] = p.T_RATED * 3.0

        elif fault_type == "COOLING_FAILURE":
            # Thermal resistance increases (fan failure)
            self.params["R_TH"] = p.R_TH * 5.0

    def get_params(self):
        """
        Simulator MUST call this every time-step.
        This ensures faults actually affect physics.
        """
        return self.params

    # ============================================================
    # LAYER 1: PHYSICS RULE ENGINE (HYBRID DETECTION CORE)
    # ============================================================
    def detect_fault_rules(
        self,
        rpm,
        slip,
        current,
        temperature,
        dT_dt,          # temperature rate of change (IMPORTANT)
        load_torque,
        voltage,
        dt
    ):
        """
        Physics-Informed Rule-Based Fault Detection
        Startup Safe + Transient Aware + Industrial Logic
        """

        # --------------------------------------------------------
        # DERIVED CONSTANTS
        # --------------------------------------------------------
        rated_rpm = p.OMEGA_RATED * (60.0 / (2 * 3.14159))
        low_rpm_threshold = 0.05 * rated_rpm      # ~ stall region
        steady_rpm_threshold = 0.85 * rated_rpm   # near steady state

        # --------------------------------------------------------
        # 1. STARTUP & TRANSIENT IMMUNITY (CRITICAL FIX)
        # Prevent false overload/jam during normal acceleration
        # --------------------------------------------------------
        if rpm < steady_rpm_threshold and temperature < (p.T_AMB + 30):
            return "NORMAL_OPERATION"

        # --------------------------------------------------------
        # 2. TRACK SUSTAINED THERMAL CONDITION (REALISTIC)
        # --------------------------------------------------------
        if temperature > p.T_CRITICAL:
            self.time_above_critical_temp += dt
        else:
            self.time_above_critical_temp = max(
                0.0, self.time_above_critical_temp - dt
            )

        # --------------------------------------------------------
        # 3. THERMAL TRIP (HIGHEST PRIORITY SAFETY FAULT)
        # --------------------------------------------------------
        if self.time_above_critical_temp > 1.5:
            return "THERMAL_TRIP"

        # Breaker trip signature (better than current == 0.0)
        if voltage < 0.1 * p.V_PHASE_RATED and rpm < low_rpm_threshold:
            return "THERMAL_TRIP"

        # --------------------------------------------------------
        # 4. MECHANICAL JAM (PHYSICS-CORRECT LOGIC)
        # --------------------------------------------------------
        if (
            rpm < low_rpm_threshold
            and current > 1.4 * p.I_RATED
            and load_torque > 1.5 * p.T_RATED
        ):
            return "MECHANICAL_JAM"

        # --------------------------------------------------------
        # 5. VOLTAGE DROP (ELECTRICAL DISTURBANCE)
        # --------------------------------------------------------
        if voltage < 0.9 * p.V_PHASE_RATED:
            return "VOLTAGE_DROP"

        # --------------------------------------------------------
        # 6. OVERLOAD (TRANSIENT-SAFE DETECTION)
        # Requires sustained stress, not startup spike
        # --------------------------------------------------------
        if (
            slip > 0.08
            and current > 1.25 * p.I_RATED
            and voltage >= 0.9 * p.V_PHASE_RATED
            and rpm > 0.6 * rated_rpm
        ):
            return "OVERLOAD"

        # --------------------------------------------------------
        # 7. COOLING FAILURE (THERMAL ANOMALY)
        # --------------------------------------------------------
        if (
            dT_dt > 0.8
            and current <= 1.2 * p.I_RATED
            and temperature > (p.T_AMB + 20)
        ):
            return "COOLING_FAILURE"

        # --------------------------------------------------------
        # 8. NORMAL STEADY OPERATION
        # --------------------------------------------------------
        if slip <= 0.06 and temperature < p.T_CRITICAL:
            return "NORMAL_OPERATION"

        # Fallback safe classification
        return "NORMAL_OPERATION"