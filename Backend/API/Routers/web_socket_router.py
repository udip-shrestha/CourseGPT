from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates


router = APIRouter(tags=["WebSocket UI"])


templates = Jinja2Templates(directory="API/Templates")


@router.get("/ws")
def websocket_test_page(request: Request):
    """
    Serves the websocket.html test UI.
    """
    return templates.TemplateResponse(request, "websocket.html")
