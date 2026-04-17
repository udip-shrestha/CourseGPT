from API.Repository.i_sql_repository import ISQLRepository
from API.Util.decorators import clean_service


class AdminService:
    def __init__(self, sql_repo: ISQLRepository):
        self.sql_repo = sql_repo

    @clean_service
    def update_course_status(self, course_id: str, enabled: bool) -> dict:
        self.sql_repo.update_course_status(course_id, enabled)
        return {"course_id": course_id, "enabled": enabled, "status": "updated"}

    @clean_service
    def update_instructor_admin(self, instructor_id: str, is_admin: bool) -> dict:
        self.sql_repo.update_instructor_admin(instructor_id, is_admin)
        return {"instructor_id": instructor_id, "is_admin": is_admin, "instructor_role": "ADMIN" if is_admin else "INSTRUCTOR", "status": "updated"}