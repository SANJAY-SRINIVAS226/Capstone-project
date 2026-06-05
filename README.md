MLOps Capstone Project
An end-to-end MLOps pipeline covering data ingestion, model training, experiment tracking, containerization, CI/CD, Kubernetes deployment on AWS EKS, and monitoring with Prometheus and Grafana.

Architecture Overview
Data Pipeline (DVC) → Experiment Tracking (MLflow + DagsHub) → Model Registry
        ↓
Flask App (Docker) → ECR → EKS (Kubernetes)
        ↓
CI/CD (GitHub Actions) + Monitoring (Prometheus + Grafana)

Tech Stack
LayerToolsProject StructureCookiecutter Data ScienceData VersioningDVC + AWS S3Experiment TrackingMLflow + DagsHubEnvironment ManagementCondaModel ServingFlaskContainerizationDockerContainer RegistryAWS ECROrchestrationKubernetes (AWS EKS)CI/CDGitHub ActionsMonitoringPrometheus + Grafana

Project Structure
├── src/
│   ├── logger/
│   ├── data_ingestion.py
│   ├── data_preprocessing.py
│   ├── feature_engineering.py
│   ├── model/
│   │   ├── model_building.py
│   │   ├── model_evaluation.py
│   │   └── register_model.py
├── flask_app/
│   ├── app.py
│   ├── requirements.txt
│   └── ...
├── tests/
├── scripts/
├── .github/
│   └── workflows/
│       └── ci.yaml
├── dvc.yaml
├── params.yaml
├── Dockerfile
└── requirements.txt

Getting Started
Prerequisites

Conda
Git + DVC
Docker Desktop
AWS CLI (v2, installed via .msi — not via pip)
kubectl and eksctl

1. Environment Setup
bash# Clone the repository
git clone <https://github.com/SANJAY-SRINIVAS226/Capstone-project>
cd <Capstone-project>

# Create and activate conda environment
conda create -n atlas python=3.10
conda activate atlas

# Scaffold project structure using Cookiecutter
pip install cookiecutter
cookiecutter -c v1 https://github.com/drivendata/cookiecutter-data-science
2. Experiment Tracking (MLflow + DagsHub)
bashpip install dagshub mlflow

Go to DagsHub → Create → New Repo → Connect GitHub repo.
Copy the experiment tracking URL and code snippet from the DagsHub repo page.
Run your experiment notebooks.

3. DVC Pipeline
bashdvc init

# Add local remote (temporary)
dvc remote add -d mylocal local_s3

# Run the full pipeline
dvc repro

# Check pipeline status
dvc status
Pipeline stages are defined in dvc.yaml and hyperparameters in params.yaml.
4. AWS S3 as DVC Remote
bashpip install "dvc[s3]" awscli

# Configure AWS credentials
aws configure

# Add S3 as DVC remote
dvc remote add -d myremote s3://<your-bucket-name>

# Push data to S3
dvc push

AWS Setup Required: Create an IAM user with S3 and ECR permissions, and an S3 bucket before running the above.


Running the Flask App
bashpip install flask
cd flask_app
python app.py

Docker
bash# Build the image from the root directory
docker build -t capstone-app:latest .

# Run with environment variable
docker run -p 8888:5000 -e CAPSTONE_TEST=<your-dagshub-token> capstone-app:latest

CI/CD (GitHub Actions)
The pipeline is defined in .github/workflows/ci.yaml and handles:

Running tests from the tests/ directory
Building and pushing the Docker image to AWS ECR
Deploying to EKS

Required GitHub Secrets
SecretDescriptionAWS_ACCESS_KEY_IDAWS IAM user access keyAWS_SECRET_ACCESS_KEYAWS IAM user secret keyAWS_REGIONe.g., us-east-1ECR_REPOSITORYECR repository name (e.g., capstone-proj)AWS_ACCOUNT_IDYour 12-digit AWS account IDCAPSTONE_TESTDagsHub auth token

Kubernetes Deployment (AWS EKS)
Cluster Setup
bash# Create EKS cluster
eksctl create cluster \
  --name flask-app-cluster \
  --region us-east-1 \
  --nodegroup-name flask-app-nodes \
  --node-type t3.small \
  --nodes 1 --nodes-min 1 --nodes-max 1 \
  --managed

# Update kubectl config
aws eks --region us-east-1 update-kubeconfig --name flask-app-cluster
Verify Deployment
bashkubectl get nodes
kubectl get pods
kubectl get svc
Access the App
bash# Get the LoadBalancer external IP
kubectl get svc flask-app-service

# Test the endpoint
curl http://<external-ip>:5000

Note: Update the EC2 node security group to allow inbound traffic on port 5000.

Teardown
bashkubectl delete deployment flask-app
kubectl delete service flask-app-service
kubectl delete secret capstone-secret
eksctl delete cluster --name flask-app-cluster --region us-east-1
After deletion, verify that all CloudFormation stacks are removed from the AWS console.

Monitoring
Prometheus (EC2 — Ubuntu, t3.medium)

Launch an EC2 instance. Open port 9090 (Prometheus UI) and port 22 (SSH) in the security group.
Install and configure Prometheus:

bashwget https://github.com/prometheus/prometheus/releases/download/v2.46.0/prometheus-2.46.0.linux-amd64.tar.gz
tar -xvzf prometheus-2.46.0.linux-amd64.tar.gz
mv prometheus-2.46.0.linux-amd64 prometheus
sudo mv prometheus /etc/prometheus
sudo mv /etc/prometheus/prometheus /usr/local/bin/

Edit /etc/prometheus/prometheus.yml to point to your Flask app's LoadBalancer address:

yamlglobal:
  scrape_interval: 15s

scrape_configs:
  - job_name: "flask-app"
    static_configs:
      - targets: ["<loadbalancer-external-ip>:5000"]

Start Prometheus:

bash/usr/local/bin/prometheus --config.file=/etc/prometheus/prometheus.yml
Grafana (EC2 — Ubuntu, t3.medium)

Launch an EC2 instance. Open port 3000 (Grafana UI) and port 22 (SSH).
Install and start Grafana:

bashsudo apt update && sudo apt upgrade -y
wget https://dl.grafana.com/oss/release/grafana_10.1.5_amd64.deb
sudo apt install ./grafana_10.1.5_amd64.deb -y
sudo systemctl start grafana-server
sudo systemctl enable grafana-server

Open Grafana at http://<ec2-public-ip>:3000 (default credentials: admin / admin).
Add Prometheus as a data source using the Prometheus EC2 instance's IP and port 9090.


Notes

AWS CLI: Use the .msi installer (not pip install awscli) to avoid conflicts with Anaconda. Ensure C:\Program Files\Amazon\AWSCLIV2\ is in your system PATH.
CloudFormation: eksctl provisions EKS resources via CloudFormation stacks. Verify stack deletion after cluster teardown to avoid lingering charges.
Fleet Request Limits: AWS imposes account-level limits on EC2 Fleet Requests. If NodeGroup creation fails with a quota error, check active Auto Scaling Groups in your account.
PersistentVolumeClaims: If your deployment uses persistent storage, PVCs bind to EBS volumes via a StorageClass. Ensure the EBS CSI driver is installed on the cluster.