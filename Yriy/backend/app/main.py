from fastapi import FastAPI
import os
from .routes import router
from fastapi.staticfiles import StaticFiles
from pathlib import Path

app = FastAPI()

app.include_router(router, prefix='/api')


@app.get("/")
def read_root():
    return {"Hello": "World"}


# Подключаем папку frontend с файлом index.html
app.mount("/", StaticFiles(directory=Path(__file__).parent / "frontend", html=True), name="frontend")
