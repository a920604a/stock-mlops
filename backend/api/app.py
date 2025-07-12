from fastapi import FastAPI
from api.routes import predict
from api.routes import train

app = FastAPI()
app.include_router(predict.router, prefix="")
app.include_router(train.router)
