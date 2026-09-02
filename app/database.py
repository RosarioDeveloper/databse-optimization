from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from psycopg import AsyncConnection
from psycopg.rows import DictRow, dict_row

from app.config import DATABASE_URL


@asynccontextmanager
async def get_connection() -> AsyncIterator[AsyncConnection[DictRow]]:
    conn = await AsyncConnection[DictRow].connect(DATABASE_URL, row_factory=dict_row)
    try:
        yield conn
        await conn.commit()
    except Exception:
        await conn.rollback()
        raise
    finally:
        await conn.close()
