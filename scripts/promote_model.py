# promote model

import os
import mlflow

def promote_model():
    # Set up DagsHub credentials for MLflow tracking
    dagshub_token = os.getenv("CAPSTONE_TEST")
    if not dagshub_token:
        raise EnvironmentError("CAPSTONE_TEST environment variable is not set")

    os.environ["MLFLOW_TRACKING_USERNAME"] = dagshub_token
    os.environ["MLFLOW_TRACKING_PASSWORD"] = dagshub_token

    dagshub_url = "https://dagshub.com"
    repo_owner = "SANJAY-SRINIVAS226"
    repo_name = "Capstone-project"

    # Set up MLflow tracking URI
    mlflow.set_tracking_uri(f'{dagshub_url}/{repo_owner}/{repo_name}.mlflow')

    client = mlflow.MlflowClient()

    model_name = "my_model"

    # Get all versions of the model
    all_versions = client.search_model_versions(f"name='{model_name}'")
    if not all_versions:
        raise ValueError(f"No versions found for model '{model_name}'")

    # Get the latest version by version number
    latest_version = max(all_versions, key=lambda v: int(v.version))
    latest_version_number = latest_version.version
    print(f"Latest version found: {latest_version_number}")

    # Archive all current production versions
    prod_versions = [v for v in all_versions if v.tags.get("stage") == "Production"]
    for version in prod_versions:
        client.set_model_version_tag(model_name, version.version, "stage", "Archived")
        print(f"Archived version {version.version}")

    # Promote the latest version to production using alias
    client.set_registered_model_alias(model_name, "champion", latest_version_number)
    client.set_model_version_tag(model_name, latest_version_number, "stage", "Production")
    print(f"Model version {latest_version_number} promoted to Production")

if __name__ == "__main__":
    promote_model()