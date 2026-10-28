import numpy as np
import pandas as pd
import os

def generate_sensor_dataset(num_records: int = 2500, random_seed: int = 42) -> pd.DataFrame:
    """
    Generates a realistic synthetic industrial machine sensor dataset.
    Features:
      - air_temperature (°C): Ambient air temperature around the equipment
      - process_temperature (°C): Internal machine temperature (air_temp + operational heat)
      - rotational_speed (RPM): Shaft rotational velocity
      - torque (Nm): Mechanical rotational force (inversely correlated with speed)
      - tool_wear (min): Accumulated wear on the cutting/machining tool
      - machine_load (%): Operating capacity percentage
    Target:
      - machine_status (0: Normal, 1: Failure Risk)
    """
    np.random.seed(random_seed)

    # 1. Base environmental & operating features
    air_temp = np.random.normal(loc=29.5, scale=2.8, size=num_records)
    air_temp = np.clip(air_temp, 21.0, 42.0)

    # Machine load between 40% and 95%
    machine_load = np.random.uniform(low=40.0, high=95.0, size=num_records)

    # Process temperature: air_temp + thermal rise
    thermal_load_effect = (machine_load / 100.0) * 6.5
    process_temp = air_temp + 8.0 + thermal_load_effect + np.random.normal(loc=0.0, scale=0.85, size=num_records)

    # Rotational speed (RPM) around 1550
    rotational_speed = np.random.normal(loc=1580.0, scale=190.0, size=num_records)
    rotational_speed = np.clip(rotational_speed, 1100.0, 2600.0)

    # Mechanical Torque (Nm) - physically correlated
    base_torque = 52.0 - (rotational_speed - 1500.0) * 0.025 + (machine_load - 50.0) * 0.18
    torque = base_torque + np.random.normal(loc=0.0, scale=4.2, size=num_records)
    torque = np.clip(torque, 15.0, 85.0)

    # Tool wear (minutes): 0 to 240 min
    tool_wear = np.random.uniform(0.0, 240.0, size=num_records)

    # 2. Physics-inspired failure mechanisms
    twf_score = ((tool_wear / 180.0) ** 2.0) * (torque / 46.0)
    temp_diff = process_temp - air_temp
    hdf_score = np.where(process_temp > 42.0, (process_temp - 42.0) * 0.65, 0.0) + \
                np.where(temp_diff > 13.0, (temp_diff - 13.0) * 0.50, 0.0)
    osf_score = ((torque / 56.0) ** 2.2) + ((torque * tool_wear) / 7200.0)
    speed_anomaly_score = np.where(rotational_speed < 1320, (1320 - rotational_speed) / 75.0, 0.0) + \
                          np.where(rotational_speed > 2100, (rotational_speed - 2100) / 85.0, 0.0)

    # Risk logit
    composite_risk_logit = (
        0.50 * twf_score +
        0.50 * hdf_score +
        0.55 * osf_score +
        0.40 * speed_anomaly_score -
        2.65
    )

    sensor_noise = np.random.normal(loc=0.0, scale=0.45, size=num_records)
    composite_risk_logit += sensor_noise

    failure_probability = 1.0 / (1.0 + np.exp(-composite_risk_logit))
    target = (failure_probability >= 0.50).astype(int)

    # Minor label noise (~3%) so boundary is realistically overlapping
    noise_indices = np.random.choice(num_records, size=int(num_records * 0.03), replace=False)
    target[noise_indices] = 1 - target[noise_indices]

    df = pd.DataFrame({
        "air_temperature": np.round(air_temp, 2),
        "process_temperature": np.round(process_temp, 2),
        "rotational_speed": np.round(rotational_speed, 1),
        "torque": np.round(torque, 2),
        "tool_wear": np.round(tool_wear, 1),
        "machine_load": np.round(machine_load, 1),
        "machine_status": target
    })

    return df

if __name__ == "__main__":
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "machine_sensor_data.csv")

    df = generate_sensor_dataset(num_records=2500, random_seed=42)
    df.to_csv(output_path, index=False)

    failure_count = df["machine_status"].sum()
    normal_count = len(df) - failure_count
    failure_rate = (failure_count / len(df)) * 100

    print("=" * 60)
    print("EdgeGuard AI: Industrial Dataset Generation Completed")
    print("=" * 60)
    print(f"Total Records Generated: {len(df)}")
    print(f"Normal Operation Records: {normal_count} ({100 - failure_rate:.2f}%)")
    print(f"Failure Risk Records:     {failure_count} ({failure_rate:.2f}%)")
    print(f"Saved to: {output_path}")
    print("\nFeature Summary Statistics:")
    print(df.describe().round(2).T[["mean", "std", "min", "50%", "max"]])
