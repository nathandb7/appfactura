from fastapi import Depends, HTTPException, status
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing_extensions import Annotated
from enum import Enum

from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
import json

SECRET = "984dfa6f49625307e02171558a1088e906aa72e0cab2cae2a696793f49c49e5e"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "name" : "John",
        "lastname" : "Doe",
        "email": "johndoe@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        "disabled": False,
    },
}

ERR_BAD_CREDENTIALS = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},)

ERR_BAD_LOGIN = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},)

class Token(BaseModel):
    access_token: str
    token_type: str
    
class TokenData(BaseModel):
    username: str | None = None

class User(BaseModel):
    username: str
    name: str
    lastname: str
    email: str
    disabled: bool

class UserInDb(User):
    hashed_password: str

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_user_db(db, username: str) -> UserInDb:
    if username in fake_users_db:
        user = fake_users_db[username]
        return UserInDb(**user)
    return None

class UserValidator():
    def __init__(self, token : str = Depends(oauth2_scheme)):
        self.user, self.error = self.validate_and_get_user(token)

    def validate_and_get_user(self, token) -> (UserInDb, HTTPException):
        try:
            print(f"Received: {token}")
            payload = jwt.decode(token, SECRET, algorithms=ALGORITHM)
            username: str = payload.get("sub")
            if not username:
                return None, ERR_BAD_CREDENTIALS
            token_data = TokenData(username=username)
        except JWTError as e:
            print(f"jwt error: {e}")
            return None, ERR_BAD_CREDENTIALS

        user = get_user_db(fake_users_db, username=token_data.username)
        if not user:
            return None, ERR_BAD_CREDENTIALS
        return user, None

class LoginHandler():
    def __init__(self, form_data: OAuth2PasswordRequestForm = Depends()):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.access_token, self.token_type, self.err = self.do_login(form_data)
        pass

    def authenticate_user(self, fake_db, username: str, password: str) -> UserInDb:
        user = get_user_db(fake_db, username)
        if not user or not self.pwd_context.verify(password, user.hashed_password):
            return None
        return user

    def create_access_token(self, data: dict, expires_delta: timedelta | None = None) -> str:
        to_encode_data = data.copy()
        if expires_delta:
            expire_time = datetime.utcnow() + expires_delta
        else:
            expire_time = datetime.utcnow() + timedelta(minutes=15)

        to_encode_data.update({"exp" : expire_time})

        encoded_jwt = jwt.encode(to_encode_data, SECRET, algorithm=ALGORITHM)
        return encoded_jwt

    def do_login(self, form_data: OAuth2PasswordRequestForm) -> dict:
        user = self.authenticate_user(fake_users_db, form_data.username, form_data.password)

        if not user:
            return None, None, ERR_BAD_LOGIN

        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        data = {"sub" : user.username}
        access_token = self.create_access_token(data=data, expires_delta=access_token_expires)

        return access_token, "Bearer", None
