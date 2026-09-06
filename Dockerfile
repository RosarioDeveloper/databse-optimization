FROM ghcr.io/astral-sh/uv:python3.14-bookworm

WORKDIR /app

COPY pyproject.toml uv.lock* README.md ./
COPY app ./app
COPY scripts ./scripts

RUN uv sync --frozen --no-dev || uv sync --no-dev

COPY . .

EXPOSE 8000

CMD ["uv", "run", "dev"]
