from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, status, Path
from TodoApp.models import Todos
from TodoApp.database import  SessionLocal
from TodoApp.routers.auth import get_current_user

router=APIRouter(    
    prefix='/admin',
    tags=['Admin']
    )


async def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency= Annotated[Session, Depends(get_db)]
user_dependency= Annotated[dict, Depends(get_current_user)]


@router.get("/todo", status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency, db:db_dependency):
    if user is None or user.get('user_role')!="admin":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication failed')
    return db.query(Todos).all()
    
@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT )
async def delete_todo(user: user_dependency, db: db_dependency, todo_id: int):
    if user is None or user.get('user_role')!='admin':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not authenticated')
    task_delete = db.query(Todos).filter(Todos.id == todo_id).first()
    if task_delete is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User or task not found")
    
    db.query(Todos).filter(Todos.id == todo_id).delete()
    db.commit()
    return "Task Deleted"
