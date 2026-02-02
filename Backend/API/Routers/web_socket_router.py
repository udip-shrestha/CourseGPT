from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from Metrics.metrics import MetricsRoute


router = APIRouter(tags=["WebSocket UI"], route_class=MetricsRoute)


templates = Jinja2Templates(directory="API/Templates")


@router.get("/ws")
def websocket_test_page(request: Request):
    """
    Serves the websocket.html test UI.
    """
    return templates.TemplateResponse(request, "websocket.html")
