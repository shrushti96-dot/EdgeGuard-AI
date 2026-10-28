import os
import json
import joblib
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report,
    roc_auc_score
)

def train_and_evaluate(
    data_path: str = "data/machine_sensor_data.csv",
    model_dir: str = "models",
    random_state: int = 42
):
    """
    Trains a RandomForest model for industrial predictive maintenance,
    evaluates actual performance on held-out test data, and persists
    the model artifact and evaluation metrics.
    """
    print("=" * 65)
    print("EdgeGuard AI: Industrial ML Model Training & Evaluation")
    print("=" * 65)

    base_dir = os.path.dirname(os.path.abspath(__file__))
    full_data_path = os.path.join(base_dir, data_path)
    full_model_dir = os.path.join(base_dir, model_dir)
    os.makedirs(full_model_dir, exist_ok=True)

    if not os.path.exists(full_data_path):
        raise FileNotFoundError(f"Dataset not found at {full_data_path}. Please run generate_dataset.py first.")

    # Load dataset
    df = pd.read_csv(full_data_path)
    feature_cols = [
        "air_temperature",
        "process_temperature",
        "rotational_speed",
        "torque",
        "tool_wear",
        "machine_load"
    ]
    target_col = "machine_status"

    X = df[feature_cols]
    y = df[target_col]

    print(f"Loaded dataset: {len(df)} samples, {len(feature_cols)} features.")

    # Stratified Train/Test Split (80% train, 20% test)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=random_state, stratify=y
    )

    print(f"Training set size:   {len(X_train)} samples ({y_train.sum()} failure risks)")
    print(f"Testing set size:    {len(X_test)} samples ({y_test.sum()} failure risks)")

    # Train Random Forest Classifier
    rf_model = RandomForestClassifier(
        n_estimators=120,
        max_depth=12,
        min_samples_split=4,
        min_samples_leaf=2,
        class_weight="balanced_subsample",
        random_state=random_state,
        n_jobs=-1
    )

    print("\nTraining RandomForestClassifier...")
    rf_model.fit(X_train, y_train)

    # Evaluate on held-out test set
    y_pred = rf_model.predict(X_test)
    y_pred_proba = rf_model.predict_proba(X_test)[:, 1]

    acc = float(accuracy_score(y_test, y_pred))
    prec = float(precision_score(y_test, y_pred, zero_division=0))
    rec = float(recall_score(y_test, y_pred, zero_division=0))
    f1 = float(f1_score(y_test, y_pred, zero_division=0))
    roc_auc = float(roc_auc_score(y_test, y_pred_proba))
    cm = confusion_matrix(y_test, y_pred).tolist()

    # Feature importances
    feature_importances = {
        feat: float(imp) for feat, imp in zip(feature_cols, rf_model.feature_importances_)
    }
    sorted_importances = dict(sorted(feature_importances.items(), key=lambda item: item[1], reverse=True))

    print("\n" + "-" * 65)
    print("ACTUAL TEST-SET PERFORMANCE METRICS:")
    print("-" * 65)
    print(f"Accuracy:        {acc:.4f} ({acc * 100:.2f}%)")
    print(f"Precision:       {prec:.4f} ({prec * 100:.2f}%)")
    print(f"Recall:          {rec:.4f} ({rec * 100:.2f}%)")
    print(f"F1-Score:        {f1:.4f}")
    print(f"ROC-AUC:         {roc_auc:.4f}")
    print("\nConfusion Matrix:")
    print(f"  True Negatives (Normal):    {cm[0][0]:3d}  | False Positives (False Alarm): {cm[0][1]:3d}")
    print(f"  False Negatives (Missed):   {cm[1][0]:3d}  | True Positives (Detected):     {cm[1][1]:3d}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=["Normal", "Failure Risk"]))
    print("Feature Importances:")
    for feat, imp in sorted_importances.items():
        print(f"  - {feat:20s}: {imp * 100:5.2f}%")

    # Serialize model artifact
    model_output_path = os.path.join(full_model_dir, "machine_health_model.joblib")
    artifact_payload = {
        "model": rf_model,
        "feature_names": feature_cols,
        "target_name": target_col,
        "model_version": "1.0.0",
        "algorithm": "RandomForestClassifier",
        "training_samples": len(X_train),
        "test_samples": len(X_test)
    }
    joblib.dump(artifact_payload, model_output_path)
    print(f"\nModel artifact saved to: {model_output_path}")

    # Metrics JSON
    metrics_payload = {
        "model_name": "EdgeGuard-RandomForest-PredictiveMaintenance",
        "model_version": "1.0.0",
        "framework": "scikit-learn",
        "training_samples": len(X_train),
        "test_samples": len(X_test),
        "metrics": {
            "accuracy": round(acc, 4),
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1_score": round(f1, 4),
            "roc_auc": round(roc_auc, 4)
        },
        "confusion_matrix": {
            "true_negative": cm[0][0],
            "false_positive": cm[0][1],
            "false_negative": cm[1][0],
            "true_positive": cm[1][1],
            "raw_matrix": cm
        },
        "feature_importances": sorted_importances,
        "features": feature_cols,
        "target": target_col
    }

    metrics_output_path = os.path.join(full_model_dir, "model_metrics.json")
    with open(metrics_output_path, "w") as f:
        json.dump(metrics_payload, f, indent=4)
    print(f"Metrics saved to:        {metrics_output_path}")
    print("=" * 65)

    return metrics_payload

if __name__ == "__main__":
    train_and_evaluate()
