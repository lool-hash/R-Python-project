import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base, get_db
from app.core.security import hash_password, create_access_token
from app.models.user import User

TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client():
    from app.main import app
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def _seed_user(role: str) -> str:
    """Insert user directly into test DB and return a JWT token."""
    db = TestingSessionLocal()
    try:
        email = f"{role}@test.com"
        user = db.query(User).filter(User.email == email).first()
        if not user:
            user = User(
                email=email,
                username=role,
                hashed_password=hash_password("testpass123"),
                role=role,
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        return create_access_token({"sub": user.id})
    finally:
        db.close()


@pytest.fixture()
def admin_headers(client):          # depends on client so DB override is active
    token = _seed_user("admin")
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def customer_headers(client):       # depends on client so DB override is active
    token = _seed_user("customer")
    return {"Authorization": f"Bearer {token}"}
