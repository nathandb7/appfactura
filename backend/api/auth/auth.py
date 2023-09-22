
from fastapi import Depends, HTTPException, status
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing_extensions import Annotated

#oauth2 dependecy
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "name" : "John",
        "lastname" : "Doe",
        "email": "johndoe@example.com",
        "hashed_password": "fakehashedsecret",
        "disabled": False,
    },
    "alice": {
        "username": "alice",
        "name" : "Alice",
        "lastname" : "Wonderson",
        "email": "alice@example.com",
        "hashed_password": "fakehashedsecret2",
        "disabled": True,
    },
}

class User(BaseModel):
    username: str
    name: str
    lastname: str
    email: str
    disabled: bool

class UserInDb(User):
    hashed_password: str


#fetch user from db
def get_user_db(db, username: str) -> UserInDb:
    if username in fake_users_db:
        user = fake_users_db[username]
        return UserInDb(**user)
    return None

def fake_decode_token(token):
    return get_user_db(fake_users_db, token)


def fake_hash_pwd(pwd: str) -> str:
    return "fakehashed" + pwd

async def get_current_user(token : str = Depends(oauth2_scheme)):
    user = fake_decode_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

async def get_current_active_user(current_user: Annotated[User, Depends(get_current_user)]):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def login(form_data: OAuth2PasswordRequestForm) -> dict:
    #find by username
    user_dict = fake_users_db.get(form_data.username)
    print(user_dict)
    if not user_dict:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    user_db = UserInDb(**user_dict)

    received_hashed_password = fake_hash_pwd(form_data.password)

    if received_hashed_password != user_db.hashed_password:
        print(received_hashed_password)
        print(user_db.hashed_password)
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    return {"access_token": user_db.username, "token_type": "bearer"}
