# backend/tests/test_endpoints.py
import pytest
from fastapi.testclient import TestClient
from ..main import app

client = TestClient(app)

@pytest.mark.parametrize("endpoint, expected_status, expected_response", [
    ("/", 200, {"message": "Welcome to the Chess LLM Backend"}),
    ("/invalid", 404, {"detail": "Not Found"}),  # Example invalid endpoint
])
def test_endpoints(endpoint, expected_status, expected_response):
    response = client.get(endpoint)
    assert response.status_code == expected_status
    assert response.json() == expected_response

def test_home_endpoint_headers():
    response = client.get("/")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
