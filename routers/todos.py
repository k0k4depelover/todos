from typing import Annotated
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, status, Path
from TodoApp.models import Todos
from TodoApp.database import SessionLocal
from TodoApp.routers.auth import get_current_user

router=APIRouter()


async def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency= Annotated[Session, Depends(get_db)]
user_dependency= Annotated[dict, Depends(get_current_user)]


class TodosRequest(BaseModel):
    title: str =Field(min_length=3)
    description: str= Field(min_length=3, max_length=100)
    priority : int =Field(gt=0, lt=6)
    complete: bool 

@router.get("/",  status_code=status.HTTP_200_OK)
def read_all(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")
    return db.query(Todos).filter(Todos.owner_id== user.get('user_id')).all()


@router.get("/todo/{todo_id}", status_code=status.HTTP_200_OK)
async def read_todo(user: user_dependency, db: db_dependency, todo_id: int= Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")
    todo_model= db.query(Todos).filter(Todos.id== todo_id).filter(Todos.owner_id== user.get('user_id')).first()
    if todo_model is  None:
        raise HTTPException(status_code=404, detail="Data not found.")
    return todo_model

    


@router.post("/todo/", status_code=status.HTTP_201_CREATED)
async def create_todo(user: user_dependency, db:db_dependency, todo_request: TodosRequest):

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")
    todo_model= Todos(**todo_request.model_dump(), owner_id=user.get('user_id'))

    db.add(todo_model)
    db.commit()

@router.put("/todo/{id_update}", status_code= status.HTTP_204_NO_CONTENT)
async def update_todo(user: user_dependency, db: db_dependency, todo_request: TodosRequest, id_update: int= Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")
    
    todo_model= db.query(Todos).filter(Todos.id== id_update).filter(Todos.owner_id== user.get('user_id')).first()
    if todo_model is not None:
        todo_model.title=todo_request.title
        todo_model.description=todo_request.description
        todo_model.priority=todo_request.priority
        todo_model.complete=todo_request.complete
        db.add(todo_model)
        db.commit()
    else:
        raise HTTPException(status_code=404, detail="Not content found")


@router.delete("/todo/{id_todo}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependency, db: db_dependency, id_todo: int= Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")
    todo_model=db.query(Todos).filter(Todos.id == id_todo).filter(Todos.owner_id== user.get('user_id')).first()

    if todo_model is None:
        raise HTTPException(status_code=404, detail="Not found")
    db.query(Todos).filter(Todos.id ==id_todo).filter(Todos.owner_id== user.get('user_id')).delete()
    db.commit()
