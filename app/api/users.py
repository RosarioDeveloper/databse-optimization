from fastapi import APIRouter, HTTPException, Query, status

from app.base_repository import BaseRepository
from app.schemas.orders import OrderResponse
from app.schemas.transactions import TransactionResponse
from app.schemas.users import UserCreate, UserResponse

router = APIRouter(prefix="/users", tags=["users"])
repository = BaseRepository()


@router.get("", response_model=list[UserResponse])
async def list_users(limit: int = Query(50, ge=1, le=500), offset: int = Query(0, ge=0)):
    return await repository.query(
        """
        SELECT id, name, email, created_at
        FROM users
        ORDER BY id
        LIMIT %s OFFSET %s
        """,
        (limit, offset),
    )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int):
    rows = await repository.query(
        """
        SELECT id, name, email, created_at
        FROM users
        WHERE id = %s
        """,
        (user_id,),
    )
    if not rows:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return rows[0]


@router.get("/{user_id}/orders", response_model=list[OrderResponse])
async def list_user_orders(
    user_id: int,
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    return await repository.query(
        """
        SELECT id, user_id, status, total_amount, created_at
        FROM orders
        WHERE user_id = %s
        ORDER BY id
        LIMIT %s OFFSET %s
        """,
        (user_id, limit, offset),
    )


@router.get("/{user_id}/transactions", response_model=list[TransactionResponse])
async def list_user_transactions(
    user_id: int,
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    return await repository.query(
        """
        SELECT id, user_id, order_id, amount, transaction_type, status, created_at
        FROM transactions
        WHERE user_id = %s
        ORDER BY id
        LIMIT %s OFFSET %s
        """,
        (user_id, limit, offset),
    )


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate):
    rows = await repository.query(
        """
        INSERT INTO users (name, email)
        VALUES (%s, %s)
        RETURNING id, name, email, created_at
        """,
        (user.name, str(user.email)),
    )
    return rows[0]
