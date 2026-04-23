import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from main import app

client = TestClient(app)


# Test 1 — health endpoint returns 200 and correct body
def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"message": "healthy"}


# Test 2 — POST /jobs creates a job and returns a job_id
# Redis is mocked — test does not need a real Redis connection
@patch("main.r")
def test_create_job(mock_redis):
    mock_redis.lpush = MagicMock(return_value=1)
    mock_redis.hset = MagicMock(return_value=1)

    response = client.post("/jobs")
    assert response.status_code == 200
    data = response.json()
    assert "job_id" in data
    assert len(data["job_id"]) == 36  # UUID is always 36 chars


# Test 3 — GET /jobs/{id} returns status when job exists
@patch("main.r")
def test_get_job_status_found(mock_redis):
    mock_redis.hget = MagicMock(return_value=b"queued")

    response = client.get("/jobs/test-id-123")
    assert response.status_code == 200
    data = response.json()
    assert data["job_id"] == "test-id-123"
    assert data["status"] == "queued"


# Test 4 — GET /jobs/{id} returns 404 when job does not exist
@patch("main.r")
def test_get_job_status_not_found(mock_redis):
    mock_redis.hget = MagicMock(return_value=None)

    response = client.get("/jobs/nonexistent-id")
    assert response.status_code == 404
    assert "error" in response.json()


# Test 5 — POST /jobs calls Redis lpush and hset exactly once each
@patch("main.r")
def test_create_job_calls_redis(mock_redis):
    mock_redis.lpush = MagicMock(return_value=1)
    mock_redis.hset = MagicMock(return_value=1)

    client.post("/jobs")

    mock_redis.lpush.assert_called_once()
    mock_redis.hset.assert_called_once()
    # Verify it pushed to the correct queue name
    args = mock_redis.lpush.call_args[0]
    assert args[0] == "job"
