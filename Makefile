# Makefile

# DOCKER_COMPOSE = docker-compose
DOCKER_COMPOSE = docker compose
# BACKEND_SERVICE = backend

TRAIN_BACKEND := backend1
PREDICT_BACKEND := backend2


LOCAL_TAG:=$(shell date +"%Y-%m-%d-%H-%M")
LOCAL_IMAGE_NAME:=stock-mlops-backend:${LOCAL_TAG}


.PHONY: up down logs clean ingest test build init integration_test quality_checks monitor reset


reset:
	sudo $(MAKE) clean
	$(MAKE) init
	$(DOCKER_COMPOSE) up -d --force-recreate
	@echo " 清除完成並重新建置所有 image 與啟動容器"


clean:
	sudo $(DOCKER_COMPOSE) down --volumes
	sudo rm -rf db/mlflow_db db/oltp db/model_meta_db db/olap
	sudo rm -rf data/mlflow_artifacts data/prometheus_data
	sudo rm -rf data/minio

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
	$(DOCKER_COMPOSE) exec $(TRAIN_BACKEND) pytest -v


all: init up ingest
build: init up

train:
	$(DOCKER_COMPOSE) exec $(TRAIN_BACKEND) python src/train.py

monitor:
	$(DOCKER_COMPOSE) exec $(TRAIN_BACKEND) python -m monitor.monitor

predict:
	$(DOCKER_COMPOSE) exec $(PREDICT_BACKEND) python src/predict.py

quality_checks:
	isort .
	black .
	pylint backend/src || true


integration_test:
	LOCAL_IMAGE_NAME=${LOCAL_IMAGE_NAME} bash backend/integraton-test/run.sh

publish: quality_checks build
	LOCAL_IMAGE_NAME=${LOCAL_IMAGE_NAME} bash scripts/publish.sh

# setup:
# 	pipenv install --dev
# 	pre-commit install
