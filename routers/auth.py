from fastapi import  APIRouter, status, Depends, HTTPException
from pydantic import BaseModel
from TodoApp.models import User
from TodoApp.database import SessionLocal
from passlib.context import CryptContext
from typing import Annotated
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from datetime import timedelta, datetime, timezone

SECRET_KEY="sdg451341&$%2vsdg*/5342$41/(!644)12gbdfmAFSFtry_hgd-bfd25641@53oler6"
ALGORITHM="HS256"
oauth2_bearer=OAuth2PasswordBearer(tokenUrl='/auth/token')

router=APIRouter(
    prefix='/auth',
    tags=['auth']
)

bcrypt_context=CryptContext(schemes=['bcrypt'], deprecated='auto')

async def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()
db_dependency= Annotated[Session, Depends(get_db)]

class CreateUserRequest(BaseModel):
    username:str
    email:str
    first_name: str
    last_name:str
    password: str
    role:str
    phone_number: str


class token(BaseModel):
    access_token:str
    token_type:str

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, create_user: CreateUserRequest):
    created_user= User(
        email= create_user.email,
        username= create_user.username,
        first_name=create_user.first_name,
        last_name= create_user.last_name,
        role= create_user.role,
        hashed_password= bcrypt_context.hash(create_user.password),
        phone_number= create_user.phone_number,
        is_active=True
            )
    db.add(created_user)
    db.commit()


    
                               
def authenticate_user(username: str, password: str, db: db_dependency):
    user= db.query(User).filter(User.username== username).first()
    if not user:
        return False
    
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    
    return user

def create_access_token(username: str, user_id: int, role:str, expires_delta: timedelta):
    # ✅ Parte del JWT: Payload (cuerpo del token)
    # Contiene los "claims" personalizados que deseamos incluir
    # En este caso: el nombre de usuario y el ID del usuario
    encode = {
        'sub': username,  # 'sub' es un claim estándar que representa el sujeto del token
        'id': user_id, 
        'role': role    # 'id' es un claim personalizado para identificar al usuario
    }

    # ✅ Parte del JWT: Claim de expiración (también va en el payload)
    # Define cuándo expira el token. Es un claim estándar: 'exp'
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({'exp': expires})

    # ✅ Parte del JWT: Firma (Signature)
    # Aquí se genera el token completo firmando el payload codificado
    # con el algoritmo elegido (por ejemplo, HS256) y la clave secreta
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

#Aun no la hemos usado
async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload= jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM] )
        username: str= payload.get("sub")
        user_id:int= payload.get("id")
        user_role:str=payload.get("role")
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Can't validate token user.")
        
        return {'username': username, 'user_id': user_id, 'user_role': user_role}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Can't validate token user.")

@router.post("/token/", status_code= status.HTTP_202_ACCEPTED, response_model=token)
async def login_for_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                          db: db_dependency):
    
    user= authenticate_user(form_data.username, form_data.password, db)
    
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Could not authenticate user")
    
    token= create_access_token(user.username, user.id, user.role, timedelta(minutes=20))
    return {'access_token': token, 'token_type': 'bearer'}

