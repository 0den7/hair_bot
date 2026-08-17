"""
Авторизация мастера.

Проверка пароля через куки. Пароль хранится в .env.
"""

import os

from dotenv import load_dotenv
from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

load_dotenv()

CALENDAR_PASSWORD = os.getenv('CALENDAR_PASSWORD', 'admin')

router = APIRouter()

templates = Jinja2Templates(directory='app/templates')


def is_authorized(request: Request):
    """Проверяет, авторизован ли мастер."""
    return request.cookies.get('master_auth') == CALENDAR_PASSWORD


@router.get('/login', response_class=HTMLResponse)
async def login_page(request: Request):
    """Страница входа."""
    return templates.TemplateResponse(request, 'login.html')


@router.post('/login')
async def login(password: str = Form(...)):
    """Обрабатывает вход."""
    if password != CALENDAR_PASSWORD:
        raise HTTPException(status_code=403, detail='Неверный пароль')
    response = RedirectResponse('/', status_code=303)
    response.set_cookie('master_auth', password)
    return response


@router.get('/logout')
async def logout():
    """Выход (очистка куки)."""
    response = RedirectResponse('/login', status_code=303)
    response.delete_cookie('master_auth')
    return response
