

# Stock Price Prediction with MLOps


[繁體中文版](./readme_zh.md)
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
├── .github/                  # GitHub Actions configuration
│   └── workflows/            # GitHub Actions CI/CD workflow
├── .pre-commit-config.yaml   # Pre-commit configuration
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
  %% ------------------- User / Frontend -------------------
  U[User Browser] -->|HTTP/WS Requests| NG[Nginx<br>Static + Reverse Proxy]

  subgraph Nginx_Proxy["Nginx Proxy"]
    NG -->|/api/predict| UP1
    NG -->|/api/train| UP2
    NG -->|/api/| UP3
    NG -->|/ws| W
    NG -->|Static files<br>/index.html, /js, /css...| Static[React Build]
  end

  %% ------------------- Upstream Pools -------------------
  subgraph Upstream_Pools["Upstream Pools"]
    direction TB
    UP1["backend_predict<br>70% to backend1<br>30% to backend2"]
    UP2["backend_train<br>30% to backend1<br>70% to backend2"]
    UP3["backend_api<br>1:1 to backend1, backend2"]
  end

  %% ------------------- Backend Containers -------------------
  subgraph Backend_API["Backend API multiple containers"]
    B1[backend1:8000]
    B2[backend2:8000]
  end

  UP1 --> B1
  UP1 --> B2
  UP2 --> B1
  UP2 --> B2
  UP3 --> B1
  UP3 --> B2

  %% ------------------- Data / ETL -------------------
  subgraph Data_ETL["Data and ETL"]
    P[Prefect Workflow<br>backend/src/workflows] -->|ETL processing| D1[(raw_db<br>PostgreSQL)]
    P -->|Cleaned data| D2[(OLAP<br>ClickHouse)]
  end

  B1 -->|Query cleaned data| D2
  B2 -->|Query cleaned data| D2
  B1 -->|Push task| E[Redis]
  B2 -->|Push task| E

  %% ------------------- Model Training -------------------
  subgraph Model_Training["Model Training & MLflow"]
    L[Celery Worker] -->|Read cleaned data| D2
    L -->|Execute training| G[Model training logic]
    G -->|Model version management| H[MLflow Registry]
    G -->|Update model metadata| D3[(mlflow-db<br>PostgreSQL)]
    H -->|Model Artifact| S[(MinIO<br>Model storage)]
    H --> D4[(mlflow internal DB<br>PostgreSQL)]
  end

  %% ------------------- Monitoring -------------------
  subgraph Monitoring["Monitoring & Real-time Push"]
    W[ws_monitor<br>Kafka Consumer + WebSocket]
    Q[metrics_publisher<br>Fetch & send to Kafka every 5s]
    N1[Kafka - prediction topic] -->|Prediction result| W
    N2[Kafka - metrics topic]
    Q --> N2
    N2 -->|Metrics| W
    J[Prometheus]
    J -->|Historical data| K[Grafana Dashboard]
  end

  %% ------------------- Async Queue -------------------
  subgraph Async_Tasks["Async Task Queue"]
    E --> |Execute| L
  end

  %% ------------------- Styles -------------------
  classDef frontend fill:#FFD966,stroke:#333,stroke-width:2px;
  classDef nginx fill:#FFB347,stroke:#333,stroke-width:2px;
  classDef upstream fill:#85C1E9,stroke:#333,stroke-width:2px;
  classDef backend fill:#ABEBC6,stroke:#333,stroke-width:2px;
  classDef db fill:#F9E79F,stroke:#333,stroke-width:2px;
  classDef cache fill:#F5B7B1,stroke:#333,stroke-width:2px;
  classDef mlflow fill:#D7BDE2,stroke:#333,stroke-width:2px;
  classDef monitoring fill:#FAD7A0,stroke:#333,stroke-width:2px;
  classDef prom fill:#D5F5E3,stroke:#333,stroke-width:2px;

  class U frontend
  class NG,Static nginx
  class UP1,UP2,UP3 upstream
  class B1,B2 backend
  class D1,D2,D3,D4,S db
  class E,L,M cache
  class G,H mlflow
  class W,Q,N1,N2 monitoring
  class J,K prom


```

- Visual diagram of the Docker Compose services
```mermaid
graph TD
  subgraph Users
    A[Browser]
  end

  subgraph Frontend
    B[Vite + React]
  end

  subgraph Backend
    C[FastAPI API]
    D[Model Training / Inference]
    E[Celery Worker]
    F[Prefect Flows]
  end

  subgraph Storage
    G[PostgreSQL as raw_db]
    H[ClickHouse as cleaned data]
    I[MinIO as Model Artifacts]
    J[MLflow as Tracking DB]
  end

  subgraph Monitoring
    K[Prometheus]
    L[Grafana]
    M[Evidently]
  end

  subgraph Messaging
    N[Kafka]
    O[Redis]
  end

  subgraph CI/CD
    P[GitHub Actions]
  end

  A --> B
  B --> C
  C --> D
  D --> E
  E --> G
  E --> H
  D --> J
  D --> I
  F --> G
  F --> H
  M --> K
  K --> L
  D --> N
  M --> N
  E --> O
  P -->|CI/CD| C

```

---

## 📈 Evaluation Checklist

### ✅ Problem Definition

* ✔️ Well-defined scope: stock prediction + model lifecycle

### ☁️ Infrastructure

* ✔️ Docker Compose setup with multiple services
* ✔️ IaC-friendly (MinIO, DB volumes, Prometheus)

### 🔬 Experiment Tracking

* ✔️ MLflow for logging experiments and model versioning
  - [here](backend/src/model_training/train.py)

### 📅 Workflow Orchestration

* ✔️ Prefect 2 for ETL and training flows
   - [here](./backend/workflows/etl_core.py)

### 🚀 Model Deployment

* ✔️ FastAPI for model inference (containerized API)

### 📊 Monitoring

* ✔️ Evidently + Prometheus + Grafana for data/model monitoring
    - [docker-compose.monitor.yml](./docker-compose.monitor.yml)
    - [docker-compose.kafka.yml](./docker-compose.kafka.yml)

* [Webhook to discord](./.github/workflows/cd-deploy.yml)

### 🔁 Reproducibility

* ✔️ Makefile + setup.md + requirements + Docker for consistent setup
    ```
    make dev-setup
    ```

### 🧪 Best Practices

* [x] Unit tests
    - [train unit test code](./backend/tests/test_train.py)
    - [predict unit test code](./backend/tests/test_predict.py)
* [x] Integration tests
    - [predict api test code](backend/integraton-test/test_predict_api.py)
    - [train api test code](backend/integraton-test/test_train_api.py)
* [x] Code formatting (black, flake8)
    - [refer to pre-commit-config.yaml](.pre-commit-config.yaml)
* [x] Makefile automation
    - [refer to Makefile](./Makefile)
* [x] Pre-commit hooks
    - [refer to pre-commit-config.yaml](.pre-commit-config.yaml)
* [x] GitHub Actions for CI
    - [refer to .github/workflows/ci-tests.yml](.github/workflows/ci-tests.yml)
    - [refer to .github/workflows/cd-deploy.yml](.github/workflows/cd-deploy.yml)

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
