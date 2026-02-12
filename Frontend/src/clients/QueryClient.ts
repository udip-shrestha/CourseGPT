import type { APIClient } from "./ApiClient";

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

}
