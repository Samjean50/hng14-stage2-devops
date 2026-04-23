from fastapi import FastAPI
from fastapi.responses import JSONResponse
import redis
import uuid
import os

app = FastAPI()

r = redis.Redis(
    host=os.getenv("REDIS_HOST", "redis"),
    port=int(os.getenv("REDIS_PORT", 6379))
)


@app.get("/health")
def health():
    return JSONResponse(content={"message": "healthy"}, status_code=200)


@app.post("/jobs")
def create_job():
    job_id = str(uuid.uuid4())
    r.lpush("job", job_id)
    r.hset(f"job:{job_id}", "status", "queued")
    return {"job_id": job_id}


@app.get("/jobs/{job_id}")
def get_job(job_id: str):
    status = r.hget(f"job:{job_id}", "status")
    if not status:
        return JSONResponse(
            content={"error": "not found"},
            status_code=404
        )
    return {"job_id": job_id, "status": status.decode()}
