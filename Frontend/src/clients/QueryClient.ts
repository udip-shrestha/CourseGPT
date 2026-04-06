import type { APIClient } from "./ApiClient";

/** One row from GET /courses/{course_id}/queries */
export interface CourseQueryRecord {
    id: string;
    student_id?: string | null;
    query_text: string;
    response_text?: string | null;
    asked_at?: string;
}

export interface CourseQueriesResponse {
    total: number;
    queries: CourseQueryRecord[];
}

export class QueryClient {
    private baseClient: APIClient;
    constructor(baseClient: APIClient) {
        this.baseClient = baseClient
    }

    async queryCourse(courseId: string, question: string) {
        if (!courseId || !question) return { errorMessage: "Course ID and question are required." };
        const params = { course_id: courseId, question };
        return this.baseClient.request("POST", `/courses/${courseId}/queries`, { query: params, operationId: `course-query-${courseId}` });
    }

    /**
     * Paginated course Q&A history (same payload as a hypothetical /queries/all with limit cap).
     */
    async getCourseQueries(
        courseId: string,
        options?: {
            limit?: number;
            offset?: number;
            orderBy?: string;
            orderDir?: "asc" | "desc";
        }
    ) {
        if (!courseId) return { errorMessage: "Course ID is required." };
        const limit = options?.limit ?? 1000;
        const offset = options?.offset ?? 0;
        return this.baseClient.request<CourseQueriesResponse>("GET", `/courses/${courseId}/queries`, {
            query: {
                limit,
                offset,
                order_by: options?.orderBy ?? "asked_at",
                order_dir: options?.orderDir ?? "desc",
            },
            operationId: `course-queries-list-${courseId}`,
        });
    }

    /**
     * Paginated Q&A history for one student in a course.
     * GET /courses/{course_id}/students/{student_id}/queries
     */
    async getStudentQueries(
        courseId: string,
        studentId: string,
        options?: {
            limit?: number;
            offset?: number;
            orderBy?: string;
            orderDir?: "asc" | "desc";
        }
    ) {
        if (!courseId) return { errorMessage: "Course ID is required." };
        if (!studentId) return { errorMessage: "Student ID is required." };
        const limit = options?.limit ?? 1000;
        const offset = options?.offset ?? 0;
        return this.baseClient.request<CourseQueriesResponse>(
            "GET",
            `/courses/${courseId}/students/${studentId}/queries`,
            {
                query: {
                    limit,
                    offset,
                    order_by: options?.orderBy ?? "asked_at",
                    order_dir: options?.orderDir ?? "desc",
                },
                operationId: `student-queries-${courseId}-${studentId}`,
            }
        );
    }

}
