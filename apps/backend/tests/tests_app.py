from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_read_root():
    """
    Test that the root endpoint returns a 200 status code and
    the expected JSON message.
    """
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}