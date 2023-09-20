from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return { "message" : "Bitch Y"}

@app.get("/test")
async def root():
    return { "message" : "Not Test"}
