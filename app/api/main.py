"""
FastAPI приложение для веб-календаря.

Предоставляет HTML-страницу с календарем, healthcheck и подключает роутеры
для API.
"""

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.api.appointments import router as appointments_router
from app.api.auth import is_authorized, router as auth_router
from app.api.services import router as services_router
from app.api.working_hours import router as working_hours_router
from app.core import constants

app = FastAPI(title=constants.APP_TITLE)
app.include_router(appointments_router)
app.include_router(auth_router)
app.include_router(services_router)
app.include_router(working_hours_router)
templates = Jinja2Templates(directory='app/templates')


@app.middleware('http')
async def check_auth(request: Request, call_next):
    """Защищает /api/ от неавторизованного доступа."""
    if (
        request.url.path.startswith(constants.API_PREFIX) and
        not is_authorized(request)
    ):
        return JSONResponse(
            status_code=401,
            content={'detail': 'Требуется авторизация'}
        )
    return await call_next(request)


@app.get('/', response_class=HTMLResponse)
async def index(request: Request):
    """Главная страница с календарем (только для авторизованных)."""
    if not is_authorized(request):
        return RedirectResponse('/login', status_code=303)
    return templates.TemplateResponse(request, 'calendar.html')


@app.get('/health')
async def health():
    """Проверка работоспособности."""
    return {'status': constants.HEALTH_OK}
