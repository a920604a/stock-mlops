```
stock-mlops-project/
├── frontend/                         # React 前端應用程式
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── App.tsx
│   └── package.json

├── backend/                          # 後端服務
│   ├── api/                          # FastAPI API 層
│   │   ├── main.py
│   │   ├── routes/
│   │   │   ├── predict.py
│   │   │   └── health.py
│   │   ├── schemas/
│   │   │   └── predict_request.py
│   │   └── utils/
│   │       └── cache.py
│   ├── app.py                        # API 主執行點（可選）
│   ├── src/                          # 核心邏輯與 workflow
│   │   ├── data_loader.py           # 從資料庫讀取股價資料
│   │   ├── train.py                 # 模型訓練並註冊至 MLflow
│   │   ├── predict.py               # 模型載入與推論
│   │   ├── database_oalp.py               # Session設定
│   │   ├── models.py                # 已完成：定義 ORM 模型 StockData
│   │   └── workflows/
│   │       └── etl_script.py
│   └── tests/

├── monitor/                          # 模型與資料監控
│   ├── monitor.py
│   ├── prometheus.yml
│   └── grafana/

├── mlruns/                           # MLflow 實驗與模型儲存目錄

├── db/                               # PostgreSQL Volume 與初始化
│   ├── pgdata/
│   └── init.sql                      # 初始建表 SQL（可選）

├── .github/
│   └── workflows/
│       └── ci.yml                    # GitHub Actions 設定

├── Dockerfile.backend                # backend FastAPI 映像檔建構
├── Dockerfile.frontend              # frontend React 映像檔建構
├── Dockerfile.monitor               # monitor 模組建構（如有需要）
├── docker-compose.yml               # 所有服務的協作與啟動設定

├── .env                              # 本地用環境變數檔（不提交）
├── .env.example                      # 提供參考的範例環境變數檔
├── .pre-commit-config.yaml           # 格式檢查與 Lint 工具
├── Makefile                          # CLI 工具集合
├── README.md                         # 專案說明文件
└── .gitignore
```
```
.
.
├── backend                  # 後端服務程式碼
│   ├── api
│   │   └── app.py           # FastAPI 或 Flask 主程式入口（API 服務啟動點）
│   ├── integraton-test      # 後端整合測試相關
│   │   ├── run.sh           # 測試啟動腳本
│   │   └── test_docker.py   # Docker 環境下的測試程式
│   ├── monitor              # 後端監控相關程式
│   │   ├── create_monitor_tb.py # 建立監控用資料表的腳本
│   │   ├── __init__.py
│   │   ├── monitor.py       # 監控核心邏輯
│   │   ├── __pycache__      # Python快取檔
│   │   │   └── monitor.cpython-311.pyc
│   │   └── save_result.py   # 儲存監控結果的程式
│   ├── pyproject.toml       # Python 專案設定（依賴管理等）
│   ├── requirements.txt     # Python 套件依賴清單
│   ├── setup.md             # 後端開發或部署設定說明文件
│   ├── src                  # 後端核心程式碼（模組化邏輯）
│   │   ├── create_clickhouse_table.py # 建立 ClickHouse 資料表腳本
│   │   ├── database_olap.py # OLAP 資料庫存取邏輯（分析型資料庫）
│   │   ├── database_oltp.py # OLTP 資料庫存取邏輯（交易型資料庫）
│   │   ├── data_loader.py   # 資料載入與前處理
│   │   ├── __init__.py
│   │   ├── model_available.py # 模型狀態或清單管理
│   │   ├── model_save.py    # 模型儲存邏輯
│   │   ├── models.py        # ORM或資料結構定義
│   │   ├── predict.py       # 模型預測功能
│   │   ├── __pycache__      # Python快取檔
│   │   ├── schema.py        # 輸入輸出資料結構定義（Pydantic等）
│   │   ├── train_config.py  # 訓練參數設定
│   │   └── train.py         # 模型訓練程式
│   ├── tests                # 單元測試程式碼
│   │   ├── __pycache__
│   │   ├── test_data_loader.py # 測試資料載入功能
│   │   ├── test_predict.py      # 測試預測功能
│   │   └── test_train.py        # 測試訓練流程
│   ├── uv.lock              # 可能是 uv 的鎖定檔（鎖定版本）
│   └── workflows            # ETL與資料處理工作流程式
│       ├── etl_core.py      # 核心 ETL 流程邏輯
│       ├── etl_script.py    # ETL 執行腳本
│       ├── parquet          # 用於 ETL 的 parquet 格式資料
│       │   ├── 2330.TW_processed.parquet
│       │   ├── AAPL_processed.parquet
│       │   └── TSM_processed.parquet
│       ├── __pycache__
│       ├── README.MD        # ETL 工作流程說明
│       └── requirements.txt # ETL 工作流程相關依賴清單
├── Criteria.MD              # 專案準則說明文件（需求、驗收標準等）
├── data                     # 原始或輸入資料目錄
├── db                       # 資料庫相關
│   └── init-scripts
│       └── model_metadata.sql # 資料庫初始化腳本（模型相關 metadata 建表）
├── docker-compose.yml       # Docker Compose 定義（整合多容器服務）
├── Dockerfile.backend       # 後端服務 Docker 映像建置腳本
├── Dockerfile.mlflow        # MLflow 服務 Docker 映像建置腳本
├── docs.md                  # 專案文件說明
├── frontend                 # 前端專案程式碼（React/Vue等）
├── Makefile                 # 自動化指令（build、test、deploy等）
├── monitor                  # 監控相關設定與檔案
│   ├── dashboards           # 監控儀表板 JSON 配置檔
│   │   └── AAPL prediction_drift.json
│   ├── docs.md              # 監控系統說明文件
│   ├── prometheus           # Prometheus 監控設定
│   │   └── prometheus.yml   # Prometheus 配置檔
│   └── provisioning         # Grafana 監控儀表板與資料源設定
│       ├── dashboards
│       │   └── dashboards.yaml
│       └── datasources
│           └── clickhouse.yaml
├── nginx                    # Nginx 反向代理與靜態資源設定
│   └── nginx.conf
├── pgdata [error opening dir] # PostgreSQL 資料目錄（可能被鎖定或無法存取）
├── README.MD                # 專案整體說明文件（包含架構、安裝與使用）
├── scripts                  # 自動化腳本（資料匯入、初始化、發佈等）
│   ├── ingest.sh            # 資料匯入腳本
│   ├── init_minio.sh        # MinIO 初始化腳本
│   └── publish.sh           # 發佈或部署腳本
└── 實作歷程.md              # 專案實作過程記錄與心得


```


1. Problem Clarification
2. Data Collection
3. Feature Engineering
4. Model Design
5. Model Evalution
6. Deployment & Monitoring

Model Design
Evaluation metrics
- Classificatopn: Precision, Recall, Area Under the ROC cure, F1 score
- Regression: MSE, MAE, R-squared/Adjusted R-squared

Molde training
- Loss function: Cross Entropy , MSE, MAE, Huge loss
- Regularzation: L1, L2, k-fold CV, dropout
- Backpropagation: SGD, AdaGrad, Momentum
- Vanishing gradient
- Activation function: Linear, ReLU, Tanh, Sigmoid, ELU
- Overfitting, Underfitting

Deployment & Monitoring
Monitoring
- model bias, offline vs. online feature inconsistances etc
- model score, model online metrics
