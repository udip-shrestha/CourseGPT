from fastapi import APIRouter, Depends, Path, Query, status

from API.Service.admin_service import AdminService
from API.dependencies import get_admin_service, authorize_admin
from Metrics.metrics import MetricsRoute


router = APIRouter(tags=["Admin"], route_class=MetricsRoute)


@router.patch(
    "/admin/courses/{course_id}/status",
    status_code=status.HTTP_200_OK,
    summary="Enable or disable a course",
    description=(
        "**Action:** Updates whether a course is enabled or disabled.\n\n"
        "**Behavior:** If `enabled=true`, the course becomes visible through the "
        "`courses` view. If `enabled=false`, it becomes hidden from default course reads.\n\n"
        "**Returns:** A status payload with the course id and enabled state."
    ),
)
def update_course_status(
    course_id: str = Path(
        ...,
        description="UUID of the course to enable or disable.",
        examples={"example": "8b7e9f2a-d4a1-4e5c-94b9-3c6f4ab0e9cd"},
    ),
    enabled: bool = Query(
        ...,
        description="Whether the course should be enabled. Use `true` to enable or `false` to disable.",
        examples={"example": True},
    ),
    service: AdminService = Depends(get_admin_service),
    _auth=Depends(authorize_admin),
):
    return service.update_course_status(course_id, enabled)


@router.patch(
    "/admin/instructors/{instructor_id}/admin",
    status_code=status.HTTP_200_OK,
    summary="Grant or revoke admin role for an instructor",
    description=(
        "**Action:** Updates whether an instructor has the admin role.\n\n"
        "**Behavior:** If `is_admin=true`, the instructor is assigned the `ADMIN` role. "
        "If `is_admin=false`, the instructor is assigned the `INSTRUCTOR` role.\n\n"
        "**Returns:** A status payload with the instructor id and resulting role."
    ),
)
def update_instructor_admin(
    instructor_id: str = Path(
        ...,
        description="UUID of the instructor whose role should be updated.",
        examples={"example": "74f2e4ea-b1a0-4f4d-a3f7-0d3078f60d21"},
    ),
    is_admin: bool = Query(
        ...,    
        description="Whether the instructor should be an admin. Use `true` for admin or `false` for instructor.",
        examples={"example": True},
    ),
    service: AdminService = Depends(get_admin_service),
    _auth=Depends(authorize_admin),
):
    return service.update_instructor_admin(instructor_id, is_admin)