from fastapi import APIRouter, Depends, HTTPException, status, Form, Request, Header
from typing import Dict, Any, List

from fastapi.responses import RedirectResponse
from API.dependencies import get_canvas_service
from API.Service.canvas_service import CanvasService
from Metrics.metrics import MetricsRoute
import jwt

router = APIRouter(route_class=MetricsRoute)


@router.get("/.well-known/jwks.json", summary="Publish JWKs for Canvas LTI")
def jwks(service: CanvasService = Depends(get_canvas_service)) -> Dict[str, Any]:
    """Return a JSON Web Key Set containing the public RSA key."""
    try:
        jwk = service.public_jwk()
        return {"keys": [jwk]}
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Public key not found for JWKS")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/lti/login", summary="LTI OIDC Login")
async def lti_login(request: Request):
    """Canvas calls this first. We must redirect back to Canvas OIDC auth endpoint."""
    params = request.query_params

    required = ["iss", "login_hint", "client_id", "target_link_uri"]
    for r in required:
        if r not in params:
            raise HTTPException(status_code=400, detail=f"Missing OIDC param: {r}")

    # Redirect back to Canvas with required params
    redirect_url = (
        f"{params['iss']}/api/lti/authorize_redirect?"
        f"response_type=id_token"
        f"&client_id={params['client_id']}"
        f"&redirect_uri={params['target_link_uri']}"
        f"&login_hint={params['login_hint']}"
        f"&response_mode=form_post"
        f"&scope=openid"
        f"&nonce=coursegptnonce"
    )

    return RedirectResponse(url=redirect_url)


@router.post("/lti/launch", name="lti_launch", summary="LTI Launch endpoint")
async def lti_launch(
    id_token: str = Form(...),
    service: CanvasService = Depends(get_canvas_service),
) -> Dict[str, Any]:
    """Accept an LTI launch (form POST) and return a signed token for the consumer."""
    try:
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

