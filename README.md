# Database Performance Lab

`database-performance-lab` is a simple asynchronous backend for studying PostgreSQL and API performance as relational data volume and request concurrency increase.

The goal is a clean baseline, not an optimized system. This project is designed to make scenarios observable, such as: the SQL query did not change, but its performance degraded as the dataset grew.

## Stack

- Python 3.14+
- FastAPI
- PostgreSQL
- psycopg 3 async API
- Pydantic
- uv
- Docker and Docker Compose
- Pytest

## Architecture

The application uses `async def` FastAPI endpoints and asynchronous PostgreSQL operations through `psycopg.AsyncConnection`. There is no ORM, no migration framework, no connection pool, and no caching layer.

Raw SQL remains directly visible in `app/api/*.py` because SQL behavior is the central subject of the performance experiments.

## Local Setup

Install dependencies:

```bash
uv sync
```

Run the development server:

```bash
uv run dev
```

Seed the database:

```bash
uv run seed
```

Run tests:

```bash
uv run test
```

## Docker Compose

Start the API and PostgreSQL:

```bash
docker compose up --build
```

Swagger is available at:

```text
http://localhost:8000/docs
```

PostgreSQL uses persistent storage. On first initialization, Docker Compose mounts `database/schema.sql` into PostgreSQL's initialization directory so the schema is created automatically.

## Project Structure

```text
database-performance-lab/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── base_repository.py
│   ├── api/
│   └── schemas/
├── database/
│   └── schema.sql
├── scripts/
│   └── seed.py
├── tests/
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── uv.lock
├── .env.example
└── README.md
```

This baseline is intentionally simple so optimizations such as indexes, connection pooling, caching, and query rewrites can be added and benchmarked later.
