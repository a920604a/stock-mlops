# 啟動服務
docker-compose up --build -d

# 進入 workflows container
docker exec -it project-workflows-1 bash

# 建立 Deployment（只需一次）
python create_deployment.py
