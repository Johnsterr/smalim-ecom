from fastapi import Depends, FastAPI

from app.routers import categories, products
from app.config import Settings, get_settings

# Создаём приложение FastAPI
app = FastAPI(
    title="E-commerce API",
    version="0.0.1",
)

# Подключаем маршруты категорий и товаров
app.include_router(categories.router)
app.include_router(products.router)


# Корневой эндпоинт для проверки
@app.get("/")
async def root():
    """
    Корневой маршрут, подтверждающий, что API работает.
    """
    return {"message": "Welcome to the E-commerce API!"}


@app.get("/settings")
async def get_app_settings(settings: Settings = Depends(get_settings)):
    """
    Возвращает текущие настройки приложения.
    """
    return {
        "app_name": settings.APP_NAME,
        "postgres_host": settings.POSTGRES_HOST,
        "postgres_port": settings.POSTGRES_PORT,
        "postgres_db": settings.POSTGRES_DB,
        "postgres_user": settings.POSTGRES_USER,
        "database_url": settings.database_url,
    }
