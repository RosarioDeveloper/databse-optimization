#!/usr/bin/env bash

set -a
source .env
set +a


AUTH=$(printf '%s' "1816556:${GRAFANA_TOKEN}" | base64 | tr -d '\n')

export OTEL_EXPORTER_OTLP_HEADERS="Authorization=Basic%20${AUTH}"

uv run opentelemetry-instrument python -m app.main