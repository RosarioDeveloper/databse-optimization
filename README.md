# API Optimization

`api-optimization` is a simple asynchronous backend for studying PostgreSQL and API performance as relational data volume and request concurrency increase.

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

## Load Testing

Install `autocannon` globally:

```bash
npm install -g autocannon
```

Run a concurrent load test against the local API:

```bash
chmod +x load_test.sh
./load_test.sh
```

Configure the load with environment variables:

```bash
CONNECTIONS=5000 DURATION=60 BASE_URL=http://localhost:8000 ./load_test.sh
```

`CONNECTIONS` is the total number of concurrent connections split across all scenarios.

## Docker Compose

Create a local `.env` with the Grafana Cloud credentials used by the OpenTelemetry Collector:

```env
GRAFANA_CLOUD_OTLP_ENDPOINT=https://otlp-gateway-prod-eu-west-6.grafana.net/otlp
GRAFANA_CLOUD_INSTANCE_ID=
GRAFANA_CLOUD_API_KEY=
GRAFANA_CLOUD_BASIC_AUTH_HEADER="Basic <BASE64_INSTANCE_ID_API_KEY>"
```

Start the API, PostgreSQL, and OpenTelemetry Collector:

```bash
docker compose up --build
```

Swagger is available at:

```text
http://localhost:8000/docs
```

PostgreSQL uses persistent storage. On first initialization, Docker Compose mounts `database/schema.sql` into PostgreSQL's initialization directory so the schema is created automatically.

The API container starts through `uv run opentelemetry-instrument python -m app.main` and exports OTLP data to the local Collector at `http://otel-collector:4318`. The Collector forwards application telemetry and host metrics to Grafana Cloud.

## Project Structure

```text
api-optimization/
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
├── load_test.sh
├── Dockerfile
├── docker-compose.yml
├── otel-collector.yaml
├── pyproject.toml
├── uv.lock
├── .env.example
└── README.md
```

This baseline is intentionally simple so optimizations such as indexes, connection pooling, caching, and query rewrites can be added and benchmarked later.
