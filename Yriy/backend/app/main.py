from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pathlib import Path

from .routes import router

app = FastAPI()

# Подключаем API роуты
app.include_router(router, prefix='/api')

# Путь к HTML-файлу
MAIN_PAGE_PATH = Path(__file__).parent.parent / "frontend" / "main_page.html"

@app.get("/", response_class=HTMLResponse)
async def read_root():
    if not MAIN_PAGE_PATH.exists():
        raise HTTPException(status_code=404, detail="HTML file not found")

    with open(MAIN_PAGE_PATH, "r", encoding="utf-8") as file:
        html_content = file.read()
    return HTMLResponse(content=html_content, status_code=200)
