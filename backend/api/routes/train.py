# api/routes/train.py
from fastapi import APIRouter, BackgroundTasks
import logging
from tasks.train_model_task import train_model_task
from fastapi import HTTPException
from dataclasses import asdict
from celery.result import AsyncResult
from celery_worker import celery_app
from src.train_config import TrainConfig
from api.schemas.train_request import TrainRequest, TrainResponse
from src.db.postgres.crud.crud import get_model

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/train")
def submit_train_job(req: TrainRequest):
    print(f"submit_train_job {req.model_id}")
    model = get_model(req.model_id)
    print("model", model.dict(), type(model.dict()))
    # task = train_model_task.delay(model)
    task = train_model_task.delay(model.dict())
    print(f"Submitted train task with ID: {task.id}")
    return TrainResponse(task_id=f"{task.id}")


@router.get("/train/status/{task_id}")
def get_train_status(task_id: str):
    result = AsyncResult(task_id, app=celery_app)

    if result.state == "PENDING":
        return {"task_id": task_id, "status": "pending"}
    elif result.state == "STARTED":
        return {"task_id": task_id, "status": "running"}
    elif result.state == "SUCCESS":
        return {"task_id": task_id, "status": "completed", "result": result.result}
    elif result.state == "FAILURE":
        return {"task_id": task_id, "status": "failed", "error": str(result.result)}
    else:
        raise HTTPException(status_code=400, detail="Unknown task state")
