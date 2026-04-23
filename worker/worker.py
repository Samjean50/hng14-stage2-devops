import redis
import time
import os
import signal
import sys

r = redis.Redis(
    host=os.getenv("REDIS_HOST", "redis"),
    port=int(os.getenv("REDIS_PORT", 6379))
)


def shutdown(signum, frame):
    print("Shutting down worker gracefully")
    sys.exit(0)


signal.signal(signal.SIGTERM, shutdown)
signal.signal(signal.SIGINT, shutdown)


def process_job(job_id):
    print(f"Processing job {job_id}")
    time.sleep(2)
    r.hset(f"job:{job_id}", "status", "completed")
    print(f"Done: {job_id}")


while True:
    job = r.brpop("job", timeout=5)
    if job:
        _, job_id = job
        try:
            process_job(job_id.decode())
        except Exception as e:
            print(f"Error processing job {job_id}: {e}")
            r.hset(f"job:{job_id.decode()}", "status", "failed")
