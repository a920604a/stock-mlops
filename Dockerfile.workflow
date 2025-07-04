FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

# 直接執行你的 main.py（裡面有呼叫 etl_flow_with_schedule）
CMD ["python", "etl_script.py"]
