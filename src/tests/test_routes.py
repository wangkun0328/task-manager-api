import asyncio

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from src.routes import router, store


def create_test_app() -> FastAPI:
    """Create a test app without rate limiting middleware."""
    app = FastAPI()
    app.include_router(router)
    return app


def _client():
    app = create_test_app()
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test")


def run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


@pytest.fixture(autouse=True)
def clear_store():
    """Reset the in-memory store before each test."""
    store._tasks.clear()
    yield


def test_health():
    async def _test():
        async with _client() as c:
            r = await c.get("/health")
            assert r.status_code == 200
            assert r.json() == {"status": "healthy"}

    run(_test())


def test_create_task():
    async def _test():
        async with _client() as c:
            r = await c.post("/tasks", json={"title": "New Task", "description": "Do something"})
            assert r.status_code == 201
            data = r.json()
            assert data["title"] == "New Task"
            assert data["status"] == "todo"
            assert "id" in data
            assert "created_at" in data

    run(_test())


def test_create_task_missing_title():
    async def _test():
        async with _client() as c:
            r = await c.post("/tasks", json={"description": "No title"})
            assert r.status_code == 422  # Pydantic validation

    run(_test())


def test_get_all_tasks_empty():
    async def _test():
        async with _client() as c:
            r = await c.get("/tasks")
            assert r.status_code == 200
            assert r.json() == []

    run(_test())


def test_get_all_tasks():
    async def _test():
        async with _client() as c:
            await c.post("/tasks", json={"title": "Task 1"})
            await c.post("/tasks", json={"title": "Task 2"})
            r = await c.get("/tasks")
            assert r.status_code == 200
            assert len(r.json()) == 2

    run(_test())


def test_get_task_by_id():
    async def _test():
        async with _client() as c:
            r = await c.post("/tasks", json={"title": "Find Me"})
            tid = r.json()["id"]
            r = await c.get(f"/tasks/{tid}")
            assert r.status_code == 200
            assert r.json()["title"] == "Find Me"

    run(_test())


def test_get_task_not_found():
    async def _test():
        async with _client() as c:
            r = await c.get("/tasks/00000000-0000-0000-0000-000000000000")
            assert r.status_code == 404

    run(_test())


def test_update_task():
    async def _test():
        async with _client() as c:
            r = await c.post("/tasks", json={"title": "Old Title"})
            tid = r.json()["id"]
            r = await c.put(f"/tasks/{tid}", json={"title": "New Title", "status": "in_progress"})
            assert r.status_code == 200
            assert r.json()["title"] == "New Title"
            assert r.json()["status"] == "in_progress"

    run(_test())


def test_update_task_not_found():
    async def _test():
        async with _client() as c:
            r = await c.put(
                "/tasks/00000000-0000-0000-0000-000000000000",
                json={"title": "Nope"},
            )
            assert r.status_code == 404

    run(_test())


def test_delete_task():
    async def _test():
        async with _client() as c:
            r = await c.post("/tasks", json={"title": "Delete Me"})
            tid = r.json()["id"]
            r = await c.delete(f"/tasks/{tid}")
            assert r.status_code == 204
            # Verify deleted
            r = await c.get(f"/tasks/{tid}")
            assert r.status_code == 404

    run(_test())


def test_delete_task_not_found():
    async def _test():
        async with _client() as c:
            r = await c.delete("/tasks/00000000-0000-0000-0000-000000000000")
            assert r.status_code == 404

    run(_test())


