"""
Pytest Test Fixtures and Application Setup
"""

import asyncio

import pytest
from httpx import AsyncClient

from app.main import app


@pytest.fixture(scope="session")
def event_loop():
    """Session-scoped event loop.

    The app uses a module-level async engine (``app.core.database.engine``)
    whose asyncpg connection pool binds to the event loop that first uses it.
    Pytest-asyncio's default per-test loops would rebind the pool per test and
    raise "another operation is in progress". Sharing one loop for the whole
    session keeps the pool on a single loop so DB-backed tests can run cleanly.
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest.fixture(autouse=True)
def _pin_session_event_loop(event_loop):
    """Keep the session loop installed as the current loop for every test.

    pytest-asyncio (0.23.x) restores the event-loop policy between tests, which
    on Python 3.14 clears the thread's current loop; its internals then call
    ``asyncio.get_event_loop()`` and hit "There is no current event loop".
    Re-pinning the shared session loop before each test keeps both the asyncpg
    pool and the plugin happy.
    """
    asyncio.set_event_loop(event_loop)
    yield
    asyncio.set_event_loop(event_loop)


@pytest.fixture
async def client():
    """Async test HTTP client fixture."""
    async with AsyncClient(app=app, base_url="http://testserver") as c:
        yield c
