from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class TransactionResponse(BaseModel):
    id: int
    user_id: int
    order_id: int
    amount: Decimal
    transaction_type: str
    status: str
    created_at: datetime
