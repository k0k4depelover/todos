from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from TodoApp.database import Base
from TodoApp.main import app
from passlib.context import CryptContext 
from fastapi.testclient import TestClient
import pytest
from TodoApp.models import Todos, User
from TodoApp.routers import admin
# <-- importante para acceder a las dependencias

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SQL_ALCHEMY_DATABASE_URL = 'postgresql://postgres:k4tty!23@localhost/testdb'

engine = create_engine(
    SQL_ALCHEMY_DATABASE_URL,
    poolclass=StaticPool
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

def override_get_current_user():
    return {'username': 'kok2', 'user_id': 1, 'user_role': 'admin'}

# 👉 Aquí se aplican los overrides
app.dependency_overrides[admin.get_db] = override_get_db
app.dependency_overrides[admin.get_current_user] = override_get_current_user

client = TestClient(app)

@pytest.fixture
def test_user():
    user= User(
        username="kok2",
        email="oskar@gmail.com",
        first_name="Oskar",
        last_name= "Cermeno",
        hashed_password= bcrypt_context.hash("hashedpassword"),
        role="admin",
        phone_number="(502)42356263"

    )
    db=TestingSessionLocal()
    db.add(user)
    db.commit()
    db.refresh(user)
    yield user
    db.close()
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM users"))
        connection.execute(text("ALTER SEQUENCE todos_id_seq RESTART WITH 1"))
        connection.commit()



@pytest.fixture
def test_todo(test_user):
    db = TestingSessionLocal()
    todo = Todos(
        title='Learn code',
        description='Need to learn',
        priority=5,
        complete=False,
        owner_id=test_user.id
    )

    db.add(todo)
    db.commit()
    db.refresh(todo)
    yield todo
    db.close()
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM todos"))
        connection.execute(text("ALTER SEQUENCE todos_id_seq RESTART WITH 1"))
        connection.commit()

