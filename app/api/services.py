"""
API для управления услугами.
"""

from fastapi import APIRouter, Body

from app.services.booking import (
    get_all_services,
    create_service,
    update_service,
    toggle_service_active,
    delete_service
)

router = APIRouter(prefix='/api/services', tags=['services'])


@router.get('/')
async def get_services():
    """Возвращает список всех услуг."""
    services = await get_all_services()

    return [
        {
            'id': service.id,
            'name': service.name,
            'duration': service.duration,
            'price': service.price,
            'description': service.description,
            'is_active': service.is_active
        }
        for service in services
    ]


@router.post('/')
async def add_service(
    name: str = Body(...),
    duration: int = Body(...),
    price: int = Body(...),
    description: str = Body(None)
):
    """Создает новую услугу."""
    service = await create_service(
        name=name,
        duration=duration,
        price=price,
        description=description
    )

    if not service:
        return {'success': False, 'message': 'Услуга с таким именем уже есть'}

    return {'success': True, 'id': service.id}


@router.put('/{service_id}')
async def edit_service(
    service_id: int,
    name: str = Body(None),
    duration: int = Body(None),
    price: int = Body(None),
    description: str = Body(None)
):
    """Обновляет услугу."""
    service = await update_service(
        service_id=service_id,
        name=name,
        duration=duration,
        price=price,
        description=description
    )

    if not service:
        return {'success': False, 'message': 'Услуга не найдена'}

    return {'success': True}


@router.post('/{service_id}/toggle')
async def toggle_service(service_id: int):
    """Переключает активность услуги."""
    service = await toggle_service_active(service_id)

    if not service:
        return {'success': False, 'message': 'Услуга не найдена'}

    return {'success': True, 'is_active': service.is_active}


@router.delete('/{service_id}')
async def remove_service(service_id: int):
    """Удаляет услугу."""
    success = await delete_service(service_id)

    if not success:
        return {
            'success': False,
            'message': 'Услуга не найдена или на нее есть записи',
        }

    return {'success': True}
