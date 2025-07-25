

# Stock Price Prediction with MLOps

## 🎯 Course Project

### Objective

The goal of this project is to apply everything learned in the course to build an end-to-end machine learning system with full MLOps workflow.

---

## 📍 Problem Statement

This project aims to build a sustainable and maintainable stock price prediction system, implementing the complete MLOps lifecycle including data collection, feature engineering, model training, experiment tracking, real-time inference, deployment, and monitoring.

Users can query predicted stock prices and historical trend charts through a web interface. Developers can periodically retrain models, track experiments, monitor performance and data drift, and trigger auto-retraining.

---

## 🧰 Technologies Used

| Category                   | Tools & Frameworks                                                |
| -------------------------- | ----------------------------------------------------------------- |
| **Cloud / Infra**          | Docker Compose (extendable to EC2), MinIO, PostgreSQL, ClickHouse |
| **ML Pipeline**            | FastAPI, Scikit-learn, Pandas, MLflow                             |
| **Workflow Orchestration** | Prefect 2                                                         |
| **Monitoring**             | Evidently + Prometheus + Grafana                                  |
| **CI/CD**                  | GitHub Actions                                                    |
| **Testing**                | pytest (unit + integration tests)                                 |
| **Formatting / Hooks**     | black, pre-commit, flake8                                         |
| **IaC**                    | Docker Compose + Volume + Network (extendable to Terraform)       |

---

## 🏗️ Project Structure

```
.
├── backend/                  # Backend with API, ML logic, workflows
│   ├── api/                  # FastAPI routes (train, predict)
│   ├── src/                  # Feature engineering, model training/inference
│   ├── monitor/              # Monitoring logic using Evidently
│   ├── tasks/                # Celery async tasks
│   ├── workflows/            # Prefect ETL & training flows
│   └── tests/                # Unit & integration tests
├── frontend/                 # Frontend (Vite + React)
├── data/, db/, pgdata/       # Data and DB initialization folders
├── monitor/                  # Prometheus & Grafana configurations
├── Dockerfile.*, docker-compose.yml
├── Makefile, setup.md, implementation_log.md
├── README.md
```

---

## 🔁 Model Lifecycle

1. ETL and training pipelines are triggered regularly via Prefect
2. Training results are logged to MLflow and registered as versioned models
3. FastAPI serves `/predict` and `/train` APIs (Celery-supported)
4. Evidently exports model drift metrics to Prometheus
5. Grafana dashboards visualize prediction accuracy, drift metrics, and system metrics

---

## 🖥️ System Architecture (Mermaid)

```mermaid
graph TD
  %% User Request Flow
  U[User Browser] -->|HTTP/WS Requests| NG[Nginx<br>Static + Reverse Proxy]

  %% Nginx Reverse Proxy
  subgraph Nginx Proxy
    NG -->|/api/predict| UP1
    NG -->|/api/train| UP2
    NG -->|/api/| UP3
    NG -->|/ws| W
    NG -->|Static files<br>/index.html, /js, /css...| Static[React Build]
  end

  %% Upstream Load Balancing Description
  subgraph Upstream Pools
    direction TB
    UP1["backend_predict<br>70% to backend1<br>30% to backend2"]
    UP2["backend_train<br>30% to backend1<br>70% to backend2"]
    UP3["backend_api<br>1:1 to backend1, backend2"]
  end

  %% Backend API (expanded containers)
  subgraph B[Backend API multiple containers]
    B1[backend1:8000]
    B2[backend2:8000]
  end

  UP1 --> B1
  UP1 --> B2
  UP2 --> B1
  UP2 --> B2
  UP3 --> B1
  UP3 --> B2

  %% Backend Interactions
  B1 -->|Query cleaned data| D2[(OLAP<br>ClickHouse)]
  B2 -->|Query cleaned data| D2
  B1 -->|Cache query| E[Redis]
  B2 -->|Cache query| E

  B1 -->|Submit training task| L[Celery Worker]
  B2 -->|Submit training task| L
  B1 -->|Push prediction request| N1[Kafka - prediction topic]
  B2 -->|Push prediction request| N1

  %% Data and ETL Process
  subgraph Data and ETL
    P[Prefect Workflow<br>backend/src/workflows] -->|ETL processing| D1[(raw_db<br>PostgreSQL)]
    P -->|Cleaned data| D2
  end

  %% Training and Inference
  subgraph Model Training
    L -->|Read cleaned data| D2
    L -->|Execute training| G[Model training logic]
    G -->|Model version management| H[MLflow Registry]
    G -->|Update model metadata| D3[(mlflow-db<br>PostgreSQL)]
    H -->|Model Artifact| S[(MinIO<br>Model storage)]
  end

  %% MLflow Internal DB
  subgraph MLflow Internal
    H --> D4[(mlflow internal DB<br>PostgreSQL)]
  end

  %% Monitoring and Real-time Push
  subgraph Monitoring and Push
    W[ws_monitor<br>Kafka Consumer + WebSocket]
    Q[metrics_publisher<br>Fetch & send to Kafka every 5s]
    N1 -->|Prediction result| W
    N2[Kafka - metrics topic]
    Q --> N2
    N2 -->|Metrics| W
    J[Prometheus]
    J -->|Historical data| K[Grafana Dashboard]
  end

  %% Async Task Queue
  subgraph Asynchronous Tasks
    L[Celery Worker] <---> M[Redis Broker]
  end

```

---

## 📈 Evaluation Checklist

### ✅ Problem Definition

* ✔️ Well-defined scope: stock prediction + model lifecycle

### ☁️ Infrastructure

* ✔️ Docker Compose setup with multiple services
* ✔️ Cloud-ready and IaC-friendly (MinIO, DB volumes, Prometheus)

### 🔬 Experiment Tracking

* ✔️ MLflow for logging experiments and model versioning

### 📅 Workflow Orchestration

* ✔️ Prefect 2 for ETL and training flows

### 🚀 Model Deployment

* ✔️ FastAPI for model inference (containerized API)

### 📊 Monitoring

* ✔️ Evidently + Prometheus + Grafana for data/model monitoring

### 🔁 Reproducibility

* ✔️ Makefile + setup.md + requirements + Docker for consistent setup

### 🧪 Best Practices

* [x] Unit tests
* [x] Integration tests
* [x] Code formatting (black, flake8)
* [x] Makefile automation
* [x] Pre-commit hooks
* [x] GitHub Actions for CI

---

## ⚙️ Installation Guide

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt

# Start all services
docker compose up --build

# Run Prefect workflow or one-off training
make train
make workflow
```

---

## 📊 Dataset

Historical stock data from TW & US markets (e.g., 2330.TW, AAPL, TSM):

* Source: Yahoo Finance
* Transformed via ETL and stored in Parquet format (see `workflows/parquet/`)

---

## 🔗 Useful Resources

* [MLFlow Documentation](https://mlflow.org/)
* [Evidently AI Docs](https://docs.evidentlyai.com/)
* [Prefect 2 Docs](https://docs.prefect.io/)
* [Grafana Dashboards](https://grafana.com/grafana/dashboards)

---

## 📜 License

MIT License.
