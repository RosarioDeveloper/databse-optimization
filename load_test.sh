#!/usr/bin/env bash
set -u

BASE_URL="${BASE_URL:-http://localhost:8000}"
CONNECTIONS="${CONNECTIONS:-2000}"
DURATION="${DURATION:-30}"
PIPELINING="${PIPELINING:-1}"
REQUESTS_PER_SECOND="${REQUESTS_PER_SECOND:-1000}"

SCENARIOS=(
  # "users-list|/users?limit=100&offset=0"
  # "products-list|/products?limit=100&offset=0"
  # "orders-list|/orders?limit=100&offset=0"
  "transactions-list|/transactions?limit=100&offset=0"
  "user-orders|/users/1/orders?limit=100&offset=0"
  "order-items|/orders/1/items"
)

if ! command -v autocannon >/dev/null 2>&1; then
  printf 'autocannon is required. Install it globally with:\n\n'
  printf '  npm install -g autocannon\n'
  exit 1
fi

if ! command -v curl >/dev/null 2>&1; then
  printf 'curl is required to check application health before the load test.\n'
  exit 1
fi

if ! [[ "$CONNECTIONS" =~ ^[0-9]+$ ]] || [ "$CONNECTIONS" -lt 1 ]; then
  printf 'CONNECTIONS must be a positive integer. Current value: %s\n' "$CONNECTIONS"
  exit 1
fi

if ! [[ "$DURATION" =~ ^[0-9]+$ ]] || [ "$DURATION" -lt 1 ]; then
  printf 'DURATION must be a positive integer. Current value: %s\n' "$DURATION"
  exit 1
fi

if ! [[ "$PIPELINING" =~ ^[0-9]+$ ]] || [ "$PIPELINING" -lt 1 ]; then
  printf 'PIPELINING must be a positive integer. Current value: %s\n' "$PIPELINING"
  exit 1
fi

if ! [[ "$REQUESTS_PER_SECOND" =~ ^[0-9]+$ ]] || [ "$REQUESTS_PER_SECOND" -lt 1 ]; then
  printf 'REQUESTS_PER_SECOND must be a positive integer. Current value: %s\n' "$REQUESTS_PER_SECOND"
  exit 1
fi

printf 'Checking API health at %s/health...\n' "$BASE_URL"
if ! curl --fail --silent --show-error "$BASE_URL/health" >/dev/null; then
  printf 'API is not reachable. Start it first with `uv run dev` or Docker Compose.\n'
  exit 1
fi

scenario_count="${#SCENARIOS[@]}"
base_connections=$((CONNECTIONS / scenario_count))
remaining_connections=$((CONNECTIONS % scenario_count))
base_requests_per_second=$((REQUESTS_PER_SECOND / scenario_count))
remaining_requests_per_second=$((REQUESTS_PER_SECOND % scenario_count))

if [ "$base_connections" -lt 1 ]; then
  printf 'CONNECTIONS must be at least the number of scenarios (%s). Current value: %s\n' "$scenario_count" "$CONNECTIONS"
  exit 1
fi

if [ "$base_requests_per_second" -lt 1 ]; then
  printf 'REQUESTS_PER_SECOND must be at least the number of scenarios (%s). Current value: %s\n' "$scenario_count" "$REQUESTS_PER_SECOND"
  exit 1
fi

log_dir="$(mktemp -d)"
pids=()
names=()
logs=()

cleanup() {
  for pid in "${pids[@]:-}"; do
    if kill -0 "$pid" >/dev/null 2>&1; then
      kill "$pid" >/dev/null 2>&1 || true
    fi
  done
  rm -rf "$log_dir"
}
trap cleanup INT TERM EXIT

printf '\nStarting concurrent load test\n'
printf 'Base URL: %s\n' "$BASE_URL"
printf 'Total connections: %s\n' "$CONNECTIONS"
printf 'Duration: %ss\n' "$DURATION"
printf 'Pipelining: %s\n' "$PIPELINING"
printf 'Requests per second: %s\n\n' "$REQUESTS_PER_SECOND"

for index in "${!SCENARIOS[@]}"; do
  scenario="${SCENARIOS[$index]}"
  name="${scenario%%|*}"
  path="${scenario#*|}"
  scenario_connections="$base_connections"
  scenario_requests_per_second="$base_requests_per_second"

  if [ "$index" -lt "$remaining_connections" ]; then
    scenario_connections=$((scenario_connections + 1))
  fi

  if [ "$index" -lt "$remaining_requests_per_second" ]; then
    scenario_requests_per_second=$((scenario_requests_per_second + 1))
  fi

  log_file="$log_dir/$name.log"
  url="$BASE_URL$path"

  printf 'Running %-18s %4s connections  %4s req/s  %s\n' "$name" "$scenario_connections" "$scenario_requests_per_second" "$url"
  autocannon \
    --connections "$scenario_connections" \
    --duration "$DURATION" \
    --pipelining "$PIPELINING" \
    --overallRate "$scenario_requests_per_second" \
    "$url" >"$log_file" 2>&1 &

  pids+=("$!")
  names+=("$name")
  logs+=("$log_file")
done

status=0
for index in "${!pids[@]}"; do
  if ! wait "${pids[$index]}"; then
    printf '\nScenario failed: %s\n' "${names[$index]}"
    status=1
  fi
done

printf '\nLoad test results\n'
for index in "${!logs[@]}"; do
  printf '\n--- %s ---\n' "${names[$index]}"
  sed 's/^/  /' "${logs[$index]}"
done

exit "$status"
