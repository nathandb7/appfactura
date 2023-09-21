from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import APIRouter

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

app.include_router(api_router)
