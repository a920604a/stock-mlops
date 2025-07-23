# ========== 參數與變數 ==========
DOCKER_COMPOSE = docker compose
DOCKER_COMPOSE_MONITOR = docker compose -f docker-compose.monitor.yml

TRAIN_BACKEND := backend1
PREDICT_BACKEND := backend2

DB_DIRS := db/mlflow_db db/oltp db/model_meta_db db/olap
DATA_DIRS := data/mlflow_artifacts data/prometheus_data data/minio

LOCAL_TAG := $(shell date +"%Y-%m-%d-%H-%M")
LOCAL_IMAGE_NAME := stock-mlops-backend:${LOCAL_TAG}

MAKEFLAGS += --no-builtin-rules

.PHONY: help up down logs clean ingest test build init integration_test quality_checks monitor reset  \
        setup retrain pipeline ci restart publish frontend-dev frontend-build \
        monitor-up monitor-down monitor-logs

# ========== 指令說明 ==========
help:
	@echo "📦 可用指令如下："
	@grep -E '^[a-zA-Z\-_]+:.*?##' Makefile | awk 'BEGIN {FS = ":.*?##"} {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ========== 初始化與清除 ==========

init: ## 初始化資料夾
	mkdir -p $(DB_DIRS)
	mkdir -p $(DATA_DIRS)

clean: ## 清除容器與資料夾
	sudo $(DOCKER_COMPOSE) down --volumes
	sudo rm -rf $(DB_DIRS) $(DATA_DIRS)
	rm -rf $(FRONTEND_DIR)/package-lock.json $(FRONTEND_DIR)/node_modules

reset: ## 清除並重新啟動所有服務
	sudo $(MAKE) clean
	$(MAKE) init
	$(DOCKER_COMPOSE) up -d --force-recreate
	@echo "🧹 清除完成並重新建置所有 image 與啟動容器"

restart: ## 快速重啟 backend 容器（不重建 image）
	$(DOCKER_COMPOSE) restart $(TRAIN_BACKEND) $(PREDICT_BACKEND)

# ========== 容器操作 ==========

up: ## 啟動所有服務（build）
	$(DOCKER_COMPOSE) up --build -d
	@echo "✅ 所有服務已啟動"

down: ## 關閉所有服務
	$(DOCKER_COMPOSE) down

logs: ## 查看 backend 服務日誌
	$(DOCKER_COMPOSE) logs -f backend

# ========== 專案功能 ==========

frontend-dev: ## 啟動前端開發模式
	cd $(FRONTEND_DIR) && npm install && npm run dev

frontend-build: ## 前端正式版編譯
	cd $(FRONTEND_DIR) && npm install && npm run build

ingest: ## 執行資料收集腳本
	bash scripts/ingest.sh

train: ## 執行模型訓練
	@echo "🚀 執行模型訓練..."
	$(DOCKER_COMPOSE) exec $(TRAIN_BACKEND) python src/model_training/train.py || (echo "❌ 訓練失敗"; exit 1)

predict: ## 執行模型推論
	$(DOCKER_COMPOSE) exec $(PREDICT_BACKEND) python src/inference/predict.py

monitor: ## 啟動監控模組
	$(DOCKER_COMPOSE) exec $(TRAIN_BACKEND) python -m monitor.monitor

# ========== 測試與品質檢查 ==========

test: ## 執行單元測試
	$(DOCKER_COMPOSE) exec $(TRAIN_BACKEND) pytest -v

quality_checks: ## 程式碼風格檢查（isort / black / pylint）
	isort .
	black .
	pylint backend/src || true

integration_test: ## 執行整合測試
	LOCAL_IMAGE_NAME=$(LOCAL_IMAGE_NAME) bash backend/integraton-test/run.sh

# ========== 組合流程 ==========

setup: clean init up ingest ## 一鍵啟動專案

build: init up ## 建置與啟動

all: init up ingest ## 同 setup，但命名與傳統相符

up-all: ## 啟動所有服務 + 監控模組
	$(DOCKER_COMPOSE) up -d
	$(DOCKER_COMPOSE_MONITOR) up -d
	@echo "🚀 主系統與監控模組已全部啟動"

pipeline: quality_checks test train predict ## 模型完整開發流程

retrain: train predict ## 訓練與預測

ci: quality_checks test integration_test ## CI/CD 使用的檢查與測試流程

publish: quality_checks build ## 品質檢查與建置後發布
	LOCAL_IMAGE_NAME=$(LOCAL_IMAGE_NAME) bash scripts/publish.sh


monitor-up: ## 啟動監控模組（Prometheus, Grafana 等）
	$(DOCKER_COMPOSE_MONITOR) up -d
	@echo "📈 監控模組已啟動"

monitor-down: ## 關閉監控模組
	$(DOCKER_COMPOSE_MONITOR) down

monitor-logs: ## 查看監控模組日誌
	$(DOCKER_COMPOSE_MONITOR) logs -f

dev-setup: monitor-down reset ingest monitor-up
