import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from API.Routers.web_socket_router import router as websocket_ui_router


@pytest.fixture
def client():
    app = FastAPI()
    app.include_router(websocket_ui_router)
    return TestClient(app)


def test_websocket_test_page_renders_template(client):
    response = client.get("/ws")

    # Status code
    assert response.status_code == 200

    # Ensure correct content type
    assert "text/html" in response.headers["content-type"]

    # HTML body check
    body = response.text.lower()
    assert "<html" in body or "<!doctype" in body

    # Optional: ensure Jinja2 template actually rendered something meaningful
    # Adjust this based on your websocket.html content
    assert "websocket" in body or "ws" in body
