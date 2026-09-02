from typing import Any

from psycopg.abc import QueryNoTemplate

from app.database import get_connection


class BaseRepository:
    async def query(self, sql: QueryNoTemplate, params: tuple[Any, ...] | None = None):
        async with get_connection() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(sql, params)
                if cursor.description is None:
                    return []

                return await cursor.fetchall()
