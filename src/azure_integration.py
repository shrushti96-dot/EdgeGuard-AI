import os
from typing import Dict, Any, Optional

class AzureMLManager:
    """
    Handles enterprise Azure Machine Learning workspace connectivity,
    model registry artifact synchronization, and IoT Edge deployment staging.
    Designed for zero-crash fallback when cloud credentials are unconfigured.
    """
    def __init__(self):
        self.subscription_id = os.getenv("AZURE_SUBSCRIPTION_ID", "").strip()
        self.resource_group = os.getenv("AZURE_RESOURCE_GROUP", "").strip()
        self.workspace_name = os.getenv("AZURE_WORKSPACE_NAME", "").strip()
        self.tenant_id = os.getenv("AZURE_TENANT_ID", "").strip()
        self.client_id = os.getenv("AZURE_CLIENT_ID", "").strip()
        self.client_secret = os.getenv("AZURE_CLIENT_SECRET", "").strip()

    def get_status(self) -> Dict[str, Any]:
        """
        Inspects the current Azure cloud environment configuration.
        Returns a status dictionary suitable for dashboard inspection.
        """
        configured_vars = {}
        missing_vars = []

        for key, val in [
            ("AZURE_SUBSCRIPTION_ID", self.subscription_id),
            ("AZURE_RESOURCE_GROUP", self.resource_group),
            ("AZURE_WORKSPACE_NAME", self.workspace_name),
        ]:
            if val:
                # Mask subscription id for security
                masked = f"{val[:6]}...{val[-4:]}" if len(val) > 10 else "***"
                configured_vars[key] = masked
            else:
                missing_vars.append(key)

        is_auth_configured = bool(self.client_id and self.client_secret and self.tenant_id)
        is_ready = len(missing_vars) == 0

        if is_ready:
            status = "CONFIGURED"
            detail = (
                f"Azure ML workspace '{self.workspace_name}' is targeted in resource group '{self.resource_group}'. "
                f"Authentication mode: {'Service Principal' if is_auth_configured else 'DefaultAzureCredential / Azure CLI'}."
            )
        else:
            status = "LOCAL_SIMULATION_MODE"
            detail = (
                f"Cloud parameters missing: {', '.join(missing_vars)}. "
                "Running in isolated Local Edge mode. Model runs locally via edge runtime."
            )

        return {
            "status": status,
            "is_ready": is_ready,
            "workspace_name": self.workspace_name or "Not configured (Local Edge)",
            "resource_group": self.resource_group or "Not configured",
            "subscription_id": configured_vars.get("AZURE_SUBSCRIPTION_ID", "Not configured"),
            "auth_type": "Service Principal" if is_auth_configured else "DefaultAzureCredential / Local CLI",
            "detail": detail,
            "missing_vars": missing_vars,
            "edge_runtime_mode": "Active (Local container / native Python runtime)"
        }

    def register_model(
        self,
        model_path: str,
        model_name: str = "edgeguard-machine-health",
        description: str = "RandomForest predictive maintenance model for industrial edge condition monitoring",
        version: str = "1.0.0",
        tags: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Registers local joblib model artifact with Azure Machine Learning Model Registry (v2 SDK).
        Safely catches network/credential errors and returns clear actionable responses.
        """
        if not os.path.exists(model_path):
            return {
                "success": False,
                "error": f"Model artifact not found at {model_path}. Please train the model first.",
                "registered": False
            }

        status = self.get_status()
        if not status["is_ready"]:
            return {
                "success": False,
                "registered": False,
                "error": f"Azure ML credentials not set. Missing: {', '.join(status['missing_vars'])}",
                "instructions": (
                    "To enable cloud model registration:\n"
                    "1. Copy .env.example to .env\n"
                    "2. Set AZURE_SUBSCRIPTION_ID, AZURE_RESOURCE_GROUP, and AZURE_WORKSPACE_NAME\n"
                    "3. Run 'az login' or supply Service Principal credentials\n"
                    "4. Re-run model registration"
                )
            }

        try:
            # Lazy import to ensure app starts even if azure-ai-ml has platform issues
            from azure.identity import DefaultAzureCredential, ClientSecretCredential
            from azure.ai.ml import MLClient
            from azure.ai.ml.entities import Model
            from azure.ai.ml.constants import AssetTypes

            # Select credential
            if self.client_id and self.client_secret and self.tenant_id:
                credential = ClientSecretCredential(
                    tenant_id=self.tenant_id,
                    client_id=self.client_id,
                    client_secret=self.client_secret
                )
            else:
                credential = DefaultAzureCredential(exclude_interactive_browser_credential=False)

            ml_client = MLClient(
                credential=credential,
                subscription_id=self.subscription_id,
                resource_group_name=self.resource_group,
                workspace_name=self.workspace_name
            )

            azure_model = Model(
                name=model_name,
                version=version,
                path=model_path,
                type=AssetTypes.CUSTOM_MODEL,
                description=description,
                tags=tags or {
                    "framework": "scikit-learn",
                    "task": "predictive-maintenance",
                    "edge_target": "azure-iot-edge",
                    "system": "EdgeGuard-AI"
                }
            )

            registered_model = ml_client.models.create_or_update(azure_model)

            return {
                "success": True,
                "registered": True,
                "model_id": registered_model.id,
                "model_name": registered_model.name,
                "version": registered_model.version,
                "workspace": self.workspace_name,
                "message": f"Successfully registered model '{model_name}' version '{version}' to Azure ML Registry."
            }

        except Exception as ex:
            return {
                "success": False,
                "registered": False,
                "error": f"Azure ML registration error: {str(ex)}",
                "instructions": "Ensure Azure credentials have Contributor or Azure ML Data Scientist role on the target workspace."
            }
