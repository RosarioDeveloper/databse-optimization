from typing import Any

from psycopg.abc import QueryNoTemplate
from psycopg.rows import dict_row
from psycopg_pool import PoolTimeout

from app.database import pool
from app.logger import logger


class BaseRepository:
    async def query(self, sql: QueryNoTemplate, params: tuple[Any, ...] | None = None):
        try:
            async with pool.connection() as conn, conn.cursor(
                row_factory=dict_row
            ) as cursor:
                await cursor.execute(sql, params)
                if cursor.description is None:
                    return []

                return await cursor.fetchall()
        except PoolTimeout:
            logger.exception("Database connection pool timeout")
            raise
