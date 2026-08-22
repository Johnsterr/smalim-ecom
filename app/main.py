from fastapi import FastAPI

# Создаём приложение FastAPI
app = FastAPI(
    title="E-commerce API",
    version="0.0.1",
)


# Корневой эндпоинт для проверки
@app.get("/")
async def root():
    """
    Корневой маршрут, подтверждающий, что API работает.
    """
    return {"message": "Welcome to the E-commerce API!"}
