from vpython import *
import math

class Dashboard3D:
    def __init__(self):
        # Scene setup
        scene.title = "High-Fidelity 3-Phase Induction Motor Twin"
        scene.width = 1100; scene.height = 650
        scene.background = vector(0.05,0.05,0.08)
        scene.camera.pos = vector(0, 5, 16)
        scene.camera.axis = vector(0, -2, -16)

        # Base plate
        self.base = box(pos=vector(0, -2.5, 0),
                        size=vector(16, 0.6, 8),
                        color=vector(0.2, 0.2, 0.2))

        # Stator housing (semi-transparent for cutaway effect)
        self.stator = cylinder(
            pos=vector(-4, 0, 0), axis=vector(8, 0, 0),
            radius=2.2,
            color=vector(0.15, 0.25, 0.6),
            opacity=0.3,  # semi-transparent
            shininess=0.6
        )
        # Cooling ribs (rings along stator)
        self.ribs = []
        for i in range(30):
            rib = ring(
                pos=vector(-3.8 + i*0.26, 0, 0),
                axis=vector(1,0,0),
                radius=2.35,
                thickness=0.08,
                color=vector(0.1, 0.2, 0.5),
                opacity=0.3
            )
            self.ribs.append(rib)

        # End shields (bearing covers), also semi-transparent
        self.front_shield = cylinder(
            pos=vector(4, 0, 0), axis=vector(0.8, 0, 0),
            radius=2.3, color=vector(0.6,0.6,0.6), opacity=0.2
        )
        self.rear_shield = cylinder(
            pos=vector(-4.8, 0, 0), axis=vector(0.8, 0, 0),
            radius=2.3, color=vector(0.6,0.6,0.6), opacity=0.2
        )

        # Rotor core
        self.rotor = cylinder(
            pos=vector(-4, 0, 0), axis=vector(8, 0, 0),
            radius=1.1,
            color=vector(0.85, 0.85, 0.9),
            shininess=0.9
        )
        # Rotor slot bars (for visible rotation)
        self.rotor_slots = []
        num_slots = 24
        for i in range(num_slots):
            angle = (2*math.pi * i) / num_slots
            y = 1.15 * math.cos(angle)
            z = 1.15 * math.sin(angle)
            slot = box(
                pos=vector(0, y, z),
                size=vector(8.05, 0.08, 0.08),
                color=vector(0.3, 0.3, 0.35),
                opacity=0.9
            )
            self.rotor_slots.append(slot)

        # Shaft
        self.shaft = cylinder(
            pos=vector(-6, 0, 0), axis=vector(12, 0, 0),
            radius=0.35,
            color=vector(0.9, 0.9, 0.9),
            shininess=1.0
        )
        # Shaft spin marker (red stripe)
        self.shaft_marker = box(
            pos=vector(0, 0.35, 0),
            size=vector(12, 0.12, 0.12),
            color=color.red,
            opacity=0.9
        )
        # Rotor imbalance marker (yellow dot) for visual cue
        self.imbalance_marker = sphere(
            pos=vector(4, 1.1, 0),
            radius=0.12,
            color=color.yellow,
            emissive=True
        )

        # Cooling fan assembly (hub + blades)
        self.fan_hub = cylinder(
            pos=vector(-5.3, 0, 0), axis=vector(0.4, 0, 0),
            radius=0.9,
            color=color.black
        )
        self.fan_blades = []
        for angle in range(0, 360, 45):
            blade = box(
                pos=vector(-5.2, 0, 0),
                size=vector(0.2, 2.4, 0.6),
                color=color.cyan
            )
            blade.rotate(angle=math.radians(angle), axis=vector(1,0,0))
            self.fan_blades.append(blade)
        # Fan cover (transparent cage)
        self.fan_cover = sphere(
            pos=vector(-5.1, 0, 0),
            radius=2.1,
            opacity=0.15,
            color=color.gray(0.7)
        )

        # Terminal box on top
        self.terminal_box = box(
            pos=vector(0, 2.8, 0),
            size=vector(3, 1.6, 2.2),
            color=vector(0.4, 0.4, 0.4)
        )
        # Mounting feet
        self.foot1 = box(
            pos=vector(-2.5, -1.8, 0),
            size=vector(2, 1, 5),
            color=vector(0.3, 0.3, 0.3)
        )
        self.foot2 = box(
            pos=vector(2.5, -1.8, 0),
            size=vector(2, 1, 5),
            color=vector(0.3, 0.3, 0.3)
        )

        # Thermal glow sphere
        self.thermal_glow = sphere(
            pos=vector(0, 0, 0), radius=2.6,
            color=color.blue,
            opacity=0.05
        )

        # Rotating magnetic field arrow
        self.field_arrow = arrow(
            pos=vector(0, 0, 0),
            axis=vector(0, 3, 0),
            color=color.yellow,
            shaftwidth=0.2,
            headwidth=0.5,
            headlength=0.7
        )

        # HUD labels for Fault status
        self.label_injected = label(pos=vector(-6, 4, 0), height=18, box=False)
        self.label_rule     = label(pos=vector( 0, 4, 0), height=18, box=False)
        self.label_ai       = label(pos=vector( 6, 4, 0), height=18, box=False)

        self.vibration_phase = 0.0  # for sinusoidal wobble

    def _thermal_color(self, temp):
        # Interpolate blue -> yellow -> red over temp range
        t = max(0, min(1, (temp - 25)/100.0))
        return vector(1*t, 0.4*(1-t), 1-t)

    def _status_color(self, text):
        st = str(text).upper()
        if "NORMAL" in st: return color.green
        if "TRIP" in st or "JAM" in st: return color.red
        return color.yellow

    def update(self, sensor_data, dt):
        rate(60)  # Cap to ~60 FPS (VPython renders ~60/sec by default【23†L50-L57】)

        rpm   = sensor_data['RPM']
        temp  = sensor_data['Temperature']
        vib   = sensor_data['Vibration']
        injected = sensor_data['Injected_Physics_Cause']
        rule = sensor_data['Detected_Fault']
        ai   = sensor_data.get('AI_Predicted_Fault', "N/A")

        # ---- Realistic rotation ----
        omega = (rpm * 2*math.pi)/60.0  # rad/s
        angle = omega * dt
        rot_axis = vector(1,0,0)
        origin = vector(0,0,0)

        # Rotate rotor & shaft
        self.rotor.rotate(angle=angle, axis=rot_axis, origin=origin)
        self.shaft.rotate(angle=angle, axis=rot_axis, origin=origin)
        # Rotate rotor slot bars and markers
        for slot in self.rotor_slots:
            slot.rotate(angle=angle, axis=rot_axis, origin=origin)
        self.shaft_marker.rotate(angle=angle, axis=rot_axis, origin=origin)
        self.imbalance_marker.rotate(angle=angle, axis=rot_axis, origin=origin)
        # Rotate fan faster (centrifugal effect)
        for blade in self.fan_blades:
            blade.rotate(angle=angle * 3, axis=rot_axis, origin=vector(-5.2,0,0))

        # ---- Vibration (sinusoidal wobble) ----
        self.vibration_phase += omega * dt
        amp = min(vib / 200.0, 0.12)
        offset = vector(
            amp * math.sin(self.vibration_phase),
            amp * math.cos(self.vibration_phase),
            0
        )
        # Apply to main assembly positions
        self.stator.pos         = vector(-4,0,0) + offset
        self.rotor.pos         = vector(-4,0,0) + offset
        self.shaft.pos         = vector(-6,0,0) + offset
        self.front_shield.pos  = vector(4,0,0) + offset
        self.rear_shield.pos   = vector(-4.8,0,0) + offset
        self.fan_hub.pos       = vector(-5.3,0,0) + offset
        self.fan_cover.pos     = vector(-5.1,0,0) + offset
        self.terminal_box.pos  = vector(0,2.8,0) + offset
        self.thermal_glow.pos  = offset
        for rib in self.ribs:
            rib.pos = vector(rib.pos.x, 0, 0) + offset*0.1  # slight rib motion

        # ---- Thermal color mapping ----
        col = self._thermal_color(temp)
        self.stator.color = col
        self.thermal_glow.color = col
        # Increase glow opacity with heat
        self.thermal_glow.opacity = min(0.35, (temp-30)/200.0)

        # ---- Rotating magnetic field arrow ----
        # Simulate slip by rotating arrow slightly faster than rotor
        self.field_arrow.rotate(angle=angle * 1.2, axis=rot_axis, origin=origin)

        # ---- HUD labels ----
        self.label_injected.text = f"Injected: {injected}"
        self.label_injected.color = self._status_color(injected)
        self.label_rule.text = f"Rule: {rule}"
        self.label_rule.color = self._status_color(rule)
        self.label_ai.text = f"AI: {ai}"
        self.label_ai.color = self._status_color(ai)
