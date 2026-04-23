
# Bug Fixes

## Fix 1
- **File:** api/main.py
- **Line:** 5
- **Problem:** Redis host hardcoded as `localhost` — fails inside Docker where services communicate by service name, not localhost
- **Fix:** Changed to `os.getenv("REDIS_HOST", "redis")`

## Fix 2
- **File:** api/main.py
- **Line:** 8 (missing)
- **Problem:** No `/health` endpoint — Docker HEALTHCHECK and `depends_on: condition: service_healthy` both fail without it
- **Fix:** Added `GET /health` returning `{"message": "healthy"}`

## Fix 3
- **File:** api/main.py
- **Line:** 16
- **Problem:** `GET /jobs/{id}` returns HTTP 200 even when job is not found — incorrect status code misleads clients
- **Fix:** Returns `JSONResponse` with `status_code=404` when job does not exist

## Fix 4
- **File:** api/requirements.txt
- **Line:** 1-3
- **Problem:** No version pins — unpinned dependencies pull latest on every build, risking silent breakage
- **Fix:** Pinned all packages to specific versions

## Fix 5
- **File:** worker/worker.py
- **Line:** 3
- **Problem:** Redis host hardcoded as `localhost` — same Docker networking failure as api/main.py
- **Fix:** Changed to `os.getenv("REDIS_HOST", "redis")`

## Fix 6
- **File:** worker/worker.py
- **Line:** 4 (imported but unused)
- **Problem:** `signal` imported but never used — no graceful shutdown handling. Docker sends SIGTERM on stop; ignoring it causes forceful SIGKILL after 10s, risking mid-job corruption
- **Fix:** Added SIGTERM and SIGINT handlers that exit cleanly

## Fix 7
- **File:** worker/worker.py
- **Line:** 13-15
- **Problem:** No error handling around `process_job` — any exception crashes the entire worker process permanently, leaving subsequent jobs unprocessed
- **Fix:** Wrapped in try/except, sets job status to `failed` on error

## Fix 8
- **File:** worker/requirements.txt
- **Line:** 1
- **Problem:** No version pin on redis package
- **Fix:** Pinned to `redis==5.0.4`

## Fix 9
- **File:** frontend/app.js
- **Line:** 4
- **Problem:** API URL hardcoded as `http://localhost:8000` — frontend container cannot reach API container via localhost
- **Fix:** Changed to `process.env.API_URL || "http://api:8000"`

## Fix 10
- **File:** frontend/app.js
- **Line:** missing
- **Problem:** No `/health` endpoint — Docker HEALTHCHECK fails
- **Fix:** Added `GET /health` returning `{"message": "healthy"}`

## Fix 11
- **File:** frontend/views/index.html
- **Line:** 36
- **Problem:** Polling only stops on `completed` status — if a job enters `failed` state the browser polls forever
- **Fix:** Added `failed` as a terminal condition to stop polling
