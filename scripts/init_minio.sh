#!/bin/sh
echo "🕒 等待 MinIO 啟動..."
sleep 5

echo "🔐 設定 mc alias..."
mc alias set local http://minio:9000 "$MINIO_ROOT_USER" "$MINIO_ROOT_PASSWORD"

echo "📦 嘗試建立 bucket mlflow-artifacts..."
mc mb local/mlflow-artifacts || echo "⚠️ 已存在或無法建立 bucket"
