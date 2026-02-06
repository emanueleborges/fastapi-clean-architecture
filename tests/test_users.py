import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.session import Base
from app.db.session_async import get_db

# Banco em memória para testes, com suporte a Async
SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    class_=AsyncSession, 
    autocommit=False, 
    autoflush=False, 
    bind=test_engine
)

async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session

app.dependency_overrides[get_db] = override_get_db

@pytest_asyncio.fixture
async def client():
    # Cria tabelas
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Cliente Async
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    
    # Limpa tabelas (opcional com StaticPool in-memory, mas boa prática)
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.mark.asyncio
async def test_user_crud_flow(client: AsyncClient):
    payload = {
        "email": "user@example.com",
        "is_active": True,
        "password": "string123",
    }

    # Create
    create_resp = await client.post("/api/v1/users/", json=payload)
    assert create_resp.status_code == 200
    created = create_resp.json()
    assert created["email"] == payload["email"]
    assert created["is_active"] is True
    assert "id" in created

    user_id = created["id"]

    # List
    list_resp = await client.get("/api/v1/users/")
    assert list_resp.status_code == 200
    users = list_resp.json()
    assert len(users) == 1

    # Filter List
    filter_active = await client.get("/api/v1/users/?is_active=true")
    assert len(filter_active.json()) == 1

    filter_inactive = await client.get("/api/v1/users/?is_active=false")
    assert len(filter_inactive.json()) == 0

    # Retrieve
    get_resp = await client.get(f"/api/v1/users/{user_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["email"] == payload["email"]

    # Update
    update_payload = {"email": "new@example.com", "is_active": False}
    update_resp = await client.put(f"/api/v1/users/{user_id}", json=update_payload)
    assert update_resp.status_code == 200
    updated = update_resp.json()
    assert updated["email"] == "new@example.com"
    assert updated["is_active"] is False

    # Delete
    delete_resp = await client.delete(f"/api/v1/users/{user_id}")
    assert delete_resp.status_code == 204

    # Confirm delete
    get_after_delete = await client.get(f"/api/v1/users/{user_id}")
    assert get_after_delete.status_code == 404
