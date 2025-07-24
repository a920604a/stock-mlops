# ========================
# Global Config & Variables
# ========================

DOCKER_COMPOSE            = docker compose
COMPOSE_DB                = docker compose -f docker-compose.database.yml
COMPOSE_KAFKA             = docker compose -f docker-compose.kafka.yml
COMPOSE_BACKEND           = docker compose -f docker-compose.backend.yml
COMPOSE_FRONTEND          = docker compose -f docker-compose.frontend.yml
COMPOSE_MONITOR           = docker compose -f docker-compose.monitor.yml

NETWORK_NAME              = monitor-net

TRAIN_BACKEND             = backend1
PREDICT_BACKEND           = backend2
BACKENDS                  = $(TRAIN_BACKEND) $(PREDICT_BACKEND)

FRONTEND_DIR              = frontend
DB_DIRS                   = db/mlflow_db db/oltp db/model_meta_db db/olap
DATA_DIRS                 = data/mlflow_artifacts data/prometheus_data data/minio

LOCAL_TAG                 = $(shell date +"%Y-%m-%d-%H-%M")
LOCAL_IMAGE_NAME          = stock-mlops-backend:${LOCAL_TAG}

MAKEFLAGS += --no-builtin-rules

.PHONY: help init init-soft net-create clean reset restart \
        up-core up-db up-kafka up-backend up-frontend up-monitor \
        down-all down-core down-db down-kafka down-backend down-frontend down-monitor \
        logs-backend logs-monitor logs-db logs-kafka logs-frontend \
        setup build all up-all ingest test train predict monitor \
        integration_test quality_checks pipeline retrain ci publish \
        frontend-dev frontend-build \
        monitor-up monitor-down monitor-logs dev-setup

# ========================
# Help
# ========================
help:
	@echo "📦 可用指令如下："
	@grep -E '^[a-zA-Z0-9_\-]+:.*?##' Makefile | awk 'BEGIN {FS = ":.*?##"} {printf "  \033[36m%-22s\033[0m %s\n", $$1, $$2}'

# ========================
# Init / Clean
# ========================

net-create: ## 建立共用 Docker network（若不存在）
	@echo "🔌 檢查/建立 network $(NETWORK_NAME)"
	@if ! docker network inspect $(NETWORK_NAME) >/dev/null 2>&1; then \
		docker network create $(NETWORK_NAME) --driver bridge; \
		echo "✅ 建立 $(NETWORK_NAME) 完成"; \
	else \
		echo "✅ $(NETWORK_NAME) 已存在"; \
	fi

init: ## 初始化資料夾（含 network）
	$(MAKE) net-create
	mkdir -p $(DB_DIRS)
	mkdir -p $(DATA_DIRS)

init-soft: ## 僅建立 network（不建立資料夾）
	$(MAKE) net-create

clean: ## 清除所有容器與資料夾（小心會刪資料）
	$(MAKE) down-all
	sudo rm -rf $(DB_DIRS) $(DATA_DIRS)
	rm -rf $(FRONTEND_DIR)/package-lock.json $(FRONTEND_DIR)/node_modules

reset: ## 清除並重新啟動核心（DB + Kafka + Backend）
	@echo "🧹 reset 核心服務 (DB/Kafka/Backend)"
	$(MAKE) down-core
	$(MAKE) init
	$(MAKE) up-core
	@echo "✅ reset 完成"

restart: ## 快速重啟 backend 容器（不重建 image）
	$(COMPOSE_BACKEND) restart $(BACKENDS)

# ========================
# Up / Down (分組控制)
# ========================

# --- UP ---

up-db: ## 啟動資料庫 (Redis/Postgres/ClickHouse/MinIO/MLflow-DB ...)
	$(COMPOSE_DB) up -d

up-kafka: ## 啟動 Kafka
	$(COMPOSE_KAFKA) up -d

up-backend: ## 啟動後端與 Celery（需 DB & Kafka 已起來）
	$(COMPOSE_BACKEND) up -d

up-frontend: ## 啟動前端與 UI
	$(COMPOSE_FRONTEND) up -d

up-monitor: ## 啟動監控模組（Prometheus, Grafana, exporters...）
	$(COMPOSE_MONITOR) up -d

# up-core: up-db up-kafka up-backend ## 依序啟動核心服務（DB → Kafka → Backend）
up-core:
	docker compose -f docker-compose.database.yml \
	               -f docker-compose.celery.yml \
				   -f docker-compose.kafka.yml \
	               -f docker-compose.backend.yml \
	               up -d

