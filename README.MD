```
stock-mlops-project/
├── frontend/                # React 前端應用程式
│   └── ...
├── backend/
│   ├── api/                     # FastAPI 應用程式
│   ├── app.py                   # 主 REST API 路由
│   ├── model_runner.py          # 載入模型並執行預測邏輯
│   ├── src/                     # 資料處理與模型邏輯
│   │   ├── data_loader.py
│   │   ├── features.py
│   │   ├── train.py
│   │   └── predict.py
│   └── data/                    # 原始與處理後資料
│       ├── raw/
│       └── processed/
├── workflows/               # Prefect workflow 任務定義
│   └── training_flow.py
├── monitor/                 # 模型監控（Evidently metrics exporter）
│   └── monitor.py
├── mlruns/                  # MLflow 模型與指標儲存（本地）
├── .github/
│   └── workflows/
│       └── ci.yml           # GitHub Actions CI 設定檔
├── docker-compose.yml       # 多服務整合配置
├── Dockerfile.backend       # FastAPI Dockerfile
├── Dockerfile.frontend      # React Dockerfile
├── Dockerfile.monitor      # Monitor 專用 Dockerfile
├── Dockerfile.workflow     # Workflow 專用 Dockerfile
├── Makefile
├── requirements.txt
├── .pre-commit-config.yaml
└── README.md

```