import random
import numpy as np
from typing import Dict, Any

class IoTSensorSimulator:
    """
    Industrial IoT sensor telemetry stream simulator.
    Simulates physical correlations between ambient environment,
    mechanical load, rotational dynamics, thermal dissipation, and tool degradation.
    """
    def __init__(self):
        # Current state baselines
        self.air_temperature = 29.5
        self.process_temperature = 41.5
        self.rotational_speed = 1580.0
        self.torque = 52.0
        self.tool_wear = 60.0
        self.machine_load = 65.0
        self.event_counter = 0

    def step(self, scenario: str = "Baseline Normal") -> Dict[str, float]:
        """
        Advances the physical simulation by one time step according to selected scenario.
        Scenarios:
          - "Baseline Normal": Stable healthy machine state with realistic brownian noise
          - "Thermal Spike (HDF)": Severe heating, poor heat dissipation
          - "Mechanical Overstrain (OSF)": Extreme torque spike, heavy drag
          - "Degraded Tool Wear (TWF)": Advanced tool wear near catastrophic failure
          - "Rotational Instability": Bearing vibration & abnormal RPM swing
        """
        self.event_counter += 1

        if scenario == "Baseline Normal":
            # Gentle drift around healthy setpoints
            self.machine_load = float(np.clip(self.machine_load + np.random.uniform(-1.5, 1.5), 50.0, 75.0))
            self.air_temperature = float(np.clip(self.air_temperature + np.random.uniform(-0.15, 0.15), 26.0, 32.0))
            thermal_load = (self.machine_load / 100.0) * 6.0
            self.process_temperature = float(self.air_temperature + 8.5 + thermal_load + np.random.normal(0, 0.2))
            self.rotational_speed = float(np.clip(self.rotational_speed + np.random.normal(0, 15), 1480.0, 1720.0))
            self.torque = float(np.clip(53.0 - (self.rotational_speed - 1500) * 0.025 + np.random.normal(0, 1.0), 44.0, 58.0))
            # Tool wear slowly increments
            self.tool_wear = float(np.clip(self.tool_wear + 0.2, 0.0, 140.0))

        elif scenario == "Thermal Spike (HDF)":
            # Temperature climbs rapidly
            self.air_temperature = float(np.clip(self.air_temperature + 0.35, 28.0, 38.0))
            self.machine_load = float(np.clip(self.machine_load + 1.2, 80.0, 96.0))
            self.process_temperature = float(np.clip(self.process_temperature + 0.65, 44.0, 52.5))
            self.rotational_speed = float(np.clip(self.rotational_speed + np.random.normal(0, 25), 1400.0, 1650.0))
            self.torque = float(np.clip(self.torque + 0.4, 52.0, 68.0))
            self.tool_wear = float(np.clip(self.tool_wear + 0.4, 80.0, 190.0))

        elif scenario == "Mechanical Overstrain (OSF)":
            # Severe mechanical resistance and torque surge
            self.machine_load = float(np.clip(self.machine_load + 1.5, 88.0, 98.0))
            self.rotational_speed = float(np.clip(self.rotational_speed - 25, 1150.0, 1380.0))
            self.torque = float(np.clip(self.torque + 1.8, 66.0, 84.0))
            self.process_temperature = float(np.clip(self.process_temperature + 0.4, 43.0, 48.0))
            self.tool_wear = float(np.clip(self.tool_wear + 0.6, 140.0, 230.0))

        elif scenario == "Degraded Tool Wear (TWF)":
            # Tool is past expiration threshold
            self.tool_wear = float(np.clip(self.tool_wear + 1.5, 195.0, 245.0))
            self.torque = float(np.clip(self.torque + np.random.normal(0.5, 2.0), 58.0, 75.0))
            self.machine_load = float(np.clip(self.machine_load + 0.5, 75.0, 92.0))
            self.process_temperature = float(np.clip(self.process_temperature + 0.3, 42.0, 47.0))
            self.rotational_speed = float(np.clip(self.rotational_speed + np.random.normal(0, 35), 1350.0, 1750.0))

        elif scenario == "Rotational Instability":
            # High vibration / bearing anomaly
            self.rotational_speed = float(np.random.choice([1180.0, 2280.0]) + np.random.normal(0, 40))
            self.torque = float(np.clip(self.torque + np.random.normal(0, 3.5), 38.0, 65.0))
            self.machine_load = float(np.clip(self.machine_load + np.random.uniform(-2, 2), 60.0, 85.0))
            self.process_temperature = float(np.clip(self.process_temperature + 0.2, 39.0, 45.0))

        return {
            "air_temperature": round(self.air_temperature, 2),
            "process_temperature": round(self.process_temperature, 2),
            "rotational_speed": round(self.rotational_speed, 1),
            "torque": round(self.torque, 2),
            "tool_wear": round(self.tool_wear, 1),
            "machine_load": round(self.machine_load, 1)
        }

    def reset(self):
        """Resets simulation to standard healthy baseline."""
        self.air_temperature = 29.5
        self.process_temperature = 41.5
        self.rotational_speed = 1580.0
        self.torque = 52.0
        self.tool_wear = 45.0
        self.machine_load = 65.0
        self.event_counter = 0
