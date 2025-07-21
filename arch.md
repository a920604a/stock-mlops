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
├── arch.md                       # 架構說明文件
├── backend                       # 後端服務程式碼
│   ├── api                      # FastAPI API 層
│   │   ├── app.py               # API 啟動入口
│   │   ├── kafka_producer.py    # Kafka Producer 實作
│   │   ├── routes               # API 路由定義（REST endpoints）
│   │   └── schemas              # 輸入輸出資料模型定義（Pydantic schemas）
│   ├── celery_worker.py         # Celery 非同步任務 Worker
│   ├── integraton-test          # 後端整合測試腳本與測試碼
│   ├── monitor                 # 後端監控相關程式碼
│   ├── pyproject.toml          # Python 專案設定
│   ├── requirements.txt        # Python 套件依賴清單
│   ├── setup.md                # 後端開發或部署說明
│   ├── src                     # 核心業務邏輯與模組
│   │   ├── data_management     # 資料讀取與管理（Dataset 定義）
│   │   ├── db                 # 資料庫連線與 ORM 相關
│   │   ├── feature_engineering # 特徵工程相關程式碼
│   │   ├── inference          # 模型推論功能
│   │   ├── model_management   # 模型狀態管理
│   │   ├── model_training     # 模型訓練核心程式
│   │   ├── production_monitor # 生產環境監控邏輯
│   │   ├── tasks              # 非同步任務定義（celery task）
│   │   └── workflows          # ETL 與自動化流程 (Prefect 或自訂 workflow)
│   ├── tests                  # 單元及整合測試程式碼
├── Criteria.MD                  # 專案需求與驗收標準文件
├── data                        # 原始資料或輸入資料目錄
├── db                          # 資料庫初始化腳本與持久化卷
├── dev.md                      # 開發流程與環境說明
├── docker-compose.monitor.yml  # 監控相關服務 Docker Compose 配置
├── docker-compose.yml          # 專案主要服務 Docker Compose 配置
├── Dockerfile.backend          # 後端服務 Docker 映像建構腳本
├── Dockerfile.mlflow           # MLflow 服務 Docker 映像建構腳本
├── docs.md                     # 專案相關文件說明
├── frontend                    # React 前端程式碼
│   ├── public                  # 靜態資源
│   ├── src                     # 前端程式碼
│   │   ├── api                 # 與後端 API 交互封裝
│   │   ├── components          # UI 元件
│   │   ├── pages               # 各頁面元件
│   │   ├── App.jsx             # React 主組件入口
│   │   └── index.html          # 頁面模板
│   ├── package.json            # npm 套件依賴
│   └── README.md               # 前端相關說明
├── Makefile                    # 常用開發任務自動化腳本
├── monitor                     # 監控系統配置與定義（Prometheus、Grafana）
│   ├── blackbox                # Blackbox Exporter 監控設定
│   ├── dashboards             # Grafana 儀表板 JSON 定義
│   ├── prometheus             # Prometheus 配置檔
│   └── provisioning           # Grafana 儀表板及資料源設定
├── nginx                       # Nginx 反向代理與靜態資源配置
├── package-lock.json           # npm 鎖定檔
├── readme.md                   # 專案說明文件
├── readme_zh.md                # 中文說明文件
├── scripts                     # 自動化腳本（資料匯入、初始化、發佈等）
├── ws_monitor                  # WebSocket 監控服務
│   ├── db.py                   # 與 ClickHouse 互動的 DB 工具函式 (插入預測資料)
│   ├── ws_app.py               # FastAPI WebSocket 服務主程式
│   ├── Dockerfile              # WebSocket 監控服務 Dockerfile
│   └── requirements.txt        # WebSocket 服務依賴
└── 實作歷程.md                  # 專案實作歷程與心得紀錄

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
