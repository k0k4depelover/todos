from .utils import *
from TodoApp.routers.admin import get_db, get_current_user # type: ignore
from fastapi import status
from TodoApp.models import Todos

app.dependency_overrides[get_db]= override_get_db
app.dependency_overrides[get_current_user]= override_get_current_user

def test_admin_read_all_authenticated(test_todo):
    response= client.get("/admin/todo")
    assert response.status_code== status.HTTP_200_OK
    assert response.json()==[{
        'id': test_todo.id,
        'title': 'Learn code',
        'priority': 5,
        'description': 'Need to learn',
        'complete': False,
        'owner_id': 1
    }]

def test_admin_delete_todo(test_todo):
    response= client.delete(f"/admin/todo/{test_todo.id}")
    assert response.status_code==status.HTTP_204_NO_CONTENT
    db= TestingSessionLocal()
    model= db.query(Todos).filter(Todos.id== test_todo.id).first()
    assert model is None

def test_admin_delete_todo_not_found(test_todo):
    response= client.delete("admin/todo/999")
    assert response.status_code== status.HTTP_404_NOT_FOUND
    assert response.json()== {'detail': "User or task not found"}