from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from fastapi.security import (OAuth2PasswordBearer,
                              OAuth2PasswordRequestForm)

from typing_extensions import Annotated

import jose
from datetime import datetime, timedelta
import auth

API_PREFIX = "/api"
app = FastAPI()

allowed_origins = [ "http://facturas-frontend:5173"]

app.add_middleware(CORSMiddleware,
                   allow_origins = allowed_origins,
                   allow_credentials = True,
                   allow_methods=["*"],
                   allow_headers=["*"])


api_router = APIRouter(prefix=API_PREFIX)

@api_router.get("/hello-world")
async def test():
    return { "message" : "Hello, World!"}

@api_router.get("/users/me")
async def get_user(user_validator: auth.UserValidator = Depends(auth.UserValidator)):
    if user_validator.error:
        raise user_validator.error
    return user_validator.user

@api_router.post("/token")
async def login(login_handler: auth.LoginHandler = Depends(auth.LoginHandler)):
    if login_handler.err:
        raise login_handler.err
    return {"access_token": login_handler.access_token, 
            "token_type": login_handler.token_type}

app.include_router(api_router)
