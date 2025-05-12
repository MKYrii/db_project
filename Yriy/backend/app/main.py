from fastapi import FastAPI
import os
from .routes import router

app = FastAPI()

app.include_router(router, prefix='/api')

@app.get("/")
def read_root():
    return {"Hello": "World"}