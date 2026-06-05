# MLOps Capstone Project

An end-to-end MLOps pipeline covering data ingestion, model training, experiment tracking, containerization, CI/CD, Kubernetes deployment on AWS EKS, and monitoring with Prometheus and Grafana.

---

## Architecture Overview




Data Pipeline (DVC)
↓
Experiment Tracking (MLflow + DagsHub)
↓
Model Registry
↓
Flask App → Docker Image → AWS ECR → AWS EKS (Kubernetes)
↓
CI/CD via GitHub Actions
↓
Monitoring: Prometheus + Grafana

```

---

## Tech Stack

| Layer | Tools |
| :--- | :--- |
| **Project Structure** | Cookiecutter Data Science |
| **Environment Management** | Conda (Python 3.10) |
| **Data Versioning** | DVC + AWS S3 |
| **Experiment Tracking** | MLflow + DagsHub |
| **Model Serving** | Flask |
| **Containerization** | Docker |
| **Container Registry** | AWS ECR |
| **Orchestration** | Kubernetes on AWS EKS |
| **CI/CD** | GitHub Actions |
| **Monitoring** | Prometheus + Grafana |

---

## Project Structure

```text
├── src/
│   ├── logger/
│   ├── data_ingestion.py
│   ├── data_preprocessing.py
│   ├── feature_engineering.py
│   └── model/
│       ├── model_building.py
│       ├── model_evaluation.py
│       └── register_model.py
├── flask_app/
│   ├── app.py
│   └── requirements.txt
├── tests/
├── scripts/
├── .github/
│   └── workflows/
│       └── ci.yaml
├── dvc.yaml
├── params.yaml
├── Dockerfile
└── requirements.txt

```

---

## Getting Started

### Prerequisites

* Conda
* Git + DVC
* Docker Desktop
* AWS CLI v2 (installed via `.msi`, not via pip)
* `kubectl` and `eksctl`

---

### 1. Environment Setup

```bash
# Clone the repo
git clone <your-repo-url>
cd <repo-name>

# Create and activate conda environment
conda create -n atlas python=3.10
conda activate atlas

