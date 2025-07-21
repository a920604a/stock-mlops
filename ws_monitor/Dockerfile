# 使用官方 Python 镜像作为基础镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 复制当前目录下的所有文件到容器的工作目录
COPY . /app

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 暴露 FastAPI 默认端口
EXPOSE 8000

# 设置环境变量
ENV KAFKA_BOOTSTRAP_SERVERS=kafka:9092

# 启动 FastAPI 应用
CMD ["uvicorn", "ws_app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
