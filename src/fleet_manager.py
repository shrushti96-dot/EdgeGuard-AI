import time
import numpy as np
from typing import Dict, Any, List
from src.inference import get_inference_engine

MACHINE_CONFIGS = [
    {
        "id": "M-01",
        "name": "CNC Machine",
        "type": "Precision CNC Milling",
        "base_rpm": 1640.0,
        "base_torque": 47.5,
        "base_temp": 40.2,
        "base_wear": 35.0,
        "base_load": 62.0,
        "pos": {"x": -16, "z": -8}
    },
    {
        "id": "M-02",
        "name": "Industrial Motor",
        "type": "Heavy AC Induction Drive",
        "base_rpm": 1520.0,
        "base_torque": 52.0,
        "base_temp": 41.5,
        "base_wear": 65.0,
        "base_load": 68.0,
        "pos": {"x": 0, "z": -8}
    },
    {
        "id": "M-03",
        "name": "Hydraulic Press",
        "type": "Metal Stamping 500T",
        "base_rpm": 1420.0,
        "base_torque": 60.5,
        "base_temp": 43.0,
        "base_wear": 95.0,
        "base_load": 76.0,
        "pos": {"x": 16, "z": -8}
    },
    {
        "id": "M-04",
        "name": "Conveyor System",
        "type": "Material Flow Transfer",
        "base_rpm": 1690.0,
        "base_torque": 43.0,
        "base_temp": 39.2,
        "base_wear": 25.0,
        "base_load": 52.0,
        "pos": {"x": -16, "z": 8}
    },
    {
        "id": "M-05",
        "name": "Cooling Unit",
        "type": "Thermal Heat Chiller",
        "base_rpm": 1580.0,
        "base_torque": 49.0,
        "base_temp": 38.5,
        "base_wear": 50.0,
        "base_load": 64.0,
        "pos": {"x": 0, "z": 8}
    },
    {
        "id": "M-06",
        "name": "Assembly Station",
        "type": "Automated Robotic Cell",
        "base_rpm": 1610.0,
        "base_torque": 51.5,
        "base_temp": 41.8,
        "base_wear": 75.0,
        "base_load": 66.0,
        "pos": {"x": 16, "z": 8}
    }
]

