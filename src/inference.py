import os
import time
import joblib
import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple

class EdgeInferenceEngine:
    """
    Lightweight, optimized local edge inference runtime for EdgeGuard AI.
    Loads serialized RandomForest artifact and executes millisecond-scale
    predictive maintenance inference without requiring external cloud connectivity.
    """
    def __init__(self, model_path: str = None):
        if model_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            model_path = os.path.join(base_dir, "models", "machine_health_model.joblib")

        self.model_path = model_path
        self.artifact = None
        self.model = None
        self.feature_names = []
        self.model_version = "Unknown"
        self.baseline_means = {
            "air_temperature": 29.6,
            "process_temperature": 41.9,
            "rotational_speed": 1583.0,
            "torque": 52.9,
            "tool_wear": 122.0,
            "machine_load": 67.0
        }
        self.baseline_stds = {
            "air_temperature": 2.8,
            "process_temperature": 3.1,
            "rotational_speed": 190.0,
            "torque": 6.9,
            "tool_wear": 69.0,
            "machine_load": 15.8
        }
        self._load_model()

    def _load_model(self):
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Model artifact not found at {self.model_path}. Please train the model first.")

        self.artifact = joblib.load(self.model_path)
        if isinstance(self.artifact, dict) and "model" in self.artifact:
            self.model = self.artifact["model"]
            self.feature_names = self.artifact.get("feature_names", list(self.baseline_means.keys()))
            self.model_version = self.artifact.get("model_version", "1.0.0")
        else:
            self.model = self.artifact
            self.feature_names = list(self.baseline_means.keys())
            self.model_version = "1.0.0"

    def predict(self, reading: Dict[str, float], risk_threshold: float = 0.50) -> Dict[str, Any]:
        """
        Executes edge prediction on a single telemetry snapshot.

        Parameters:
            reading (dict): Dictionary with keys:
                - air_temperature
                - process_temperature
                - rotational_speed
                - torque
                - tool_wear
                - machine_load
            risk_threshold (float): Decision cutoff for failure risk alert

        Returns:
            dict containing prediction class, calibrated risk score, risk level,
            edge latency, feature influences, and timestamp.
        """
        t_start = time.perf_counter()

        # Construct single-row DataFrame with explicit ordering
        ordered_data = {feat: [reading.get(feat, self.baseline_means.get(feat, 0.0))] for feat in self.feature_names}
        input_df = pd.DataFrame(ordered_data)

        # Predict probability of failure risk (class 1)
        probabilities = self.model.predict_proba(input_df)[0]
        risk_score = float(probabilities[1])

        # Binary decision based on configured operational threshold
        is_failure_risk = bool(risk_score >= risk_threshold)
        prediction_label = "Failure Risk" if is_failure_risk else "Normal"

        # Categorize risk severity
        if risk_score < 0.30:
            risk_level = "Optimal"
        elif risk_score < 0.50:
            risk_level = "Guarded"
        elif risk_score < 0.75:
            risk_level = "High Warning"
        else:
            risk_level = "Critical Threat"

        # Calculate feature deviations & influence scores
        influences = {}
        total_raw_influence = 0.0
        feature_importances = dict(zip(self.feature_names, self.model.feature_importances_))

        for feat in self.feature_names:
            val = float(reading.get(feat, self.baseline_means[feat]))
            mean = self.baseline_means[feat]
            std = self.baseline_stds[feat]
            z_score = abs(val - mean) / std
            weight = feature_importances.get(feat, 0.16)
            influence = z_score * weight
            influences[feat] = influence
            total_raw_influence += influence

        # Normalize relative feature influence percentages (ensure native Python float)
        if total_raw_influence > 0:
            normalized_influences = {
                feat: float(round((val / total_raw_influence) * 100.0, 1))
                for feat, val in influences.items()
            }
        else:
            normalized_influences = {feat: float(round(100.0 / len(self.feature_names), 1)) for feat in self.feature_names}

        # Sort descending
        sorted_influences = dict(sorted(normalized_influences.items(), key=lambda item: item[1], reverse=True))

        t_end = time.perf_counter()
        latency_ms = round((t_end - t_start) * 1000.0, 2)

        # Physical safety rule boundary check (distinct from statistical ML model)
        safety_violations = []
        if reading.get("process_temperature", 0) > 46.5:
            safety_violations.append("Process Temperature > 46.5°C")
        if reading.get("torque", 0) > 68.0:
            safety_violations.append("Torque > 68.0 Nm")
        if reading.get("tool_wear", 0) > 200.0:
            safety_violations.append("Tool Wear > 200 min")
        speed = reading.get("rotational_speed", 1550.0)
        if speed < 1300.0 or speed > 2150.0:
            safety_violations.append(f"Rotational Speed ({speed} RPM) outside tolerance")

        # Health state categorization
        if is_failure_risk:
            health_state = "Critical"
            status_color = "#ef4444"
        elif risk_score >= 0.32 or len(safety_violations) > 0:
            health_state = "Warning"
            status_color = "#f59e0b"
        else:
            health_state = "Normal"
            status_color = "#10b981"

        return {
            "prediction": 1 if is_failure_risk else 0,
            "status_label": prediction_label,
            "health_state": health_state,
            "status_color": status_color,
            "risk_score": float(round(risk_score, 4)),
            "risk_score_pct": float(round(risk_score * 100.0, 1)),
            "risk_level": risk_level,
            "threshold_used": risk_threshold,
            "latency_ms": latency_ms,
            "safety_violations": safety_violations,
            "has_safety_violation": len(safety_violations) > 0,
            "feature_influences": sorted_influences,
            "input_reading": reading,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }

# Global singleton helper
_inference_engine_instance = None

def get_inference_engine() -> EdgeInferenceEngine:
    global _inference_engine_instance
    if _inference_engine_instance is None:
        _inference_engine_instance = EdgeInferenceEngine()
    return _inference_engine_instance
