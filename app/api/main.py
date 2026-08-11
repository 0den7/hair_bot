"""
FastAPI приложение для веб-календаря.

Предоставляет HTML-страницу с календарем, healthcheck и подключает роутеры
для API.
"""

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from app.api.appointments import router as appointments_router

app = FastAPI(title='Календарь записей')
app.include_router(appointments_router)


@app.get('/', response_class=HTMLResponse)
async def index():
    """Главная страница с календарем."""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Календарь записи</title>
    </head>
    <body>
        <h1>Календарь записи</h1>
        <p>Здесь будет календарь.</p>
    </body>
    </html>
    '''


@app.get('/health')
async def health():
    """Проверка работоспособности."""
    return {'status': 'ok'}
