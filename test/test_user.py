from .utils import *
from TodoApp.routers.admin import get_db, get_current_user
from fastapi import status

app.dependency_overrides[get_db]= override_get_db
app.dependency_overrides[get_current_user]= override_get_current_user

def test_return_user(test_user):
    response= client.get("/users")
    assert response.status_code== status.HTTP_200_OK
    assert response.json() is None

