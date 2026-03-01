import time
import threading
import sys
import os
import pandas as pd

from simulation.unified_digital_twin import UnifiedDigitalTwin
from ai.fault_classifier import AIFaultClassifier
from visualization.dashboard_3d import Dashboard3D
from visualization.live_plots import LivePlotter

# ============================================================
# GLOBAL STATE (REAL-TIME CONTROL)
# ============================================================
current_injected_fault = "NORMAL_OPERATION"
simulation_running = True


# ============================================================
# MODE 1: BULK DATASET GENERATION (AI TRAINING DATA)
# ============================================================
def run_bulk_dataset_generation():
    """
    Offline fast simulation to generate high-quality synthetic IoT dataset
    using real physics + faults.
    """
    print("\n[MODE 1] Initializing Bulk Dataset Generation...")
    
    twin = UnifiedDigitalTwin()
    dt = 0.05  # 50 ms timestep (industrial standard)
    dataset = []

    # Carefully designed realistic industrial fault sequence
    scenarios = [
        ("NORMAL_OPERATION", 100),
        ("OVERLOAD", 50),
        ("NORMAL_OPERATION", 50),
        ("VOLTAGE_DROP", 60),
        ("NORMAL_OPERATION", 40),
        ("MECHANICAL_JAM", 20),
        ("NORMAL_OPERATION", 30),
        ("COOLING_FAILURE", 80),
        ("NORMAL_OPERATION", 50),
        ("THERMAL_TRIP", 50)
    ]

    total_time = sum(duration for _, duration in scenarios)
    total_steps = int(total_time / dt)

    print(f"Executing {len(scenarios)} scenarios over {total_time} virtual seconds")
    print(f"Total simulation steps: {total_steps}")

    for fault, duration in scenarios:
        print(f"Running Scenario: {fault}")
        twin.inject_fault(fault)
        steps = int(duration / dt)

        for _ in range(steps):
            sensor_data = twin.step(dt)

            # Industrial failsafe: automatic breaker trip
            if twin.state[1] > 120.0 and fault != "THERMAL_TRIP":
                twin.inject_fault("THERMAL_TRIP")

            dataset.append(sensor_data)

    print("\nSimulation complete. Structuring dataset...")
    df = pd.DataFrame(dataset)
    df.to_csv("synthetic_dataset.csv", index=False)

    print(f"SUCCESS: {len(dataset)} IoT records saved to 'synthetic_dataset.csv'")
    print("Dataset ready for AI training.\n")


# ============================================================
# USER INPUT THREAD (LIVE FAULT INJECTION)
# ============================================================
def user_input_thread():
    """
    Background thread for real-time fault injection commands.
    """
    global current_injected_fault, simulation_running

    print("\n--- INTERACTIVE DIGITAL TWIN CONTROL ---")
    print("Commands:")
    print("1 or normal       -> Normal Operation")
    print("2 or overload     -> Overload")
    print("3 or temptrip     -> Thermal Trip")
    print("4 or voltdrop     -> Voltage Drop")
    print("5 or jam          -> Mechanical Jam")
    print("6 or coolingfail  -> Cooling Failure")
    print("exit              -> Stop Simulation\n")

    while simulation_running:
        try:
            cmd = input().strip().lower()

            if cmd == "exit":
                simulation_running = False
                break
            elif cmd in ["1", "normal"]:
                current_injected_fault = "NORMAL_OPERATION"
            elif cmd in ["2", "overload"]:
                current_injected_fault = "OVERLOAD"
            elif cmd in ["3", "temptrip"]:
                current_injected_fault = "THERMAL_TRIP"
            elif cmd in ["4", "voltdrop"]:
                current_injected_fault = "VOLTAGE_DROP"
            elif cmd in ["5", "jam"]:
                current_injected_fault = "MECHANICAL_JAM"
            elif cmd in ["6", "coolingfail"]:
                current_injected_fault = "COOLING_FAILURE"
            else:
                continue

            print(f">>> Injected Physical Fault: {current_injected_fault} <<<")

        except EOFError:
            pass


