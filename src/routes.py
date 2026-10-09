import logging
import uuid as _uuid

from fastapi import APIRouter, HTTPException

from src.models import Task, TaskCreate, TaskUpdate
from src.store import TaskStore

logger = logging.getLogger(__name__)

router = APIRouter()
store = TaskStore()


@router.get("/health", tags=["Health"])
async def health() -> dict[str, str]:
    logger.info("Health check requested")
    return {"status": "healthy"}


@router.get("/tasks", response_model=list[Task], tags=["Tasks"])
async def get_tasks() -> list[Task]:
    tasks = store.list_all()
    logger.info("Returning %d tasks", len(tasks))
    return tasks


@router.get(
    "/tasks/{task_id}",
    response_model=Task,
    tags=["Tasks"],
    responses={404: {"description": "Task not found"}},
)
async def get_task(task_id: _uuid.UUID) -> Task:
    task = store.get(task_id)
    if not task:
        logger.warning("Task %s not found", task_id)
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.post(
    "/tasks",
    response_model=Task,
    status_code=201,
    tags=["Tasks"],
    responses={400: {"description": "Validation error"}},
)
async def create_task(data: TaskCreate) -> Task:
    task = store.create(data)
    logger.info("Created task %s", task.id)
    return task


@router.put(
    "/tasks/{task_id}",
    response_model=Task,
    tags=["Tasks"],
    responses={404: {"description": "Task not found"}},
)
async def update_task(task_id: _uuid.UUID, data: TaskUpdate) -> Task:
    task = store.update(task_id, data)
    if not task:
        logger.warning("Task %s not found for update", task_id)
        raise HTTPException(status_code=404, detail="Task not found")
    logger.info("Updated task %s", task_id)
    return task


@router.delete(
    "/tasks/{task_id}",
    status_code=204,
    tags=["Tasks"],
    responses={404: {"description": "Task not found"}},
)
async def delete_task(task_id: _uuid.UUID) -> None:
    if not store.delete(task_id):
        logger.warning("Task %s not found for deletion", task_id)
        raise HTTPException(status_code=404, detail="Task not found")
    logger.info("Deleted task %s", task_id)
