# Makefile

# DOCKER_COMPOSE = docker-compose
DOCKER_COMPOSE = docker compose


.PHONY: up up-core down logs restart-core

# 啟動所有服務
up:
	$(DOCKER_COMPOSE) up --build -d

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
