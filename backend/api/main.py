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

#from auth import log
#from passlib.context import 
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

API_PREFIX = "/api"
app = FastAPI()

allowed_origins = [ "http://facturas-frontend:5173"]

app.add_middleware(CORSMiddleware,
                   allow_origins = allowed_origins,
                   allow_credentials = True,
                   allow_methods=["*"],
                   allow_headers=["*"])


api_router = APIRouter(prefix="/api")

@api_router.get("/hello-world")
async def test():
    return { "message" : "Hello, World!"}

@api_router.get("/items")
async def read_items(token: Annotated[str, Depends(oauth2_scheme)]):
    return {"token" : token}

@api_router.get("/users/me")
async def read_subscribers(subscriber : auth.User = Depends(auth.get_current_active_user)):
    return subscriber

@api_router.post("/token")
async def login(form_data : OAuth2PasswordRequestForm = Depends()):
    return await auth.login(form_data)

app.include_router(api_router)