# ============================================================
# MODE 2: REAL-TIME 3D DIGITAL TWIN (MAIN DEMO MODE)
# ============================================================
def run_real_time_interactive():
    """
    Real-Time Hybrid Digital Twin:
    Physics (ODE) + AI + 3D Visualization + Live Plots
    Physics is the MASTER clock (industrial architecture).
    """
    global current_injected_fault, simulation_running

    print("\n[MODE 2] Booting Real-Time Hybrid Digital Twin...")

    # --------------------------------------------------------
    # 1. AI INITIALIZATION (AUTO DATASET HANDLING)
    # --------------------------------------------------------
    ai = AIFaultClassifier()

    if os.path.exists("synthetic_dataset.csv"):
        print("Found dataset. Training AI model...")
        ai.train("synthetic_dataset.csv")
    else:
        print("Dataset not found. Generating dataset automatically...")
        run_bulk_dataset_generation()
        ai.train("synthetic_dataset.csv")

    # --------------------------------------------------------
    # 2. INITIALIZE PHYSICS ENGINE + VISUAL SYSTEMS
    # --------------------------------------------------------
    twin = UnifiedDigitalTwin()
    dashboard3D = Dashboard3D()   # VPython 3D Twin
    plotter = LivePlotter()       # Matplotlib Analytics

    dt = 0.05  # 50 ms real-time step (industrial IoT sampling rate)
    dataset = []

    # Start user input thread (fault control)
    input_thread = threading.Thread(target=user_input_thread, daemon=True)
    input_thread.start()

    print("\nStreaming Physics-Coupled Digital Twin Data...")
    print(f"{'Time':<6} | {'RPM':<6} | {'Current':<8} | {'Temp':<6} | "
          f"{'Injected':<16} | {'Rule_Detect':<16} | {'AI_Predict':<16}")
    print("-" * 100)

    # --------------------------------------------------------
    # 3. MAIN REAL-TIME LOOP (DETERMINISTIC)
    # --------------------------------------------------------
    try:
        while simulation_running:
            loop_start = time.time()  # Anchor real-time clock

            # -------- FAILSAFE PROTECTION (Industrial Logic) --------
            if twin.state[1] > 120.0 and current_injected_fault != "THERMAL_TRIP":
                print("\n!!! CRITICAL: Temperature > 120°C -> Automatic Breaker Trip !!!")
                current_injected_fault = "THERMAL_TRIP"

            # -------- 1. PHYSICS ENGINE (MASTER) --------
            twin.inject_fault(current_injected_fault)
            sensor_data = twin.step(dt)

            # -------- 2. AI PREDICTION (Layer 2 Intelligence) --------
            ai_prediction = ai.predict(sensor_data)
            sensor_data['AI_Predicted_Fault'] = ai_prediction

            # -------- 3. 3D DIGITAL TWIN VISUAL UPDATE --------
            dashboard3D.update(sensor_data, dt)

            # -------- 4. LIVE ANALYTICS DASHBOARD --------
            plotter.update(sensor_data)

            # Memory-safe logging (cap size for long demos)
            if len(dataset) < 5000:
                dataset.append(sensor_data)

            # Console log every 0.5 seconds (10 steps)
            if len(dataset) % 10 == 0:
                print(
                    f"{sensor_data['Time']:5.1f}s | "
                    f"{sensor_data['RPM']:6.0f} | "
                    f"{sensor_data['Current']:8.2f} | "
                    f"{sensor_data['Temperature']:6.1f} | "
                    f"{sensor_data['Injected_Physics_Cause']:<16} | "
                    f"{sensor_data['Detected_Fault']:<16} | "
                    f"{str(ai_prediction):<16}"
                )

            # -------- 5. REAL-TIME CLOCK SYNCHRONIZATION --------
            elapsed = time.time() - loop_start
            sleep_time = max(0, dt - elapsed)
            time.sleep(sleep_time)

    except KeyboardInterrupt:
        simulation_running = False

    print("\nReal-Time Digital Twin Simulation Terminated.")


# ============================================================
# MAIN ENTRY POINT
# ============================================================
def main():
    print("==================================================")
    print("HYBRID PHYSICS-INFORMED DIGITAL TWIN SYSTEM")
    print("3-Phase Induction Motor + AI + 3D Visualization")
    print("==================================================")
    print("Select Execution Mode:")
    print("1: Bulk Dataset Generation (Train AI & Export CSV)")
    print("2: Real-Time Interactive 3D Digital Twin Simulation")

    try:
        choice = input("Enter Mode (1 or 2): ").strip()

        if choice == "1":
            run_bulk_dataset_generation()
        elif choice == "2":
            run_real_time_interactive()
        else:
            print("Invalid choice. Exiting.")

    except KeyboardInterrupt:
        print("\nInterrupted by user.")


if __name__ == "__main__":
    main()