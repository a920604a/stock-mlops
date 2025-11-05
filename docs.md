
## 📦 專案模組職責說明

| 模組名稱                      | 目錄位置                      | 職責說明                                                    |
| ------------------------- | ------------------------- | ------------------------------------------------------- |
| **frontend**              | `./frontend`              | React 前端，負責股票查詢、歷史資料視覺化、模型預測結果展示、操作介面。                  |
| **backend/api**           | `./backend/api`           | FastAPI API 層，處理前端請求、路由分發、資料 CRUD、推論 API 等。             |
| **backend/src**           | `./backend/src`           | 核心商業邏輯：特徵工程、模型訓練、推論邏輯、資料管理。                             |
| **backend/src/workflows** | `./backend/src/workflows` | 使用 Prefect 定義的批次 ETL 與訓練流程，統一納入 backend，便於 CI/CD 與版本控管。 |
| **monitor**               | `./monitor`               | Prometheus 與 Grafana 監控設定檔與儀表板資源，管理模型與系統監控指標的展示。         |
| **mlruns**                | `./mlruns`                | MLflow 本地模型實驗與模型版本管理資料存放目錄。                             |
| **db**                    | `./db` (PostgreSQL 資料卷)   | PostgreSQL OLTP 與模型元資料存放。                               |
| **redis**                 | Redis 容器                  | 快取層與訊息中繼，減少 DB 負載，提高系統響應速度。                             |
| **prometheus**            | Prometheus 容器             | 收集與儲存監控指標資料。                                            |
| **grafana**               | Grafana 容器                | 指標資料視覺化展示，呈現模型表現、資料漂移及系統狀態。                             |
| **kafka**                 | Kafka 容器                  | 事件訊息串流平台，用於即時資料與監控訊息傳遞。                                 |
| **metrics_publisher**      | `./metrics_publisher`      | 定期從 backend 暴露的 `/metrics` 端點抓取 Prometheus 指標，並透過 Kafka 發送至即時監控管道。 |
| **ws_monitor**            | `./ws_monitor`             | WebSocket 即時監控服務，整合 Kafka 消息並提供前端推，包含異常監控                    |
| **celery**                | Celery 任務佇列               | 背景非同步任務處理，如訓練、 長時間的預測等長時間任務。                               |
| **flow**                |        一個基於 Web 的 Celery 監控工具      |     一個基於 Web 的 Celery 監控工具                           |
| **minio**                 | MinIO 容器                  | 物件存儲服務，作為 MLflow artifact repository。                   |
| **redis**                |            |     給 Celery 當作「Broker」                           |

---

## services

| 分類         | 包含服務                                                                                                             | 建議檔案名稱                        |
| ---------- | ---------------------------------------------------------------------------------------------------------------- | ----------------------------- |
| **監控**     | prometheus、grafana、node-exporter、cadvisor、blackbox-exporter、celery\_exporter | `docker-compose.monitor.yml`  |
| **前端**     | nginx                                                                                                            | `docker-compose.frontend.yml` |
| **後端**     | mlflow、backend1、backend2                                                                                         | `docker-compose.backend.yml`  |
| **資料庫**    | redis、raw\_db、model\_meta\_db、mlflow-db、clickhouse、minio、init-minio                                              | `docker-compose.database.yml` |
| **Kafka**  | kafka、kafka-ui、metrics\_publisher、ws\_monitor                                                                    | `docker-compose.kafka.yml`    |
| **Celery** | celery\_train、celery\_predict、flower                                                                             | `docker-compose.celery.yml`   |

---

## API Design

## API 介面清單

### 1. 預測 (Predict)

| 方法   | 路徑                                             | 描述           | 備註                                |
| ---- | ---------------------------------------------- | ------------ | --------------------------------- |
| GET  | `/api/predict/`                                | 查詢歷史預測紀錄     |                                   |
| POST | `/api/predict/`                                | 單筆即時預測       | backend2 as kafka producer -> kafka broker -> ws_monitor as kafka consumer 。由 backend2 作為 Kafka Producer 發送訊息 |
| POST | `/api/predict/future/`                         | 多天未來預測       | backend2 celery task -> redis Broker -> celery_predict worker -> backend2。透過 Celery 任務非同步執行                 |
| GET  | `/api/predict/future/status/{task_id}`         | 查詢未來預測任務狀態   |                                   |
| GET  | `/api/predict/future/partial_status/{task_id}` | 查詢未來預測任務部分狀態 |                                   |

