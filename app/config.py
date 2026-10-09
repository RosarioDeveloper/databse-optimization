import os

from dotenv import load_dotenv

load_dotenv()

CACHE_TTL = "60m"
WORKERS = 2
MAX_POOL_SIZE = 10
LATENCY = 500  # latency in seconds
# RPS = int((MAX_POOL_SIZE / LATENCY * 1000) * 0.8)
RPS = 1000 * 0.8


POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", "5432"))
POSTGRES_DB = os.getenv("POSTGRES_DB", "database_optimization")
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")

REDIS_URL = os.getenv("REDIS_URL", "memory://")

DATABASE_URL = (
    f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}"
    f"@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
)