class MachineFleetManager:
    """
    Manages telemetry, simulated physics, fault injection states,
    and real ML inference for all 6 industrial machines on the factory floor.
    """
    def __init__(self):
        self.engine = get_inference_engine()
        self.machines: Dict[str, Dict[str, Any]] = {}
        self.event_counter = 0
        self.initialize_fleet()

    def initialize_fleet(self):
        self.machines = {}
        for cfg in MACHINE_CONFIGS:
            m_id = cfg["id"]
            reading = {
                "air_temperature": 29.5,
                "process_temperature": cfg["base_temp"],
                "rotational_speed": cfg["base_rpm"],
                "torque": cfg["base_torque"],
                "tool_wear": cfg["base_wear"],
                "machine_load": cfg["base_load"]
            }
            pred = self.engine.predict(reading, risk_threshold=0.50)
            vibration = self._compute_vibration(reading["rotational_speed"], reading["torque"], reading["tool_wear"])

            self.machines[m_id] = {
                "id": m_id,
                "name": cfg["name"],
                "type": cfg["type"],
                "pos": cfg["pos"],
                "reading": reading,
                "vibration": vibration,
                "prediction": pred["prediction"],
                "status_label": pred["status_label"],
                "health_state": pred.get("health_state", "Normal"),
                "status_color": pred.get("status_color", "#10b981"),
                "risk_score": pred["risk_score"],
                "risk_score_pct": pred["risk_score_pct"],
                "risk_level": pred["risk_level"],
                "latency_ms": pred["latency_ms"],
                "safety_violations": pred.get("safety_violations", []),
                "has_safety_violation": pred.get("has_safety_violation", False),
                "feature_influences": pred["feature_influences"],
                "fault_mode": "None",
                "is_fault_active": False,
                "last_update": time.strftime("%H:%M:%S"),
                "history": [{
                    "event_id": 1,
                    "timestamp": time.strftime("%H:%M:%S"),
                    **reading,
                    "vibration": vibration,
                    "status_label": pred["status_label"],
                    "health_state": pred.get("health_state", "Normal"),
                    "risk_score_pct": pred["risk_score_pct"]
                }]
            }
        self.event_counter = 6

    def _compute_vibration(self, rpm: float, torque: float, wear: float) -> float:
        """Physical empirical vibration estimate (mm/s RMS)."""
        base_vib = 1.6 + (rpm / 1600.0) * 0.8 + (torque / 50.0) * 0.5 + (wear / 200.0) * 0.9
        noise = np.random.normal(0, 0.12)
        return round(float(np.clip(base_vib + noise, 0.8, 12.0)), 2)

    def step_fleet(self, risk_threshold: float = 0.50):
        """Simulates one telemetry tick across all 6 machines."""
        self.event_counter += 1
        current_time = time.strftime("%H:%M:%S")

        for m_id, m in self.machines.items():
            r = m["reading"]
            fault = m["fault_mode"]

            if fault == "Thermal Surge (HDF)":
                r["air_temperature"] = float(np.clip(r["air_temperature"] + 0.35, 28.0, 39.5))
                r["machine_load"] = float(np.clip(r["machine_load"] + 1.2, 82.0, 96.0))
                r["process_temperature"] = float(np.clip(r["process_temperature"] + 0.75, 45.0, 54.0))
                r["torque"] = float(np.clip(r["torque"] + 0.45, 52.0, 68.5))
                r["tool_wear"] = float(np.clip(r["tool_wear"] + 0.4, 80.0, 195.0))
            elif fault == "Mechanical Overstrain (OSF)":
                r["machine_load"] = float(np.clip(r["machine_load"] + 1.6, 88.0, 98.0))
                r["rotational_speed"] = float(np.clip(r["rotational_speed"] - 35, 1120.0, 1340.0))
                r["torque"] = float(np.clip(r["torque"] + 2.0, 68.0, 85.0))
                r["process_temperature"] = float(np.clip(r["process_temperature"] + 0.4, 43.0, 48.5))
            elif fault == "Tool Wear Critical (TWF)":
                r["tool_wear"] = float(np.clip(r["tool_wear"] + 2.0, 205.0, 248.0))
                r["torque"] = float(np.clip(r["torque"] + 0.8, 60.0, 76.0))
                r["process_temperature"] = float(np.clip(r["process_temperature"] + 0.3, 42.0, 47.0))
            elif fault == "Vibration & Bearing Fault":
                r["rotational_speed"] = float(np.random.choice([1160.0, 2350.0]) + np.random.normal(0, 45))
                r["torque"] = float(np.clip(r["torque"] + np.random.normal(0.8, 3.0), 45.0, 72.0))
                r["tool_wear"] = float(np.clip(r["tool_wear"] + 0.3, 40.0, 160.0))
            else:
                # Normal operational drift
                r["air_temperature"] = float(np.clip(r["air_temperature"] + np.random.uniform(-0.15, 0.15), 26.0, 32.5))
                thermal_load = (r["machine_load"] / 100.0) * 6.0
                r["process_temperature"] = float(r["air_temperature"] + 8.2 + thermal_load + np.random.normal(0, 0.2))
                r["rotational_speed"] = float(np.clip(r["rotational_speed"] + np.random.normal(0, 18), 1460.0, 1740.0))
                r["torque"] = float(np.clip(53.0 - (r["rotational_speed"] - 1500) * 0.025 + np.random.normal(0, 1.2), 42.0, 58.0))
                r["tool_wear"] = float(np.clip(r["tool_wear"] + 0.15, 10.0, 145.0))
                r["machine_load"] = float(np.clip(r["machine_load"] + np.random.uniform(-1.2, 1.2), 50.0, 76.0))

            # Round values
            for k in r:
                r[k] = round(r[k], 2 if "temp" in k or "torque" in k else 1)

            # Evaluate with real ML inference
            pred = self.engine.predict(r, risk_threshold=risk_threshold)
            vib = self._compute_vibration(r["rotational_speed"], r["torque"], r["tool_wear"])
            if fault != "None":
                vib = round(vib * 1.85, 2)

            m["vibration"] = vib
            m["prediction"] = pred["prediction"]
            m["status_label"] = pred["status_label"]
            m["health_state"] = pred.get("health_state", "Normal")
            m["status_color"] = pred.get("status_color", "#10b981")
            m["risk_score"] = pred["risk_score"]
            m["risk_score_pct"] = pred["risk_score_pct"]
            m["risk_level"] = pred["risk_level"]
            m["latency_ms"] = pred["latency_ms"]
            m["safety_violations"] = pred.get("safety_violations", [])
            m["has_safety_violation"] = pred.get("has_safety_violation", False)
            m["feature_influences"] = pred["feature_influences"]
            m["last_update"] = current_time

            # Update history
            m["history"].append({
                "event_id": self.event_counter,
                "timestamp": current_time,
                **r,
                "vibration": vib,
                "status_label": pred["status_label"],
                "health_state": pred.get("health_state", "Normal"),
                "risk_score_pct": pred["risk_score_pct"]
            })
            if len(m["history"]) > 40:
                m["history"].pop(0)

    def inject_fault(self, machine_id: str, fault_type: str = "Mechanical Overstrain (OSF)", risk_threshold: float = 0.50):
        if machine_id in self.machines:
            m = self.machines[machine_id]
            m["fault_mode"] = fault_type
            m["is_fault_active"] = True

            r = m["reading"]
            if fault_type == "Thermal Surge (HDF)":
                r["air_temperature"] = 36.2
                r["process_temperature"] = 51.5
                r["machine_load"] = 94.0
                r["torque"] = 62.0
            elif fault_type == "Mechanical Overstrain (OSF)":
                r["rotational_speed"] = 1210.0
                r["torque"] = 78.5
                r["machine_load"] = 96.0
                r["tool_wear"] = 188.0
            elif fault_type == "Tool Wear Critical (TWF)":
                r["tool_wear"] = 235.0
                r["torque"] = 69.5
                r["machine_load"] = 89.0
                r["process_temperature"] = 46.8
            elif fault_type == "Vibration & Bearing Fault":
                r["rotational_speed"] = 2390.0
                r["torque"] = 66.0
                r["machine_load"] = 85.0
                r["tool_wear"] = 170.0

            pred = self.engine.predict(r, risk_threshold=risk_threshold)
            vib = round(self._compute_vibration(r["rotational_speed"], r["torque"], r["tool_wear"]) * 2.3, 2)

            m["vibration"] = vib
            m["prediction"] = pred["prediction"]
            m["status_label"] = pred["status_label"]
            m["health_state"] = pred.get("health_state", "Critical")
            m["status_color"] = pred.get("status_color", "#ef4444")
            m["risk_score"] = pred["risk_score"]
            m["risk_score_pct"] = pred["risk_score_pct"]
            m["risk_level"] = pred["risk_level"]
            m["safety_violations"] = pred.get("safety_violations", [])
            m["has_safety_violation"] = pred.get("has_safety_violation", False)
            m["feature_influences"] = pred["feature_influences"]
            m["last_update"] = time.strftime("%H:%M:%S")

            m["history"].append({
                "event_id": self.event_counter,
                "timestamp": m["last_update"],
                **r,
                "vibration": vib,
                "status_label": pred["status_label"],
                "health_state": m["health_state"],
                "risk_score_pct": pred["risk_score_pct"]
            })
            if len(m["history"]) > 40:
                m["history"].pop(0)

    def clear_fault(self, machine_id: str, risk_threshold: float = 0.50):
        if machine_id in self.machines:
            m = self.machines[machine_id]
            m["fault_mode"] = "None"
            m["is_fault_active"] = False

            # Reset to baseline
            for cfg in MACHINE_CONFIGS:
                if cfg["id"] == machine_id:
                    m["reading"] = {
                        "air_temperature": 29.5,
                        "process_temperature": cfg["base_temp"],
                        "rotational_speed": cfg["base_rpm"],
                        "torque": cfg["base_torque"],
                        "tool_wear": cfg["base_wear"],
                        "machine_load": cfg["base_load"]
                    }
                    break

            pred = self.engine.predict(m["reading"], risk_threshold=risk_threshold)
            vib = self._compute_vibration(m["reading"]["rotational_speed"], m["reading"]["torque"], m["reading"]["tool_wear"])
            m["vibration"] = vib
            m["prediction"] = pred["prediction"]
            m["status_label"] = pred["status_label"]
            m["health_state"] = pred.get("health_state", "Normal")
            m["status_color"] = pred.get("status_color", "#10b981")
            m["risk_score"] = pred["risk_score"]
            m["risk_score_pct"] = pred["risk_score_pct"]
            m["risk_level"] = pred["risk_level"]
            m["safety_violations"] = pred.get("safety_violations", [])
            m["has_safety_violation"] = pred.get("has_safety_violation", False)
            m["feature_influences"] = pred["feature_influences"]
            m["last_update"] = time.strftime("%H:%M:%S")

    def get_fleet_summary(self) -> Dict[str, Any]:
        total = len(self.machines)
        critical_count = sum(1 for m in self.machines.values() if m["health_state"] == "Critical")
        warning_count = sum(1 for m in self.machines.values() if m["health_state"] == "Warning")
        normal_count = sum(1 for m in self.machines.values() if m["health_state"] == "Normal")
        active_alerts = critical_count + warning_count
        avg_risk = round(sum(m["risk_score_pct"] for m in self.machines.values()) / max(total, 1), 1)

        return {
            "total_machines": total,
            "normal_count": normal_count,
            "warning_count": warning_count,
            "critical_count": critical_count,
            "active_alerts": active_alerts,
            "avg_risk_pct": avg_risk,
            "all_healthy": active_alerts == 0
        }
