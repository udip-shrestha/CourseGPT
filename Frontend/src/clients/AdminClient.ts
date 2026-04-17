import type { APIClient } from "./ApiClient";

export class AdminClient {
    private baseClient: APIClient;

    constructor(baseClient: APIClient) {
        this.baseClient = baseClient;
    }

    async updateCourseStatus(courseId: string, enabled: boolean) {
        if (!courseId) return { errorMessage: "Course ID is required." };

        return this.baseClient.request("PATCH", `/admin/courses/${courseId}/status`, {
            query: { enabled },
            operationId: `admin-course-status-${courseId}`,
        });
    }

    async updateInstructorAdmin(instructorId: string, isAdmin: boolean) {
        if (!instructorId) return { errorMessage: "Instructor ID is required." };

        return this.baseClient.request("PATCH", `/admin/instructors/${instructorId}/admin`, {
            query: { is_admin: isAdmin },
            operationId: `admin-instructor-admin-${instructorId}`,
        });
    }
}