#!/usr/bin/env bash
set -e

echo "⏳ 等待所有核心服務啟動..."

wait_for_http_service() {
  local name="$1"
  local url="$2"
  for i in {1..10}; do
    if curl -s -L --fail "$url" > /dev/null; then
      echo "✅ $name is up: $url"
      return 0
    fi
    echo "⏳ Waiting for $name... ($i/10)"
    sleep 3
  done
  echo "❌ $name did not become ready: $url"
  exit 1
}

wait_for_redis() {
  for i in {1..10}; do
    if docker compose -f docker-compose.database.yml exec -T redis redis-cli ping | grep -q PONG; then
      echo "✅ Redis is up"
      return 0
    fi
    echo "⏳ Waiting for Redis... ($i/10)"
    sleep 2
  done
  echo "❌ Redis did not become ready"
  exit 1
}


wait_for_postgres() {
  local name="$1"
  local service="$2"
  for i in {1..10}; do
    if docker compose -f docker-compose.database.yml exec -T  "$service" pg_isready -U user > /dev/null 2>&1; then
      echo "✅ $name is up"
      return 0
    fi
    echo "⏳ Waiting for $name... ($i/10)"
    sleep 2
  done
  echo "❌ $name did not become ready"
  exit 1
}

# 開始等待服務
wait_for_http_service "Backend1"   http://localhost:8001/docs
wait_for_http_service "Backend2"   http://localhost:8002/docs
wait_for_http_service "MLflow"     http://localhost:5010
wait_for_http_service "ClickHouse" http://localhost:8123/ping
wait_for_http_service "MinIO"      http://localhost:9001
wait_for_http_service "Grafana"    http://localhost:3002
# wait_for_http_service "Prometheus" http://localhost:9090/-/ready

wait_for_redis
wait_for_postgres "Raw DB" raw_db
wait_for_postgres "Model Meta DB" model_meta_db
wait_for_postgres "MLflow DB" mlflow-db

echo "✅ 所有核心服務啟動完成"
