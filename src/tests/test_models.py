import uuid

import pytest

from src.models import Task, TaskCreate, TaskStatus, TaskUpdate


def test_task_create_valid():
    data = TaskCreate(title="Test", description="A test task")
    assert data.title == "Test"
    assert data.description == "A test task"
    assert data.status == TaskStatus.TODO


def test_task_create_with_status():
    data = TaskCreate(title="In Progress Task", status=TaskStatus.IN_PROGRESS)
    assert data.status == TaskStatus.IN_PROGRESS


def test_task_create_empty_title_raises():
    with pytest.raises(Exception):
        TaskCreate(title="")


def test_task_create_long_title_raises():
    with pytest.raises(Exception):
        TaskCreate(title="x" * 201)


def test_task_create_long_description_raises():
    with pytest.raises(Exception):
        TaskCreate(description="x" * 1001)


def test_task_create_invalid_status_raises():
    with pytest.raises(Exception):
        TaskCreate.model_validate({"title": "Test", "status": "invalid"})


def test_task_update_partial():
    data = TaskUpdate(title="Updated Title")
    assert data.title == "Updated Title"
    assert data.description is None
    assert data.status is None


def test_task_full_model():
    task = Task(
        id=uuid.uuid4(),
        title="Full Task",
        description="Full description",
        status=TaskStatus.DONE,
        created_at="2026-01-01T00:00:00Z",
        updated_at="2026-01-01T00:00:00Z",
    )
    assert task.id is not None
    assert task.status == TaskStatus.DONE
    assert task.title == "Full Task"
