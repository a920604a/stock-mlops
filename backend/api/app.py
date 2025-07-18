from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import datasets
from api.routes import predict
from api.routes import train
from api.routes import etl
from api.routes import models
from api.routes import mlflow_model

from prometheus_fastapi_instrumentator import Instrumentator


app = FastAPI()
Instrumentator().instrument(app).expose(app)

# 設定允許的來源
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # ⬅️ 加上 http://
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(predict.router, prefix="/api", tags=["model"])
app.include_router(train.router, prefix="/api", tags=["model"])
app.include_router(datasets.router, prefix="/api", tags=["datasets"])
app.include_router(etl.router, prefix="/api", tags=["datasets"])
app.include_router(models.router, prefix="/api", tags=["model"])
app.include_router(mlflow_model.router, prefix="/api", tags=["model"])
