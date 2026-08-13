"""
FastAPI приложение для веб-календаря.

Предоставляет HTML-страницу с календарем, healthcheck и подключает роутеры
для API.
"""

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.api.appointments import router as appointments_router

app = FastAPI(title='Календарь записей')
app.include_router(appointments_router)
templates = Jinja2Templates(directory='app/templates')


@app.get('/', response_class=HTMLResponse)
async def index(request: Request):
    """Главная страница с календарем."""
    return templates.TemplateResponse(request, 'calendar.html')


@app.get('/health')
async def health():
    """Проверка работоспособности."""
    return {'status': 'ok'}
