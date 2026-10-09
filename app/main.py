from contextlib import asynccontextmanager

import uvicorn
from cashews import cache
from fastapi import FastAPI
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from app import config
from app.api import orders, products, transactions, users
from app.base_repository import BaseRepository
from app.database import pool

repository = BaseRepository()

# Rate Limiter
limiter_config = Limiter(
    key_func=get_remote_address,
    default_limits=[f"{config.RPS}/second"],
    # application_limits=["900/second"],
    storage_uri=config.REDIS_URL,
    headers_enabled=True,
)


# Application
@asynccontextmanager
async def lifespan(app: FastAPI):
    cache.setup(config.REDIS_URL)
    await pool.open()
    await pool.wait()
    yield
    await pool.close()


app = FastAPI(
    title="API Optimization",
    lifespan=lifespan,
)


# Middlewares
app.state.limiter = limiter_config
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore
app.add_middleware(SlowAPIMiddleware)


# @app.middleware("http")
# async def http_intercept(
#     req: Request, call_next: Callable[[Request], Awaitable[Response]]
# ):
#     response = await call_next(req)
#     pool_stats = pool.get_stats()
#     print(f"Using {pool_stats['pool_size']}/{pool_stats['pool_max']} connections.")
#     print(f"Request waiting {pool_stats['requests_waiting']}/")

#     return response


# Routes
app.include_router(users.router)
app.include_router(products.router)
app.include_router(orders.router)
app.include_router(transactions.router)


@app.get("/health")
async def health():
    rows = await repository.query("SELECT 1 AS ok;")
    return {"status": "ok", "database": rows[0]["ok"] == 1}  # type: ignore


def run() -> None:
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )


if __name__ == "__main__":
    run()
