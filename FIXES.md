# Bug Fixes

## Fix 1
- **File:** api/main.py
- **Line:** 5
- **Problem:** Redis host hardcoded as `localhost` — fails inside Docker where services
  communicate by service name, not localhost. The API container trying to connect to
  localhost:6379 finds nothing there and crashes on startup.
- **Fix:** Changed to `redis.Redis(host=os.getenv("REDIS_HOST", "redis"), port=int(os.getenv("REDIS_PORT", 6379)))`

## Fix 2
- **File:** api/main.py
- **Line:** 8 (missing)
- **Problem:** No `/health` endpoint — Docker HEALTHCHECK instruction and
  `depends_on: condition: service_healthy` in docker-compose both require a health
  endpoint to verify the container is ready. Without it the entire stack hangs on startup.
- **Fix:** Added `GET /health` returning `{"message": "healthy"}` with status 200

## Fix 3
- **File:** api/main.py
- **Line:** 16
- **Problem:** `GET /jobs/{id}` returns HTTP 200 even when the job does not exist.
  Returning 200 with an error body is incorrect — clients cannot distinguish between
  a successful response and a not-found response.
- **Fix:** Returns `JSONResponse` with `status_code=404` when `r.hget` returns None

## Fix 4
- **File:** api/requirements.txt
- **Line:** 1-3
- **Problem:** No version pins on any dependency. Unpinned packages pull the latest
  version on every image build, meaning a new release of fastapi, uvicorn, or redis
  could silently break the application between builds.
- **Fix:** Pinned all packages — `fastapi==0.115.0`, `uvicorn==0.32.0`, `redis==5.2.0`

## Fix 5
- **File:** worker/worker.py
- **Line:** 3
- **Problem:** Redis host hardcoded as `localhost` — same Docker networking failure
  as api/main.py. The worker container cannot reach Redis via localhost.
- **Fix:** Changed to `redis.Redis(host=os.getenv("REDIS_HOST", "redis"), port=int(os.getenv("REDIS_PORT", 6379)))`

## Fix 6
- **File:** worker/worker.py
- **Line:** 4 (imported but never used)
- **Problem:** `signal` module imported but no signal handlers registered. Docker
  sends SIGTERM when stopping a container — ignoring it causes Docker to wait 10
  seconds then send SIGKILL, which can kill the worker mid-job and leave a job
  permanently stuck in the `queued` state with no worker to process it.
- **Fix:** Added `signal.signal(signal.SIGTERM, shutdown)` and
  `signal.signal(signal.SIGINT, shutdown)` with a clean exit handler

## Fix 7
- **File:** worker/worker.py
- **Line:** 13-15
- **Problem:** No error handling around `process_job`. Any unhandled exception
  crashes the entire worker process permanently. The job is already popped off
  the Redis queue so it is lost — no retry, no status update, silent failure.
- **Fix:** Wrapped `process_job` call in try/except. On exception, sets job
  status to `failed` in Redis so the frontend can display the correct state

## Fix 8
- **File:** worker/requirements.txt
- **Line:** 1
- **Problem:** No version pin on the redis package — same unpinned dependency
  risk as the API requirements file.
- **Fix:** Pinned to `redis==5.2.0`

## Fix 9
- **File:** frontend/app.js
- **Line:** 4
- **Problem:** API URL hardcoded as `http://localhost:8000`. The frontend container
  cannot reach the API container via localhost — localhost inside the frontend
  container refers to the frontend container itself, not the API.
- **Fix:** Changed to `process.env.API_URL || "http://api:8000"` — reads from
  environment variable with a sensible default using the Docker service name

## Fix 10
- **File:** frontend/app.js
- **Line:** missing
- **Problem:** No `/health` endpoint on the frontend — Docker HEALTHCHECK and
  `depends_on: condition: service_healthy` both fail without a health route.
- **Fix:** Added `GET /health` returning `{"message": "healthy"}`

## Fix 11
- **File:** frontend/views/index.html
- **Line:** 36
- **Problem:** Job polling only stops when status equals `completed`. If a job
  enters a `failed` state the browser polls the status endpoint forever, creating
  an infinite request loop.
- **Fix:** Added `failed` as a second terminal condition —
  `if (data.status !== 'completed' && data.status !== 'failed')`

## Fix 12
- **File:** frontend/package.json
- **Line:** missing file
- **Problem:** No `package-lock.json` in the repository. The Dockerfile uses
  `npm ci` which requires a lockfile to guarantee reproducible installs. Without
  it the build fails with `EUSAGE` error.
- **Fix:** Generated `package-lock.json` by running `npm install` locally and
  committed it to the repository

## Fix 13
- **File:** frontend/Dockerfile
- **Line:** 4
- **Problem:** `npm ci --only=production` flag is deprecated in npm v9+ and
  causes a warning that can break strict CI environments.
- **Fix:** Changed to `npm ci --omit=dev` which is the current supported flag

## Fix 14
- **File:** api/Dockerfile and worker/Dockerfile
- **Line:** 4 (builder stage pip install)
- **Problem:** `pip install --user` in the builder stage installs packages to
  `/root/.local`. When copied to the final image and run as a non-root user,
  the PATH does not include `/root/.local/bin`, causing `ModuleNotFoundError`
  for uvicorn and other packages at runtime.
- **Fix:** Changed to `pip install --prefix=/install` and
  `COPY --from=builder /install /usr/local` — packages land in the standard
  system Python path and are accessible regardless of which user runs the process

## Fix 15
- **File:** api/Dockerfile and worker/Dockerfile
- **Line:** 1
- **Problem:** `python:3.11-slim` base image (Debian 13) contains CRITICAL
  severity CVEs with available fixes, causing Trivy security scan to fail
  the pipeline.
- **Fix:** Upgraded base image to `python:3.12-alpine` — Alpine Linux has a
  significantly smaller attack surface and no fixable CRITICAL CVEs

## Fix 16
- **File:** frontend/Dockerfile
- **Line:** 1
- **Problem:** `node:18-alpine` uses Alpine 3.21 which contains CRITICAL
  severity CVEs in Node.js packages, causing Trivy security scan to fail.
- **Fix:** Upgraded to `node:20-alpine` which uses Alpine 3.22+ with patched
  packages and no fixable CRITICAL CVEs

## Fix 17
- **File:** docker-compose.yml
- **Line:** 1
- **Problem:** `version: "3.9"` attribute is obsolete in Docker Compose v2+
  and generates a warning that can cause confusion and noise in CI logs.
- **Fix:** Removed the version field entirely
