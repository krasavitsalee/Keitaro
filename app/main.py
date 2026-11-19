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
    return HTMLResponse("""<!DOCTYPE html>
<html lang="ru"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Keitaro Wrapper</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Anton&family=Inter:wght@300;400;500;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/static/style.css"></head>
<body>
<header class="topbar"><div class="topbar-inner">
  <a href="/" class="logo"><div class="logo-mark">K</div><span>Keitaro Wrapper</span></a>
  <div class="topbar-actions">
    <nav class="topbar-nav">
      <a href="/" class="active">Главная</a>
      <a href="/creator">Создаватор</a>
      <a href="/editor">Редактор</a>
    </nav>
    <div class="status-dot">Подключено к Keitaro</div>
  </div>
</div></header>
<main class="container">
  <div class="hero">
    <h1>Управляйте кампаниями<br><span class="red">Keitaro.</span></h1>
    <p>Создавайте кампании с двумя потоками и редактируйте офферы — без ручной работы в трекере.</p>
  </div>
  <div class="cta-grid">
    <a href="/creator" class="cta-card" style="text-decoration:none;color:inherit;">
      <div class="icon">🚀</div><h3>Создать кампанию</h3>
      <p>Название, страна, оффер — и кампания готова с двумя потоками.</p>
      <span class="arrow">→</span>
    </a>
    <a href="/editor" class="cta-card" style="text-decoration:none;color:inherit;">
      <div class="icon">⚙️</div><h3>Редактировать кампанию</h3>
      <p>Добавляйте и удаляйте офферы в потоках существующих кампаний.</p>
      <span class="arrow">→</span>
    </a>
  </div>
  <div class="stats-row">
    <div class="stat"><div class="num">2</div><div class="label">Потока</div></div>
    <div class="stat"><div class="num">1</div><div class="label">Оффер</div></div>
    <div class="stat"><div class="num">1</div><div class="label">Страна</div></div>
    <div class="stat"><div class="num">∞</div><div class="label">Скорость</div></div>
  </div>
</main>
</body></html>""")