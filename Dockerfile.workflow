FROM prefecthq/prefect:2.16.3-python3.10

WORKDIR /app
# 因為 build context 是 ./workflows，所以直接複製所有檔案

COPY . /app/

RUN pip install -r requirements.txt

CMD ["prefect", "agent", "start", "-q", "default"]
