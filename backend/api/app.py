from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import datasets

from api.routes import predict
from api.routes import train
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


app.include_router(predict.router, prefix="/api")
app.include_router(train.router, prefix="/api")

app.include_router(datasets.router, prefix="/api", tags=["datasets"])