up-all: ## 依序啟動所有服務(核心 + 前端 + 監控)
	$(MAKE) up-core
	$(MAKE) up-frontend
	$(MAKE) up-monitor
	@echo "🚀 所有服務已啟動"

# --- DOWN ---

down-db:
	$(COMPOSE_DB) down

down-kafka:
	$(COMPOSE_KAFKA) down

down-backend:
	$(COMPOSE_BACKEND) down

down-frontend:
	$(COMPOSE_FRONTEND) down

down-monitor:
	$(COMPOSE_MONITOR) down

down-core:
	docker compose -f docker-compose.database.yml \
	               -f docker-compose.celery.yml \
	               -f docker-compose.kafka.yml \
	               -f docker-compose.backend.yml \
	               down


down-all: ## 關閉所有服務（Monitor → Frontend → Backend → Kafka → DB）
	$(MAKE) down-monitor || true
	$(MAKE) down-frontend || true
	$(MAKE) down-backend || true
	$(MAKE) down-kafka || true
	$(MAKE) down-db || true
	@echo "🛑 所有服務已關閉"

# ========================
# Logs
# ========================

logs-backend: ## 追 backend1 & backend2 日誌
	$(COMPOSE_BACKEND) logs -f $(BACKENDS)

logs-monitor: ## 追監控模組日誌
	$(COMPOSE_MONITOR) logs -f

logs-db:
	$(COMPOSE_DB) logs -f

logs-kafka:
	$(COMPOSE_KAFKA) logs -f

logs-frontend:
	$(COMPOSE_FRONTEND) logs -f

# 與你原本兼容的別名
monitor-up: up-monitor ## 啟動監控模組（Prometheus, Grafana 等）
	@echo "📈 監控模組已啟動"

monitor-down: down-monitor ## 關閉監控模組

monitor-logs: logs-monitor ## 查看監控模組日誌

# ========================
# Project Ops
# ========================

frontend-dev: ## 啟動前端開發模式
	cd $(FRONTEND_DIR) && npm install && npm run dev

frontend-build: ## 前端正式版編譯
	cd $(FRONTEND_DIR) && npm install && npm run build

ingest: ## 執行資料收集腳本
	bash scripts/ingest.sh

train: ## 執行模型訓練
	@echo "🚀 執行模型訓練..."
	$(COMPOSE_BACKEND) exec $(TRAIN_BACKEND) python src/model_training/train.py || (echo "❌ 訓練失敗"; exit 1)

predict: ## 執行模型推論
	$(COMPOSE_BACKEND) exec $(PREDICT_BACKEND) python src/inference/predict.py

monitor: ## 模擬監控
	$(COMPOSE_BACKEND) exec $(PREDICT_BACKEND) python src/inference/simulate_predict_days.py --start-date 2025-06-01 --days 15 --ticker AAPL --exchange US --base-url http://localhost:8000
	@echo "📊 模擬監控已完成"

# ========================
# Tests & Quality
# ========================

test: ## 單元測試
	$(COMPOSE_BACKEND) exec $(TRAIN_BACKEND) pytest -v

quality_checks: ## 程式碼風格檢查（isort / black / pylint）
	isort .
	black .
	pylint backend/src || true

integration_test: ## 整合測試
	$(COMPOSE_BACKEND) exec $(PREDICT_BACKEND) pytest integraton-test/test_predict_api.py

pipeline: quality_checks test train predict ## 模型完整開發流程

retrain: train predict ## 訓練與預測

ci: quality_checks test integration_test ## CI/CD 檢查與測試流程

publish: quality_checks build ## 品質檢查與建置後發布
	LOCAL_IMAGE_NAME=$(LOCAL_IMAGE_NAME) bash scripts/publish.sh

# ========================
# High-level Flows
# ========================

setup: clean init up-all ingest ## 一鍵啟動整套（含監控）

build: init up-core ## 核心建置與啟動

all: init up-core ingest ## 與傳統 all 同義

dev-setup: ## 本地開發快速重來（停監控 → reset 核心 → ingest → 啟監控）
	$(MAKE) monitor-down
	$(MAKE) reset
	$(MAKE) ingest
	$(MAKE) up-frontend
	$(MAKE) monitor-up


# make up-core
# make up-frontend
# make up-monitor
