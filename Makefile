# Makefile

# DOCKER_COMPOSE = docker-compose
DOCKER_COMPOSE = docker compose
BACKEND_SERVICE = backend
LOCAL_TAG:=$(shell date +"%Y-%m-%d-%H-%M")
LOCAL_IMAGE_NAME:=stock-mlops-backend:${LOCAL_TAG}


.PHONY: up down logs clean ingest test build init integration_test quality_checks

clean:
	$(DOCKER_COMPOSE) down --volumes
	rm -rf db/mlflow_db db/oltp db/model_meta_db db/olap
	rm -rf data/mlflow_artifacts data/prometheus_data
	rm -rf data/minio

init:
	mkdir -p db/mlflow_db db/oltp db/model_meta_db db/olap
	mkdir -p data/mlflow_artifacts data/prometheus_data data/minio

# 啟動所有服務
up:
	$(DOCKER_COMPOSE) up --build -d
	@echo "✅ 所有服務已啟動"
# clickhouse create table (so far, use script)
# 進入 MinIO web 控制台（http://localhost:9001）登入後： 建立一個 bucket 名為：mlflow-artifacts

ingest:
	bash scripts/ingest.sh

# 關閉所有服務
down:
	$(DOCKER_COMPOSE) down

# 查看服務 log（包含 backend）
logs:
	$(DOCKER_COMPOSE) logs -f backend


test:
	$(DOCKER_COMPOSE) exec $(BACKEND_SERVICE) pytest -v


build: init up ingest


train:
	$(DOCKER_COMPOSE) exec $(BACKEND_SERVICE) python src/train.py
predict:
	$(DOCKER_COMPOSE) exec $(BACKEND_SERVICE) python src/predict.py

quality_checks:
	isort .
	black .
	pylint backend/src

publish: build integration_test
integration_test: 
	LOCAL_IMAGE_NAME=${LOCAL_IMAGE_NAME} bash backend/integraton-test/run.sh

# publish: integration_test
# 	LOCAL_IMAGE_NAME=${LOCAL_IMAGE_NAME} bash scripts/publish.sh

# setup:
# 	pipenv install --dev
# 	pre-commit install