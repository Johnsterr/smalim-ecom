from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from app.db_depends import get_async_db
from app.models.reviews import Review as ReviewModel
from app.models.products import Product as ProductModel


async def update_product_rating(product_id: int, db: AsyncSession = Depends(get_async_db)) -> None:
    """
    Пересчитывает средний рейтинг товара на основе всех активных отзывов.
    """
    # Рассчитываем среднюю оценку среди активных отзывов
    stmt = select(func.avg(ReviewModel.grade)).where(
        ReviewModel.product_id == product_id,
        ReviewModel.is_active == True
    )

    result = await db.execute(stmt)
    avg_rating = result.scalar() or 0.0

    # Находим товар и обновляем его рейтинг
    stmt = select(ProductModel).where(ProductModel.id == product_id)
    result = await db.scalars(stmt)
    product = result.first()

    if product:
        product.rating = avg_rating
        await db.commit()
