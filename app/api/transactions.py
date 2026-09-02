from fastapi import APIRouter, HTTPException, Query, status

from app.base_repository import BaseRepository
from app.schemas.transactions import TransactionResponse

router = APIRouter(prefix="/transactions", tags=["transactions"])
repository = BaseRepository()


@router.get("", response_model=list[TransactionResponse])
async def list_transactions(limit: int = Query(50, ge=1, le=500), offset: int = Query(0, ge=0)):
    return await repository.query(
        """
        SELECT id, user_id, order_id, amount, transaction_type, status, created_at
        FROM transactions
        ORDER BY id
        LIMIT %s OFFSET %s
        """,
        (limit, offset),
    )


@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(transaction_id: int):
    rows = await repository.query(
        """
        SELECT id, user_id, order_id, amount, transaction_type, status, created_at
        FROM transactions
        WHERE id = %s
        """,
        (transaction_id,),
    )
    if not rows:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    return rows[0]
