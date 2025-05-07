from typing import Annotated
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, status, Path
from TodoApp.models import User, Todos
from TodoApp.database import  SessionLocal
from TodoApp.routers.auth import get_current_user
from passlib.context import CryptContext

router=APIRouter(    
    prefix='/users',
    tags=['Users']
    )
bcrypt_context=CryptContext(schemes=['bcrypt'], deprecated='auto')

class UserVerification(BaseModel):
    password : str
    new_password: str = Field(min_length=6)


async def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency= Annotated[Session, Depends(get_db)]
user_dependency= Annotated[dict, Depends(get_current_user)]
bcrypt_context=CryptContext(schemes=['bcrypt'], deprecated='auto')

@router.get("/", status_code=status.HTTP_200_OK)
async def read_all(db: db_dependency, user: user_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    return db.query(User).filter(User.id== user.get('user_id')).all()


@router.put("/update_phone/{phone_number}", status_code=status.HTTP_202_ACCEPTED)
async def update_phone_number(user: user_dependency, db: db_dependency, phone_number: str):
    if user is None: 
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    user_model= db.query(User).filter(User.id == user.get('user_id')).first()
    user_model.phone_number= phone_number
    db.add(user_model)
    db.commit()

@router.put("/{id_user}", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(db: db_dependency, user: user_dependency, user_verification: UserVerification):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")
    user_model= db.query(User).filter(User.id== user.get("user_id")).first()

    if not bcrypt_context.verify(user_verification.password, user_model.hashed_password):
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Error on password change.")

    user_model.hashed_password= bcrypt_context.hash(user_verification.new_password)
    db.add(user_model)
    db.commit()