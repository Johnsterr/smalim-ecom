from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.products import Product as ProductModel
from app.models.users import User as UserModel
from app.models.reviews import Review as ReviewModel
from app.schemas import Review as ReviewSchema, ReviewCreate
from app.db_depends import get_async_db
from app.auth import get_current_admin, get_current_user
from app.services.review_service import update_product_rating


# Создаём маршрутизатор для отзывов
router = APIRouter(
    prefix="/reviews",
    tags=["reviews"],
)


@router.get("/", response_model=list[ReviewSchema])
async def get_all_reviews(
    db: AsyncSession = Depends(get_async_db)
):
    """
    Получение всех активных отзывов.
    """
    stmt = select(ReviewModel).where(ReviewModel.is_active == True)
    result = await db.scalars(stmt)
    reviews = result.all()
    return reviews


@router.post("/", response_model=ReviewSchema, status_code=status.HTTP_201_CREATED)
async def create_review(
    review: ReviewCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Создание нового отзыва.
    """
    # Проверяем, что пользователь имеет роль buyer
    if current_user.role != "buyer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only buyers can create reviews"
        )

    # Проверяем, существует ли товар и активен ли он
    stmt = select(ProductModel).where(ProductModel.id == review.product_id,
                                      ProductModel.is_active == True)
    product_result = await db.scalars(stmt)
    product = product_result.first()
    if not product:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Product not found or inactive")

    # Проверяем, не оставлял ли пользователь уже отзыв на этот товар
    existing_review_stmt = select(ReviewModel).where(
        ReviewModel.user_id == current_user.id,
        ReviewModel.product_id == review.product_id,
        ReviewModel.is_active == True
    )
    existing_review_result = await db.scalars(existing_review_stmt)
    existing_review = existing_review_result.first()

    if existing_review:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="You have already reviewed this product")

    # Проверяем, что оценка в пределах допустимого диапазона
    if not 1 <= review.grade <= 5:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                            detail="Grade must be between 1 and 5")

    # Создаем новый отзыв
    db_review = ReviewModel(
        user_id=current_user.id,
        product_id=review.product_id,
        comment=review.comment,
        grade=review.grade,
        is_active=True,
        comment_date=datetime.now()
    )

    db.add(db_review)
    await db.commit()
    await db.refresh(db_review)
    # Пересчитываем средний рейтинг товара
    await update_product_rating(product.id, db)
    return db_review


@router.delete("/{review_id}", status_code=status.HTTP_200_OK)
async def delete_review(
    review_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: UserModel = Depends(get_current_admin)
):
    """
    Удаляет отзыв о товаре по его ID.
    """
    # Проверяем, существует ли активный отзыв
    stmt = select(ReviewModel).where(ReviewModel.id == review_id,
                                     ReviewModel.is_active == True)
    review_result = await db.scalars(stmt)
    review = review_result.first()
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Review not found or inactive")

    # Проверяем права доступа
    is_author = review.user_id == current_user.id
    is_admin = current_user.role == "admin"

    if not (is_author or is_admin):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You don't have permission to delete this review")

    product_id = review.product_id

    # Изменяем объект установив is_active=False и сохраняем
    review.is_active = False
    await db.commit()
    await db.refresh(review)
    # Пересчитываем рейтинг товара
    await update_product_rating(product_id, db)
    return {"message": "Review deleted"}
