import uuid
from datetime import datetime, timezone
from typing import Optional

from src.models import Task, TaskCreate, TaskUpdate


class TaskStore:
    """In-memory task storage with CRUD operations."""

    def __init__(self) -> None:
        self._tasks: dict[uuid.UUID, Task] = {}

    def list_all(self) -> list[Task]:
        return list(self._tasks.values())

    def get(self, task_id: uuid.UUID) -> Optional[Task]:
        return self._tasks.get(task_id)

    def create(self, data: TaskCreate) -> Task:
        now = datetime.now(timezone.utc)
        task = Task(
            id=uuid.uuid4(),
            title=data.title,
            description=data.description,
            status=data.status,
            created_at=now,
            updated_at=now,
        )
        self._tasks[task.id] = task
        return task

    def update(self, task_id: uuid.UUID, data: TaskUpdate) -> Optional[Task]:
        if task_id not in self._tasks:
            return None
        existing = self._tasks[task_id]
        update_data = data.model_dump(exclude_unset=True)
        updated = existing.model_copy(
            update={**update_data, "updated_at": datetime.now(timezone.utc)}
        )
        self._tasks[task_id] = updated
        return updated

    def delete(self, task_id: uuid.UUID) -> bool:
        return self._tasks.pop(task_id, None) is not None