---

### 2. 模型管理 (Model)

| 方法     | 路徑                       | 描述                | 備註 |
| ------ | ------------------------ | ----------------- | -- |
| GET    | `/api/models/`           | 列出所有模型            |    |
| POST   | `/api/models/`           | 新增模型              |    |
| GET    | `/api/models/{model_id}` | 取得指定模型詳細          |    |
| DELETE | `/api/models/{model_id}` | 刪除指定模型            |    |
| GET    | `/api/mlflow/models`     | MLflow 模型列表 (將棄用) |    |
| GET    | `/api/mlflow/{model_id}` | MLflow 模型詳細       |    |

---

### 3. 訓練任務 (Train)

| 方法   | 路徑                            | 描述       | 備註                            |
| ---- | ----------------------------- | -------- | ----------------------------- |
| POST | `/api/train`                  | 提交模型訓練任務 | backend1 celery task -> redis Broker -> celery_train worker -> backend1    。 透過 backend1 將任務放入 Celery 任務佇列 |
| GET  | `/api/train/status/{task_id}` | 查詢訓練任務狀態 |                               |

---

### 4. 監控指標 (Metrics)

| 方法  | 路徑         | 描述          | 備註                                                                 |
| --- | ---------- | ----------- | ------------------------------------------------------------------ |
| GET | `/metrics` | 取得系統與模型監控指標 | 由 backend1 提供；metrics\_publisher 會拉取並透過 Kafka 發送給 ws\_monitor 推播前端。 |

- backend1 -> prometheus
- metrics_publisher as kafka producer -> kafka broker -> ws_monitor as kafka consumer
datasets
---

### 5. 資料集 (Datasets)

| 方法  | 路徑              | 描述      | 備註 |
| --- | --------------- | ------- | -- |
| GET | `/api/datasets` | 取得資料集列表 |    |

---


## 🔁 工作流程與資料流說明

```mermaid
graph TD
  %% 使用者操作
  subgraph 使用者操作
    A[Frontend<br>React]
    A -->|觸發訓練任務| B[Backend API<br>FastAPI]
    A -->|請求預測任務| B
    A -->|HTTP Polling 狀態| B
  end

  %% 資料與 ETL 流程
  subgraph 資料與 ETL
    P[Prefect Workflow<br>backend/src/workflows] -->|ETL 處理| D1[(raw_db<br>PostgreSQL<br>原始資料)]
    P -->|清洗後資料| D2[(OLAP<br>ClickHouse<br>ETL 清洗 & 預測結果)]
  end

  %% 訓練與推論系統
  subgraph 訓練與推論
    B -->|查詢 cleaned data| D2
    B -->|快取查詢| E[Redis]

    %% 模型訓練
    B -->|提交訓練任務| L[Celery Worker]
    L -->|讀取 cleaned data| D2
    L -->|執行訓練| G[模型訓練邏輯]
    G -->|模型版本管理| H[MLflow Registry]
    G -->|更新 model_meta| D3[(mlflow-db<br>PostgreSQL<br>模型元資料)]
    H -->|模型 Artifact| S[(MinIO<br>模型儲存)]

    %% 模型預測
    B -->|推送預測請求| N1[Kafka - prediction topic]
  end

  %% MLflow 內部資料庫
  subgraph MLflow內部
    H --> D4[(mlflow內建DB<br>PostgreSQL)]
  end

  %% 監控與即時推播
  subgraph 監控與推播
    I[backend /metrics] --> Q[metrics_publisher<br>每5秒抓取並發送 Kafka]
    Q --> N2[Kafka - metrics topic]
    W[ws_monitor<br>Kafka Consumer + WebSocket]
    N1 -->|預測結果| W
    N2 -->|Metrics| W
    W -->|WebSocket 推播| A
    I -->|Metrics 拉取| J[Prometheus]
    J -->|提供歷史數據| K[Grafana 儀表板]
  end

  %% 非同步任務佇列
  subgraph 非同步任務
    L[Celery Worker] <---> M[Redis Broker]
  end

```
---
