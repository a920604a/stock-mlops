# Makefile

# DOCKER_COMPOSE = docker-compose
DOCKER_COMPOSE = docker compose 
BACKEND_SERVICE = backend


.PHONY: up up-core down logs restart-core clean ingest test

clean:
	$(DOCKER_COMPOSE) down --volumes
	rm -rf db/mlflow_db db/pgdata
	rm -rf data/mlflow_artifacts data/prometheus_data
	
init:
	mkdir data/prometheus_data	

# 啟動所有服務
up:
	$(DOCKER_COMPOSE) up --build -d
# clickhouse create table
# 進入 MinIO web 控制台（http://localhost:9001）登入後： 建立一個 bucket 名為：mlflow-artifacts

ingest:
	bash scripts/ingest.sh


# ✅ 僅啟動核心服務：db + mlflow + backend
up-core:
	$(DOCKER_COMPOSE) up --build -d db mlflow backend

# 關閉所有服務
down:
	$(DOCKER_COMPOSE) down

# 查看服務 log（包含 backend）
logs:
	$(DOCKER_COMPOSE) logs -f backend

# 重新啟動 backend + 依賴
restart-core:
	$(DOCKER_COMPOSE) restart db mlflow backend




test:
	$(DOCKER_COMPOSE) exec $(BACKEND_SERVICE) pytest -v tests/test_predict.py