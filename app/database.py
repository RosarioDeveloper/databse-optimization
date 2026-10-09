from psycopg_pool import AsyncConnectionPool

from app import config
from app.config import DATABASE_URL

pool = AsyncConnectionPool(
    conninfo=DATABASE_URL,
    min_size=4,
    max_size=config.MAX_POOL_SIZE,
    open=False,
)
