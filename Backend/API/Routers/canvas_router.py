from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, status, Form, Request, Header, Path
from typing import Dict, Any, List
from urllib.parse import urlencode

from fastapi.responses import RedirectResponse
from API.dependencies import get_canvas_service, get_course_service, get_student_service
from API.Service.canvas_service import CanvasService
from API.Service.courses_service import CourseService
from API.Service.students_service import StudentService
from Metrics.metrics import MetricsRoute
import os
import jwt
import uuid

load_dotenv()

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
    canvas_service: CanvasService = Depends(get_canvas_service),
    course_service: CourseService = Depends(get_course_service),
    student_service: StudentService = Depends(get_student_service),
) -> RedirectResponse:
    """Handle an LTI launch and redirect the user appropriately.

    Uses Canvas and application services to determine whether the user is a
    student or instructor and whether corresponding records already exist.  The
    frontend base URL is read from `FRONTEND_BASE_URL` env var (defaults to
    static).  Redirects include query parameters indicating role or registration
    requirements.
    """
    try:
        decoded = jwt.decode(id_token, options={"verify_signature": False})

        canvas_user_id = decoded.get("sub")
        context = decoded.get("https://purl.imsglobal.org/spec/lti/claim/context", {})
        canvas_context_id = context.get("id")
        roles = decoded.get("https://purl.imsglobal.org/spec/lti/claim/roles", [])
        custom = decoded.get("https://purl.imsglobal.org/spec/lti/claim/custom", {})
        canvas_course_id = custom.get("canvas_course_id")

        base_url = os.getenv("FRONTEND_BASE_URL")

        # resolve internal course if linked
        try:
            course = course_service.get_course_by_canvas_id(canvas_course_id)
            internal_id = course.get("id")
        except HTTPException:
            internal_id = None

        is_instructor = any("Instructor" in r for r in roles)

        if is_instructor:
            if internal_id:
                return canvas_service.redirect_to(base_url, f"/courses/{internal_id}")
            else:
                return canvas_service.redirect_to(base_url, f"/register-course?canvas_context_id={canvas_context_id}&canvas_course_id={canvas_course_id}")

        # student flows
        if not internal_id:
            return canvas_service.redirect_to(base_url, f"/?error=course_not_linked")

        student_rec = student_service.find_student_in_course_by_canvas(canvas_user_id, internal_id)
        if student_rec:
            return canvas_service.redirect_to(base_url, f"/courses/{internal_id}/chats?role=student")
        else:
            return canvas_service.redirect_to(base_url,
                f"/courses/{internal_id}/chats?role=student&needs_registration=1&canvas_user_id={canvas_user_id}"
            )

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
    
@router.get(
    "/courses/{course_id}/canvas/modules",
    status_code=status.HTTP_200_OK,
    summary="Retrieve Canvas modules for a course",
)
async def get_canvas_modules(
    course_id: str = Path(..., description="CourseGPT course ID"),
    course_service: CourseService = Depends(get_course_service),
    service: CanvasService = Depends(get_canvas_service),
):
    course = course_service.read_course(course_id)
    canvas_course_id = course.get("canvas_course_id")

    if not canvas_course_id:
        raise HTTPException(
            status_code=400,
            detail="Course is not linked to Canvas"
        )

    canvas_token = os.getenv("CANVAS_API")

    return await service.get_canvas_modules(canvas_course_id, canvas_token)

