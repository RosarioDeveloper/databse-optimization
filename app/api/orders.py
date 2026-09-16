from decimal import Decimal

from cashews import cache
from fastapi import APIRouter, HTTPException, Query, status

from app import config
from app.base_repository import BaseRepository
from app.schemas.orders import OrderCreate, OrderItemResponse, OrderResponse

router = APIRouter(prefix="/orders", tags=["orders"])
repository = BaseRepository()


@router.get("", response_model=list[OrderResponse])
@cache(ttl=config.CACHE_TTL)
async def list_orders(
    limit: int = Query(50, ge=1, le=500), offset: int = Query(0, ge=0)
):
    print("entrei")

    from app.logger import logger

    logger.info("hellow word")
    return await repository.query(
        """
        SELECT id, user_id, status, total_amount, created_at
        FROM orders
        ORDER BY id
        LIMIT %s OFFSET %s
        """,
        (limit, offset),
    )


@router.get("/{order_id}", response_model=OrderResponse)
@cache(ttl=config.CACHE_TTL)
async def get_order(order_id: int):
    rows = await repository.query(
        """
        SELECT id, user_id, status, total_amount, created_at
        FROM orders
        WHERE id = %s
        """,
        (order_id,),
    )
    if not rows:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Order not found"
        )
    return rows[0]


@router.get("/{order_id}/items", response_model=list[OrderItemResponse])
@cache(ttl=config.CACHE_TTL)
async def list_order_items(order_id: int):
    return await repository.query(
        """
        SELECT id, order_id, product_id, quantity, unit_price, created_at
        FROM order_items
        WHERE order_id = %s
        ORDER BY id
        """,
        (order_id,),
    )


@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
@cache(ttl=config.CACHE_TTL)
async def create_order(order: OrderCreate):
    if not order.items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Order must contain items"
        )

    user_rows = await repository.query(
        "SELECT id FROM users WHERE id = %s", (order.user_id,)
    )
    if not user_rows:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    total_amount = Decimal("0.00")
    priced_items = []
    for item in order.items:
        product_rows = await repository.query(
            """
            SELECT id, price
            FROM products
            WHERE id = %s
            """,
            (item.product_id,),
        )
        if not product_rows:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
            )
        unit_price = product_rows[0]["price"]
        total_amount += unit_price * item.quantity
        priced_items.append((item.product_id, item.quantity, unit_price))

    order_rows = await repository.query(
        """--sql
        INSERT INTO orders (user_id, status, total_amount)
        VALUES (%s, %s, %s)
        RETURNING id, user_id, status, total_amount, created_at
        """,
        (order.user_id, "pending", total_amount),
    )
    created_order = order_rows[0]  # type: ignore

    for product_id, quantity, unit_price in priced_items:
        await repository.query(
            """
            INSERT INTO order_items (order_id, product_id, quantity, unit_price)
            VALUES (%s, %s, %s, %s)
            """,
            (created_order["id"], product_id, quantity, unit_price),
        )

    return created_order