# Scaffold with Cookiecutter
pip install cookiecutter
cookiecutter -c v1 [https://github.com/drivendata/cookiecutter-data-science](https://github.com/drivendata/cookiecutter-data-science)

```

---

### 2. Experiment Tracking — MLflow + DagsHub

```bash
pip install dagshub mlflow

```

1. Go to [DagsHub](https://dagshub.com/dashboard) → **Create** → **New Repo** → **Connect GitHub repo**
2. Copy the experiment tracking URL and code snippet from your DagsHub repo page.
3. Run your experiment notebooks.

---

### 3. DVC Pipeline

```bash
dvc init

# Add a local remote (temporary)
dvc remote add -d mylocal local_s3

# Run the full pipeline
dvc repro

# Check pipeline status
dvc status

```

*Pipeline stages are defined in `dvc.yaml`. Hyperparameters live in `params.yaml`.*

---

### 4. AWS S3 as DVC Remote Storage

> **Prerequisites:** Create an IAM user (with S3 + ECR permissions) and an S3 bucket on AWS first.

```bash
pip install "dvc[s3]" awscli

# Configure AWS credentials
aws configure

# Add S3 as DVC remote
dvc remote add -d myremote s3://<your-bucket-name>

# Push data to S3
dvc push

```

---

## Running the Flask App Locally

```bash
pip install flask
cd flask_app
python app.py

```

---

## Docker

```bash
# Build image from the root directory
docker build -t capstone-app:latest .

# Run with your DagsHub token as an environment variable
docker run -p 8888:5000 -e CAPSTONE_TEST=<your-dagshub-token> capstone-app:latest

```

---

## CI/CD — GitHub Actions

The pipeline in `.github/workflows/ci.yaml` handles:

* Running tests from the `tests/` directory
* Building and pushing the Docker image to AWS ECR
* Deploying to AWS EKS

### Required GitHub Secrets

| Secret | Description |
| --- | --- |
| `AWS_ACCESS_KEY_ID` | IAM user access key |
| `AWS_SECRET_ACCESS_KEY` | IAM user secret key |
| `AWS_REGION` | AWS Region (e.g., `us-east-1`) |
| `ECR_REPOSITORY` | ECR repo name (e.g., `capstone-proj`) |
| `AWS_ACCOUNT_ID` | Your 12-digit AWS account ID |
| `CAPSTONE_TEST` | DagsHub auth token |

---

## Kubernetes Deployment — AWS EKS

### Cluster Setup

```bash
# Create the EKS cluster
eksctl create cluster \
  --name flask-app-cluster \
  --region us-east-1 \
  --nodegroup-name flask-app-nodes \
  --node-type t3.small \
  --nodes 1 \
  --nodes-min 1 \
  --nodes-max 1 \
  --managed

# Update kubectl config
aws eks --region us-east-1 update-kubeconfig --name flask-app-cluster

```

### Verify Deployment

```bash
kubectl get nodes
kubectl get namespaces
kubectl get pods
kubectl get svc

```

### Access the App

```bash
# Get the LoadBalancer external IP
kubectl get svc flask-app-service

# Test the endpoint
curl http://<external-ip>:5000

```

> **Note:** Update the EC2 node security group to allow inbound traffic on port `5000`.

### Teardown

```bash
kubectl delete deployment flask-app
kubectl delete service flask-app-service
kubectl delete secret capstone-secret
eksctl delete cluster --name flask-app-cluster --region us-east-1

# Verify deletion
eksctl get cluster --region us-east-1

```

*After deletion, verify all **CloudFormation stacks** are removed from the AWS console to avoid lingering charges.*

---

## Monitoring

### Prometheus Setup (EC2 — Ubuntu, t3.medium)

**Security Group:** Open ports `9090` (Prometheus UI) and `22` (SSH)

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Download and install Prometheus
wget [https://github.com/prometheus/prometheus/releases/download/v2.46.0/prometheus-2.46.0.linux-amd64.tar.gz](https://github.com/prometheus/prometheus/releases/download/v2.46.0/prometheus-2.46.0.linux-amd64.tar.gz)
tar -xvzf prometheus-2.46.0.linux-amd64.tar.gz
sudo mv prometheus-2.46.0.linux-amd64 /etc/prometheus
sudo mv /etc/prometheus/prometheus /usr/local/bin/

```

Edit `/etc/prometheus/prometheus.yml`:

```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: "flask-app"
    static_configs:
      - targets: ["<loadbalancer-external-ip>:5000"]

```

```bash
# Start Prometheus
/usr/local/bin/prometheus --config.file=/etc/prometheus/prometheus.yml

```

---

### Grafana Setup (EC2 — Ubuntu, t3.medium)

**Security Group:** Open ports `3000` (Grafana UI) and `22` (SSH)

```bash
sudo apt update && sudo apt upgrade -y
wget [https://dl.grafana.com/oss/release/grafana_10.1.5_amd64.deb](https://dl.grafana.com/oss/release/grafana_10.1.5_amd64.deb)
sudo apt install ./grafana_10.1.5_amd64.deb -y

sudo systemctl start grafana-server
sudo systemctl enable grafana-server

```

1. Open Grafana at `http://<ec2-public-ip>:3000` (Default credentials: `admin` / `admin`)
2. Add Prometheus as a data source using `http://<prometheus-ec2-ip>:9090`
3. Click **Save and Test** → Start building dashboards!

---

## Important Notes

* **AWS CLI Installation:** Use the official `.msi` installer—**not** `pip install awscli`—to avoid version conflicts with Anaconda environments. Ensure `C:\Program Files\Amazon\AWSCLIV2\` is explicitly included in your system `PATH`.
* **CloudFormation & EKS:** `eksctl` provisions EKS infrastructure via CloudFormation stacks background processes. Always check the AWS console UI after cluster teardown to confirm zero orphaned resources remain active.
* **EC2 Fleet Request Limits:** AWS enforces internal limits on Fleet requests per lifecycle cluster. If node groups fail creation due to a quota constraint, evaluate active Auto Scaling Groups blocking pool allocations.
* **PersistentVolumeClaims (PVCs):** For architectures requiring state persistence, PVCs bind directly to EBS via specialized `StorageClass` configurations. Confirm the AWS EBS CSI driver has been successfully installed cluster-wide before attaching storage.

```

```
