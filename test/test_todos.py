from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from TodoApp.database import Base
from TodoApp.main import app
from TodoApp.routers.todos import get_db
from TodoApp.routers.auth import get_current_user
from fastapi.testclient import TestClient
from fastapi import status
import pytest

from TodoApp.models import Todos
SQL_ALCHEMY_DATABASE_URL= 'postgresql://postgres:k4tty!23@localhost/testdb'

engine= create_engine(
    SQL_ALCHEMY_DATABASE_URL,
    poolclass= StaticPool
)

TestingSessionLocal= sessionmaker(autocommit= False, autoflush= False, bind= engine)

@pytest.fixture
def test_todo():
    todo= Todos(
        title='Learn code',
        description='Need to learn',
        priority= 5,
        complete=False, 
        id=1

    )
    db= TestingSessionLocal()
    db.add(todo)
    db.commit()
    yield todo
    with engine.connect() as conection:
        conection.execute(text("DELETE FROM todos; "))
        conection.commit()

Base.metadata.create_all(bind=engine)


def override_get_db():
    db= TestingSessionLocal()
    try:
        yield db
    finally:
        db.close() 

def override_get_current_user():
    return {'username': 'kok2', 'user_id': 1, 'user_role': 'admin'}

app.dependency_overrides[get_db]= override_get_db
app.dependency_overrides[get_current_user]= override_get_current_user

client= TestClient(app)

def test_read_all_authenticated(test_todo):
    response= client.get("/")
    assert response.status_code== status.HTTP_200_OK
    assert response.json()==[]

