from fastapi import APIRouter, Depends, HTTPException, status, Form, Request, Header
from typing import Dict, Any, List
from urllib.parse import urlencode

from fastapi.responses import RedirectResponse
from API.dependencies import get_canvas_service
from API.Service.canvas_service import CanvasService
from Metrics.metrics import MetricsRoute
import jwt
import uuid

router = APIRouter(tags=["Canvas LTI"], route_class=MetricsRoute)


@router.get("/.well-known/jwks.json", summary="Publish JWKs for Canvas LTI")
def jwks(service: CanvasService = Depends(get_canvas_service)) -> Dict[str, Any]:
    """Return a JSON Web Key Set containing the public RSA key."""
    try:
        return service.public_jwk()
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Public key not found for JWKS")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/lti/login", summary="LTI OIDC Login")
async def lti_login(iss: str = Form(...),
    login_hint: str = Form(...),
    target_link_uri: str = Form(...),
    client_id: str = Form(...),
    lti_deployment_id: str = Form(...),
    lti_message_hint: str = Form(None),
    canvas_environment: str = Form(None),
    canvas_region: str = Form(None),
    lti_storage_target: str = Form(None),):
    """Canvas calls this first. We must redirect back to Canvas OIDC auth endpoint."""

    if not all([iss, login_hint, target_link_uri, client_id]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing required OIDC parameters"
        )

    query_params = {
        "response_type": "id_token",
        "client_id": client_id,
        "redirect_uri": target_link_uri,
        "login_hint": login_hint,
        "response_mode": "form_post",
        "scope": "openid",
        "nonce": str(uuid.uuid4()),
        "state": str(uuid.uuid4()),
        "prompt": "none", 
    }

    # Optional LTI params to include only if present
    if lti_message_hint:
        query_params["lti_message_hint"] = lti_message_hint
    if canvas_environment:
        query_params["canvas_environment"] = canvas_environment
    if canvas_region:
        query_params["canvas_region"] = canvas_region
    if lti_storage_target:
        query_params["lti_storage_target"] = lti_storage_target

    redirect_url = f"{iss}/api/lti/authorize_redirect?{urlencode(query_params)}"
    return RedirectResponse(url=redirect_url, status_code=status.HTTP_302_FOUND)


@router.post("/lti/launch", name="lti_launch", summary="LTI Launch endpoint")
async def lti_launch(
    id_token: str = Form(...),
    service: CanvasService = Depends(get_canvas_service),
) -> Dict[str, Any]:
    """Accept an LTI launch (form POST) and return a signed token for the consumer."""
    try:
        print("Received LTI launch with id_token:", id_token[:30] + "...")
        decoded = jwt.decode(id_token, options={"verify_signature": False})

        user_id = decoded.get("sub")

        context = decoded.get("https://purl.imsglobal.org/spec/lti/claim/context", {})
        course_id = context.get("id")

        roles = decoded.get("https://purl.imsglobal.org/spec/lti/claim/roles", [])

        return {
            "user_id": user_id,
            "course_id": course_id,
            "roles": roles,
            "message": "LTI launch successful (signature not yet verified)"
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"LTI launch failed: {e}")

@router.get("/canvas/files", summary="List Canvas files (ingestion helper)")
def canvas_files(
    authorization: str | None = Header(default=None),
    service: CanvasService = Depends(get_canvas_service),
) -> List[Dict[str, Any]]:
    """Return a list of files fetched from Canvas or placeholder result.

    If an Authorization header is present, it will be passed (not validated) to the fetch helper.
    """
    try:
        token = None
        if authorization:
            if authorization.lower().startswith("bearer "):
                token = authorization.split(" ", 1)[1]
            else:
                token = authorization
        files = service.fetch_canvas_files(canvas_token=token)
        return files
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

