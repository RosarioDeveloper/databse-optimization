from fastapi import FastAPI
import uvicorn

from app.api import orders, products, transactions, users
from app.base_repository import BaseRepository

from opentelemetry.instrumentation import auto_instrumentation

auto_instrumentation.initialize()


app = FastAPI(title="Database Performance Lab")
repository = BaseRepository()


@app.get("/health")
async def health():
    rows = await repository.query("SELECT 1 AS ok;")
    return {"status": "ok", "database": rows[0]["ok"] == 1}


app.include_router(users.router)
app.include_router(products.router)
app.include_router(orders.router)
app.include_router(transactions.router)


uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False)
