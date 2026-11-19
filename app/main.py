from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import text

from app.database import Base, engine
from app.routers import creator, editor

app = FastAPI(title="Keitaro Wrapper")

# create tables
Base.metadata.create_all(bind=engine)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(creator.router)
app.include_router(editor.router)


@app.get("/")
def index():
    from fastapi.responses import HTMLResponse
    return HTMLResponse('<h1>Keitaro Wrapper</h1><ul><li><a href="/creator">Создаватор кампаний</a></li><li><a href="/editor">Редактор кампаний</a></li></ul>')