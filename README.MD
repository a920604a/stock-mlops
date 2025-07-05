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
│   └── data/
│       ├── raw/
│       └── processed/

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
