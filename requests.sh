
#!/usr/bin/env bash
set -u

# autocannon -c 10 -d 5 http://localhost:8000/orders

seq 5 | xargs -I{} -P 5 curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8000/health