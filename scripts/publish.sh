#!/bin/bash
set -e

# 你在 Makefile 中帶入的 image tag
IMAGE_NAME="${LOCAL_IMAGE_NAME:-stock-mlops-backend:latest}"

# 先登入 Docker Hub（如果沒先登入的話，理想在 CI/CD 透過 docker/login-action 完成）
# 這裡假設已經登入成功

echo "🔨 Publish backend image: $IMAGE_NAME"

# 確認本地有這個 image
if ! docker image inspect "$IMAGE_NAME" >/dev/null 2>&1; then
    echo "❌ Image $IMAGE_NAME 不存在，請先執行 build"
    exit 1
fi

# 你的 Docker Hub repository 名稱（記得替換成你的帳號/專案名）
DOCKERHUB_REPO="your_dockerhub_username/stock-mlops-backend"

# Tag image 為 Docker Hub 格式
docker tag "$IMAGE_NAME" "$DOCKERHUB_REPO:latest"
docker tag "$IMAGE_NAME" "$DOCKERHUB_REPO:${IMAGE_NAME##*:}" # 也打 tag 原本的 tag

# Push image
docker push "$DOCKERHUB_REPO:latest"
docker push "$DOCKERHUB_REPO:${IMAGE_NAME##*:}"

echo "✅ Publish 完成"
