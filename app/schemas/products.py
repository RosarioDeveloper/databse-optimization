from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class ProductCreate(BaseModel):
    name: str
    description: str
    price: Decimal = Field(ge=0)


class ProductResponse(BaseModel):
    id: int
    name: str
    description: str
    price: Decimal
    created_at: datetime
