import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database import Base, get_db
from main import app

TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def reset_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def dealer_token(client):
    client.post("/auth/register", json={
        "company_name": "Test Bil AB",
        "email": "dealer@test.se",
        "password": "hemligt123",
    })
    resp = client.post("/auth/login", data={
        "username": "dealer@test.se",
        "password": "hemligt123",
    })
    return resp.json()["access_token"]


@pytest.fixture
def auth_headers(dealer_token):
    return {"Authorization": f"Bearer {dealer_token}"}