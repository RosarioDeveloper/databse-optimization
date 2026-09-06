Create a backend project called `api-optimization`.

The project is a simple laboratory for studying PostgreSQL and API performance with large relational datasets and high request concurrency.

Use:

- Python 3.14+
- FastAPI
- PostgreSQL
- psycopg 3 with async support
- Pydantic
- uv as the dependency manager
- Docker
- Docker Compose
- Pytest

The application must be asynchronous.

Use `async def` for API endpoints and asynchronous PostgreSQL operations.

Keep the project intentionally simple.

Do not implement performance optimizations. I will implement and benchmark the optimizations later.

## Main Goal

Build a baseline asynchronous API that works correctly with relational data.

Later, this project will be used to study:

- large datasets
- slow SQL queries
- execution plans
- indexes
- joins
- pagination
- N+1 problems
- connection pooling
- async concurrency
- database contention
- throughput
- p50 / p95 / p99 latency
- caching
- query optimization

Do not implement solutions for these problems now.

## Database

Do not use an ORM.

Do not use:

- SQLAlchemy
- Alembic
- Django ORM
- any ORM or migration framework

Use raw PostgreSQL SQL with `psycopg`.

Use the asynchronous psycopg API.

Do not introduce a connection pool yet.

Connection pooling will be implemented later as part of the performance experiments.

Create:

```text
database/schema.sql
```

This file must contain the complete database schema and act as the only database migration.

Docker Compose should automatically execute this schema when PostgreSQL is initialized for the first time.

## Database Schema

Create the following tables.

### users

- id
- name
- email
- created_at

### products

- id
- name
- description
- price
- created_at

### orders

- id
- user_id
- status
- total_amount
- created_at

Relationship:

```text
users 1:N orders
```

### order_items

- id
- order_id
- product_id
- quantity
- unit_price
- created_at

Relationships:

```text
orders 1:N order_items
products 1:N order_items
```

### payments

- id
- order_id
- amount
- status
- payment_method
- created_at

Relationship:

```text
orders 1:1 payments
```

### transactions

- id
- user_id
- order_id
- amount
- transaction_type
- status
- created_at

Use proper PostgreSQL:

- primary keys
- foreign keys
- constraints
- appropriate data types

Do not create manual performance indexes.

Only use indexes automatically created or required by primary keys and constraints.

## Async Database Connection

Create:

```text
app/database.py
```

This file should contain the PostgreSQL connection configuration.

Use environment variables for database configuration.

Use psycopg's asynchronous connection API.

For example, use:

```python
psycopg.AsyncConnection
```

Database operations must never block the FastAPI event loop using synchronous psycopg calls.

Do not use a connection pool yet.

Keep the connection lifecycle simple and explicit so connection pooling can later be introduced and benchmarked as a separate optimization.

## Base Repository

Create only:

```text
app/base_repository.py
```

Do not create repositories such as:

- UserRepository
- ProductRepository
- OrderRepository
- TransactionRepository

API modules must use `BaseRepository` directly.

Create a small `BaseRepository` class with access to the asynchronous PostgreSQL connection provider.

Its primary method should look approximately like:

```python
async def query(
    self,
    sql: str,
    params=None,
):
    ...
```

The method must:

1. receive raw SQL
2. optionally receive SQL parameters
3. execute the SQL asynchronously
4. await the database operation
5. return the result
6. correctly handle the connection lifecycle

Use proper parameter binding.

Never interpolate user-provided values directly into SQL strings.

Example:

```python
repository = BaseRepository()

user = await repository.query(
    """
    SELECT *
    FROM users
    WHERE id = %s
    """,
    (user_id,),
)
```

Keep `BaseRepository` extremely small.

Do not implement:

- query builders
- ORM-like abstractions
- Unit of Work
- entity-specific repositories
- generic models
- complex dependency injection
- connection pooling

Raw SQL must remain visible inside the API modules because SQL performance is the main subject of the project.

## Async API

All endpoints that perform database I/O must use:

```python
async def
```

Example:

```python
@router.get("/{user_id}")
async def get_user(user_id: int):
    result = await repository.query(
        """
        SELECT *
        FROM users
        WHERE id = %s
        """,
        (user_id,),
    )

    return result
```

Do not use synchronous database operations inside asynchronous routes.

## API Endpoints

### Users

```text
GET /users
GET /users/{user_id}
GET /users/{user_id}/orders
POST /users
```

### Products

```text
GET /products
GET /products/{product_id}
POST /products
```

### Orders

```text
GET /orders
GET /orders/{order_id}
GET /orders/{order_id}/items
POST /orders
```

### Transactions

```text
GET /transactions
GET /transactions/{transaction_id}
GET /users/{user_id}/transactions
```

### Health

```text
GET /health
```

The health endpoint must asynchronously verify that PostgreSQL is reachable using:

