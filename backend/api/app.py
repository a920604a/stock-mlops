import asyncio

from api.kafka_producer import close_kafka_producer, init_kafka_producer
from api.routes import datasets, etl, mlflow_model, models, predict, train
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from src.db.clickhouse.schema.create_clickhouse_table import create_clickhouse_table

clients = set()


app = FastAPI()
Instrumentator().instrument(app).expose(app)

origins = [
    "http://localhost",
    "http://localhost:5173",  # 如果前端跑在 5173 port
    # 其他允許的來源
]

# 設定允許的來源
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# REST API routers

app.include_router(predict.router, prefix="/api", tags=["model"])
app.include_router(train.router, prefix="/api", tags=["model"])
app.include_router(datasets.router, prefix="/api", tags=["datasets"])
app.include_router(etl.router, prefix="/api", tags=["datasets"])
app.include_router(models.router, prefix="/api", tags=["model"])
app.include_router(mlflow_model.router, prefix="/api", tags=["model"])


# 啟動時初始化 Kafka Producer
@app.on_event("startup")
async def startup_event():
    create_clickhouse_table()
    from asyncio import sleep

    from aiokafka.errors import KafkaConnectionError

    for attempt in range(5):
        try:
            await init_kafka_producer()
            print("Kafka Producer 初始化完成")
            break
        except KafkaConnectionError as e:
            print(f"Kafka Producer 初始化失敗: {e}，重試 {attempt + 1}/5")
            await sleep(5)
    else:
        raise RuntimeError("Kafka Producer 初始化失敗，無法啟動應用程式")


@app.on_event("shutdown")
async def shutdown_event():
    await close_kafka_producer()
