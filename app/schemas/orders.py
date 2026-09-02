from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field



class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)


class OrderCreate(BaseModel):
    user_id: int
    items: list[OrderItemCreate]


class OrderResponse(BaseModel):
    id: int
    user_id: int
    status: str
    total_amount: Decimal
    created_at: datetime


class OrderItemResponse(BaseModel):
    id: int
    order_id: int
    product_id: int
    quantity: int
    unit_price: Decimal
    created_at: datetime
