from cashews import cache
from fastapi import APIRouter, HTTPException, Query, status

from app import config
from app.base_repository import BaseRepository
from app.schemas.products import ProductCreate, ProductResponse

router = APIRouter(prefix="/products", tags=["products"])
repository = BaseRepository()


@router.get("", response_model=list[ProductResponse])
@cache(ttl=config.CACHE_TTL)
async def list_products(
    limit: int = Query(50, ge=1, le=500), offset: int = Query(0, ge=0)
):
    return await repository.query(
        """
        SELECT id, name, description, price, created_at
        FROM products
        ORDER BY id
        LIMIT %s OFFSET %s
        """,
        (limit, offset),
    )


@router.get("/{product_id}", response_model=ProductResponse)
@cache(ttl=config.CACHE_TTL)
async def get_product(product_id: int):
    rows = await repository.query(
        """
        SELECT id, name, description, price, created_at
        FROM products
        WHERE id = %s
        """,
        (product_id,),
    )
    if not rows:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )
    return rows[0]


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
@cache(ttl=config.CACHE_TTL)
async def create_product(product: ProductCreate):
    rows = await repository.query(
        """
        INSERT INTO products (name, description, price)
        VALUES (%s, %s, %s)
        RETURNING id, name, description, price, created_at
        """,
        (product.name, product.description, product.price),
    )
    return rows[0]
