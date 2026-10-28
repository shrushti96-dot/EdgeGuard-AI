import os
import sys
from dotenv import load_dotenv

# Load local environment variables from .env if present
load_dotenv()

from src.azure_integration import AzureMLManager

def main():
    print("=" * 65)
    print("EdgeGuard AI: Azure Machine Learning Model Registration Utility")
    print("=" * 65)

    base_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(base_dir, "models", "machine_health_model.joblib")

    if not os.path.exists(model_path):
        print(f"[ERROR] Saved model artifact not found at: {model_path}")
        print("Please train the model first by running: python train_model.py")
        sys.exit(1)

    manager = AzureMLManager()
    status = manager.get_status()

    print(f"Target Workspace:   {status['workspace_name']}")
    print(f"Resource Group:     {status['resource_group']}")
    print(f"Subscription ID:    {status['subscription_id']}")
    print(f"Authentication:     {status['auth_type']}")
    print(f"Operational Mode:   {status['status']}")
    print("-" * 65)

    if not status["is_ready"]:
        print("[NOTICE] Azure Cloud Environment is not yet configured.")
        print(status["detail"])
        print("\nSetup Instructions:")
        print("1. Copy .env.example to .env")
        print("2. Populate your Azure Subscription, Resource Group, and Workspace Name")
        print("3. Authenticate via 'az login' or supply Azure Service Principal credentials")
        print("4. Re-run: python azure_ml_register.py")
        print("-" * 65)
        print("[SUCCESS] Local Edge inference remains 100% operational in autonomous mode.")
        return

    print("Attempting to connect to Azure ML Workspace and register model artifact...")
    result = manager.register_model(
        model_path=model_path,
        model_name="edgeguard-rf-machine-health",
        version="1.0.0",
        description="EdgeGuard AI trained Random Forest classifier for industrial IoT edge condition monitoring."
    )

    if result["success"]:
        print(f"[SUCCESS] {result['message']}")
        print(f"Azure Model ID: {result.get('model_id')}")
    else:
        print(f"[FAILED] {result['error']}")
        if "instructions" in result:
            print(f"Recommendation: {result['instructions']}")

if __name__ == "__main__":
    main()
