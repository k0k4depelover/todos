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
        owner_id=1

    )
    db= TestingSessionLocal()
    db.add(todo)
    db.commit()
    db.refresh(todo)
    yield todo
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM todos"))
        connection.execute(text("ALTER SEQUENCE todos_id_seq RESTART WITH 1"))  # Reinicia la secuencia
        connection.commit()
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
    assert response.json() == [{
        'id': test_todo.id,
        'title': 'Learn code',
        'priority': 5,
        'description': 'Need to learn',
        'complete': False,
        'owner_id': 1
    }]

def test_read_one_authenticated(test_todo):
    response = client.get(f"/todo/{test_todo.id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        'id': test_todo.id,
        'title': 'Learn code',
        'priority': 5,
        'description': 'Need to learn',
        'complete': False,
        'owner_id': 1
    }

def test_read_one_authenticated_not_found():
    response=client.get("/todo/999")
    assert response.status_code== status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'Data not found.'}

def test_create_todo(test_todo):   
    request_data={
        'title': 'New Todo',
        'priority': 5,
        'description': 'New Description',
        'complete': False,

    }

    response = client.post("/todo", json= request_data)
    assert response.status_code== status.HTTP_201_CREATED
    db= TestingSessionLocal()
    model= db.query(Todos).filter(Todos.id== 2).first()
    assert model.title==request_data.get('title')
    assert model.priority==request_data.get('priority')
    assert model.description==request_data.get('description')
    assert model.complete==request_data.get('complete')

def test_update_todo(test_todo):
    request_data={
        'title': 'Change Todo',
        'priority': 5,
        'description': 'Change Description',
        'complete': False,

    }
    response= client.put("/todo/1", json=request_data)
    assert response.status_code== status.HTTP_204_NO_CONTENT
    db= TestingSessionLocal()
    model= db.query(Todos).filter(Todos.id== 1).first()
    assert model.title==request_data.get('title')
    assert model.priority==request_data.get('priority')
    assert model.description==request_data.get('description')
    assert model.complete==request_data.get('complete')

def test_update_todo_not_found(test_todo):
    request_data={
        'title': 'Change Todo',
        'priority': 5,
        'description': 'Change Description',
        'complete': False,

    }
    response= client.put("/todo/999", json=request_data)
    assert response.status_code== status.HTTP_404_NOT_FOUND
    assert response.json()== {'detail': "Not content found"}

def test_delete_todo(test_todo):
    response= client.delete(f'/todo/{test_todo.id}')
    assert response.status_code==status.HTTP_204_NO_CONTENT
    db= TestingSessionLocal()
    model= db.query(Todos).filter(Todos.id== test_todo.id).first()
    assert model is None