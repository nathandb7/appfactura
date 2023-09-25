from fastapi import Depends, HTTPException, status
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing_extensions import Annotated

from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
import json

SECRET = "984dfa6f49625307e02171558a1088e906aa72e0cab2cae2a696793f49c49e5e"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class DTEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return str(obj)
        return json.JSONEncoder.default(self, obj)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


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


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode_data = data.copy()
    if expires_delta:
        expire_time = datetime.utcnow() + expires_delta
    else:
        expire_time = datetime.utcnow() + timedelta(minutes=15)

    to_encode_data.update({"exp" : expire_time})

    encoded_jwt = jwt.encode(to_encode_data, SECRET, algorithm=ALGORITHM)
    return encoded_jwt

#fetch user from db
def get_user_db(db, username: str) -> UserInDb:
    if username in fake_users_db:
        user = fake_users_db[username]
        return UserInDb(**user)
    return None

def verify_password(plain_pass, hashed_pass) -> bool:
    return pwd_context.verify(plain_pass, hashed_pass)

def fake_decode_token(token):
    return get_user_db(fake_users_db, token)

def fake_hash_pwd(pwd: str) -> str:
    return "fakehashed" + pwd


def authenticate_user(fake_db, username: str, password: str) -> UserInDb:
    user = get_user_db(fake_db, username)
    if not user:
        return None

    if not pwd_context.verify(password, user.hashed_password):
        return None

    return user

async def get_current_user(token : str = Depends(oauth2_scheme)):

    credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},)

    try:
        print(f"Received: {token}")
        payload = jwt.decode(token, SECRET, algorithms=ALGORITHM)
        username: str = payload.get("sub")
        if not username:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError as e:
        print(f"jwt error: {e}")
        raise credentials_exception

    user = get_user_db(fake_users_db, username=token_data.username)
    if not user:
        raise credentials_exception

    return user

async def get_current_active_user(current_user: Annotated[User, Depends(get_current_user)]):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def login(form_data: OAuth2PasswordRequestForm) -> dict:
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    data = {"sub" : user.username}
    access_token = create_access_token(data=data, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}
