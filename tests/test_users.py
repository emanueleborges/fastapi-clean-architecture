import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.session import Base, get_db

SQLALCHEMY_DATABASE_URL = "sqlite://"

test_engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def client():
    Base.metadata.create_all(bind=test_engine)
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=test_engine)


def test_user_crud_flow(client: TestClient):
    payload = {
        "email": "user@example.com",
        "is_active": True,
        "password": "string123",
    }

    # Create
    create_resp = client.post("/api/v1/users/", json=payload)
    assert create_resp.status_code == 200
    created = create_resp.json()
    assert created["email"] == payload["email"]
    assert created["is_active"] is True
    assert "id" in created

    user_id = created["id"]

    # List
    list_resp = client.get("/api/v1/users/")
    assert list_resp.status_code == 200
    users = list_resp.json()
    assert len(users) == 1

    # Retrieve
    get_resp = client.get(f"/api/v1/users/{user_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["email"] == payload["email"]

    # Update
    update_payload = {"email": "new@example.com", "is_active": False}
    update_resp = client.put(f"/api/v1/users/{user_id}", json=update_payload)
    assert update_resp.status_code == 200
    updated = update_resp.json()
    assert updated["email"] == "new@example.com"
    assert updated["is_active"] is False

    # Delete
    delete_resp = client.delete(f"/api/v1/users/{user_id}")
    assert delete_resp.status_code == 204

    # Confirm delete
    get_after_delete = client.get(f"/api/v1/users/{user_id}")
    assert get_after_delete.status_code == 404
