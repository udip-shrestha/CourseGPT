import { APIClient } from "./ApiClient.ts";
import type { CourseQueriesResponse } from "./QueryClient";

export interface AnswerFeedbackItem {
    id: string;
    query_id: string;
    course_id: string;
    student_id: string;
    vote: number;
    created_at: string;
}

export interface CourseFeedbackItem {
    id: string;
    course_id: string;
    feedback_text: string;
    received_at: string;
}

export interface AdminFeedbackItem extends CourseFeedbackItem {
    course_name: string;
}

export interface UsageTrendPoint {
    date: string;
    queries: number;
    uniqueUsers: number;
}

export interface SystemOverview {
    totalDocuments: number;
    totalCourses: number;
    totalInstructors: number;
    totalStudents: number;
    totalQueries: number;
    totalFeedback: number;
    averageDocumentsPerCourse: number;
    averageCoursesPerInstructor: number;
    averageQueriesPerCourse: number;
}

export interface TopQuestionsItem {
    queryText: string;
    count: number;
    answer?: string;
}

export interface TopKeywordsItem {
    keyword: string;
    count: number;
}

export interface CourseSatisfaction {
    course_id: string;
    upvotes: number;
    downvotes: number;
    total_votes: number;
    satisfaction_score: number;
}

export interface MetricBreakdownItem {
    count: number;
    courseId?: string;
    courseName?: string;
    instructorId?: string;
    instructorName?: string;
}

export interface QueryDistributionItem {
    courseName: string;
    count: number;
}

function timeRangeToDays(timeRange: string): number {
    switch (timeRange) {
        case "7d": return 7;
        case "30d": return 30;
        case "90d": return 90;
        case "1y": return 365;
        default: return 7;
    }
}

export class AnalyticsClient {
    private client: APIClient;

    constructor(client: APIClient) {
        this.client = client;
    }

    async getDocumentCount(courseId: string) {
        if (!courseId) return { data: 0 };
        const res = await this.client.request<Record<string, number>>("GET", "/documents/count", { query: { group_by_course: true } });
        return { data: res.data ? (res.data[courseId] ?? 0) : 0 };
    }

    async getStudentCount(courseId: string) {
        return this.client.request<{ course_id: string; student_count: number }>("GET", "/students/count", { query: { course_id: courseId } });
    }

    async getCourseSatisfaction(courseId: string) {
        return this.client.request<CourseSatisfaction>("GET", `/feedback/courses/${courseId}/satisfaction`);
    }

    async getCourseAnswerFeedbacks(courseId: string, limit: number = 100, offset: number = 0) {
        return this.client.request<{ total: number; answer_feedbacks: AnswerFeedbackItem[] }>(
            "GET",
            `/feedback/courses/${courseId}/answer-feedbacks`,
            { query: { limit, offset } }
        );
    }

    async getCourseFeedback(courseId: string, limit: number = 50, offset: number = 0) {
        return this.client.request<{ total: number; feedback: CourseFeedbackItem[] }>(
            "GET",
            `/feedback/courses/${courseId}`,
            { query: { limit, offset } }
        );
    }

    async getAllFeedback(limit: number = 50, offset: number = 0) {
        return this.client.request<{ total: number; feedback: AdminFeedbackItem[] }>(
            "GET",
            "/feedback",
            { query: { limit, offset } }
        );
    }

    async getUsageTrend(courseId: string, timeRange: string) {
        return this.client.request<UsageTrendPoint[]>("GET", `/courses/${courseId}/analytics/usage-trend`, {
            query: { days: timeRangeToDays(timeRange) }
        });
    }

    // Updated to accept timeRange to fix TS2554
    async getTopQuestions(courseId: string, limit: number = 10, timeRange?: string) {
        return this.client.request<TopQuestionsItem[]>("GET", `/courses/${courseId}/analytics/top-questions`, {
            query: { limit, days: timeRange ? timeRangeToDays(timeRange) : undefined }
        });
    }

    // Updated to accept timeRange to fix TS2554
    async getTopKeywords(courseId: string, limit: number = 20, timeRange?: string) {
        return this.client.request<TopKeywordsItem[]>("GET", `/courses/${courseId}/analytics/top-keywords`, {
            query: { limit, days: timeRange ? timeRangeToDays(timeRange) : undefined }
        });
    }

    // --- SYSTEM / ADMIN LEVEL METHODS (RESTORED) ---

    async getSystemOverview(instructorId: string) {
        return this.client.request<SystemOverview>("GET", `/instructors/${instructorId}/analytics/system-overview`);
    }

    async getSystemQueryTrend(instructorId: string, timeRange: string) {
        return this.client.request<UsageTrendPoint[]>("GET", `/instructors/${instructorId}/analytics/system-query-trend`, {
            query: { days: timeRangeToDays(timeRange) }
        });
    }

    async getDocumentsByCourse(instructorId: string) {
        return this.client.request<MetricBreakdownItem[]>("GET", `/instructors/${instructorId}/analytics/documents-by-course`);
    }

    async getDocumentsByInstructor(instructorId: string) {
        return this.client.request<MetricBreakdownItem[]>("GET", `/instructors/${instructorId}/analytics/documents-by-instructor`);
    }

    async getCoursesByInstructor(instructorId: string) {
        return this.client.request<MetricBreakdownItem[]>("GET", `/instructors/${instructorId}/analytics/courses-by-instructor`);
    }

    async getQueriesByCourse(instructorId: string, timeRange: string) {
        return this.client.request<MetricBreakdownItem[]>("GET", `/instructors/${instructorId}/analytics/queries-by-course`, {
            query: { days: timeRangeToDays(timeRange) }
        });
    }

    async getAllCourseQueries(courseId: string, options?: { orderBy?: string; orderDir?: "asc" | "desc" }) {
        return this.client.request<CourseQueriesResponse>("GET", `/courses/${courseId}/queries/all`, {
            query: { order_by: options?.orderBy ?? "asked_at", order_dir: options?.orderDir ?? "desc" },
        });
    }

    async topKeywords(courseId: string, limit: number, timeRange: string) {
        return this.getTopKeywords(courseId, limit, timeRange);
    }
}
