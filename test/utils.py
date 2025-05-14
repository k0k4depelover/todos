from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from TodoApp.database import Base
from TodoApp.main import app
from fastapi.testclient import TestClient
import pytest
from TodoApp.models import Todos

SQL_ALCHEMY_DATABASE_URL= 'postgresql://postgres:k4tty!23@localhost/testdb' #Reusable

engine= create_engine(
    SQL_ALCHEMY_DATABASE_URL, #Reusable
    poolclass= StaticPool
)

TestingSessionLocal= sessionmaker(autocommit= False, autoflush= False, bind= engine) #Reusable
Base.metadata.create_all(bind=engine) #Reusable 



def override_get_db(): #Reusable
    db= TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()




def override_get_current_user(): #Reusable
    return {'username': 'kok2', 'user_id': 1, 'user_role': 'admin'}


client= TestClient(app)

@pytest.fixture
def test_todo():
    todo= Todos(
        title='Learn code',
        description='Need to learn',
        priority= 5,
        complete=False, 
        owner_id=1

    )
    db= TestingSessionLocal() #Reusable
    db.add(todo)
    db.commit()
    db.refresh(todo)
    yield todo
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM todos"))
        connection.execute(text("ALTER SEQUENCE todos_id_seq RESTART WITH 1"))  # Reinicia la secuencia
        connection.commit()