```sql
SELECT 1;
```

## Pagination

For list endpoints, use simple offset pagination:

```text
limit
offset
```

Example:

```text
GET /orders?limit=50&offset=0
```

Use raw SQL:

```sql
LIMIT %s OFFSET %s
```

Do not implement cursor or keyset pagination yet.

## Pydantic Schemas

Use Pydantic only for HTTP request and response validation.

Do not use Pydantic as a database abstraction.

## Project Structure

Use:

```text
api-optimization/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── base_repository.py
│   │
│   ├── api/
│   │   ├── users.py
│   │   ├── products.py
│   │   ├── orders.py
│   │   └── transactions.py
│   │
│   └── schemas/
│       ├── users.py
│       ├── products.py
│       ├── orders.py
│       └── transactions.py
│
├── database/
│   └── schema.sql
│
├── scripts/
│   └── seed.py
│
├── tests/
│
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── uv.lock
├── .env.example
├── .gitignore
└── README.md
```

The Python `schemas` directory contains only Pydantic request and response models.

The PostgreSQL schema lives only in:

```text
database/schema.sql
```

## Dependency Management

Use `uv`.

Configure dependencies and project metadata in:

```text
pyproject.toml
```

Target:

```text
Python >= 3.14
```

Do not use:

- requirements.txt
- Poetry
- Pipenv

Generate and include:

```text
uv.lock
```

## Project Scripts

Configure executable project scripts so the developer experience is:

```bash
uv sync
uv run dev
uv run seed
uv run test
```

### `uv run dev`

Starts the FastAPI development server with reload enabled.

### `uv run seed`

Runs:

```text
scripts/seed.py
```

### `uv run test`

Runs the unit tests with Pytest.

Use proper Python entry points/functions for these scripts rather than shell-specific hacks.

## Seed

Create:

```text
scripts/seed.py
```

The seed must also use asynchronous PostgreSQL operations.

Do not accept CLI arguments.

Define dataset sizes as constants at the top of the file.

For example:

```python
USERS_COUNT = ...
PRODUCTS_COUNT = ...
ORDERS_COUNT = ...
```

Choose values large enough to provide a useful initial performance dataset while remaining reasonable for local development.

Generate:

- users
- products
- orders
- order_items
- payments
- transactions

Use Faker where appropriate.

Maintain valid relationships between all generated records.

The goal is that:

```bash
uv run seed
```

creates enough relational data to immediately begin performance experiments.

If dataset size needs to change, only the constants inside `scripts/seed.py` should need to be modified.

Keep the seed readable.

Do not heavily optimize it.

## Docker Compose

Create only:

```text
api
postgres
```

Use a Python 3.14-compatible image for the API.

PostgreSQL must use persistent storage.

Mount:

```text
database/schema.sql
```

into PostgreSQL's initialization directory so the schema is automatically created when the database is initialized for the first time.

The API must communicate with PostgreSQL through the Docker Compose internal network.

The complete project must start with:

```bash
docker compose up --build
```

Swagger must be available at:

```text
http://localhost:8000/docs
```

## Tests

Use Pytest.

Support asynchronous code in tests where necessary.

Create only basic unit tests.

Do not create a large integration or end-to-end testing infrastructure.

Testing is not the main purpose of this repository.

## README

Create a concise README explaining:

1. project purpose
2. technology stack
3. asynchronous architecture
4. how to install dependencies with `uv`
5. how to run `uv run dev`
6. how to run `uv run seed`
7. how to run `uv run test`
8. how to start everything with Docker Compose
9. how `database/schema.sql` initializes PostgreSQL
10. how to access Swagger
11. project structure
12. that this is intentionally a baseline implementation

Explain that the central experiment is observing how the same application behaves as:

```text
data volume increases
+
request concurrency increases
```

The repository should eventually demonstrate scenarios such as:

```text
The SQL query did not change,
but its performance degraded as the dataset grew.
```

## Important Constraints

Do not use an ORM.

Do not use Alembic.

Do not create entity-specific repositories.

Do not move SQL queries away from API modules.

Do not use synchronous PostgreSQL calls.

Do not introduce connection pooling yet.

Do not add Redis.

Do not add Kafka.

Do not add RabbitMQ.

Do not add Elasticsearch.

Do not add Kubernetes.

Do not add a monitoring stack.

Do not implement caching.

Do not implement sharding.

Do not implement partitioning.

Do not implement read replicas.

Do not implement CQRS.

Do not implement event sourcing.

Do not implement microservices.

Do not introduce unnecessary architectural abstractions.

Do not perform premature optimization.

Prefer simple, explicit, asynchronous code.

Keep SQL queries directly visible inside the API modules.

The project must represent a clean, intentionally simple async baseline that I can progressively optimize, load test and benchmark myself.

Generate the complete project structure and implementation.
