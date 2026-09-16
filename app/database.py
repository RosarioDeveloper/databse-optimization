from psycopg_pool import AsyncConnectionPool

from app.config import DATABASE_URL

pool = AsyncConnectionPool(
    conninfo=DATABASE_URL,
    min_size=4,
    max_size=40,
    open=False,
)
