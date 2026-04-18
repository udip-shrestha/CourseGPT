import { APIClient } from "./ApiClient.ts";
import type { CourseQueriesResponse } from "./QueryClient";

export interface OverviewSummary {
    activeUsers?: number;
    totalEnrolled?: number;
    totalQueries?: number;
    engagementRate?: number;
    averageSatisfaction?: number;
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

export interface UsageTrendPoint {
    date: string;
    queries: number;
    uniqueUsers: number;
}

export interface QueryDistributionItem {
    courseName: string;
    count: number;
}

export interface MetricBreakdownItem {
    count: number;
    courseId?: string;
    courseName?: string;
    instructorId?: string;
    instructorName?: string;
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

export interface EngagementDistributionItem {
    range: string;
    count: number;
}

export interface DocumentUsageItem {
    documentName: string;
    studentCount: number;
    usagePercentage: number;
}

export interface CourseTrendInsights {
    peakDate: string;
    peakQueries: number;
    averageDailyQueries: number;
    averageDailyUsers: number;
    activeQueryDays: number;
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

    /**
     * Get specific document count for a course by parsing the grouped document map.
     */
    async getDocumentCount(courseId: string) {
        if (!courseId) return { data: 0 };

        const res = await this.client.request<Record<string, number>>(
            "GET",
            "/documents/count",
            { query: { group_by_course: true } }
        );

        if (res.data) {
            return { data: res.data[courseId] ?? 0 };
        }

        return { data: 0, errorMessage: res.errorMessage };
    }

    async getStudentCount(courseId: string) {
        if (!courseId) return { errorMessage: "Course ID is required." };
        return this.client.request<{ course_id: string; student_count: number }>(
            "GET",
            "/students/count",
            { query: { course_id: courseId } }
        );
    }

    async getCourseSatisfaction(courseId: string) {
        if (!courseId) return { errorMessage: "Course ID is required." };
        return this.client.request<CourseSatisfaction>(
            "GET",
            `/feedback/courses/${courseId}/satisfaction`
        );
    }

    async getCourseDocumentUsage(courseId: string) {
        if (!courseId) return { errorMessage: "Course ID is required." };
        return this.client.request<DocumentUsageItem[]>(
            "GET",
            `/courses/${courseId}/analytics/document-usage`
        );
    }

    async getCourseOverview(courseId: string, days?: number) {
        if (!courseId) return { errorMessage: "Course ID is required." };
        return this.client.request<any>("GET", `/courses/${courseId}/analytics/overview`, {
            query: days ? { days } : undefined
        });
    }

    async getTopQuestions(courseId: string, limit: number = 10, _timeRange?: string) {
        if (!courseId) return { errorMessage: "Course ID is required." };
        return this.client.request<TopQuestionsItem[]>("GET", `/courses/${courseId}/analytics/top-questions`, {
            query: { limit }
        });
    }

    async getTopKeywords(courseId: string, limit: number = 20, _timeRange?: string) {
        if (!courseId) return { errorMessage: "Course ID is required." };
        return this.client.request<TopKeywordsItem[]>("GET", `/courses/${courseId}/analytics/top-keywords`, {
            query: { limit }
        });
    }

    async getEngagementMetrics(courseId: string) {
        if (!courseId) return { errorMessage: "Course ID is required." };
        return this.client.request("GET", `/courses/${courseId}/analytics/engagement`);
    }

    async getUsageTrend(courseId: string, timeRange: string) {
        if (!courseId) return { errorMessage: "Course ID is required." };
        return this.client.request<UsageTrendPoint[]>("GET", `/courses/${courseId}/analytics/usage-trend`, {
            query: { days: timeRangeToDays(timeRange) }
        });
    }

    async getQueryDistribution(instructorId: string, timeRange: string) {
        if (!instructorId) return { errorMessage: "Instructor ID is required." };
        return this.client.request<QueryDistributionItem[]>("GET", `/instructors/${instructorId}/analytics/query-distribution`, {
            query: { days: timeRangeToDays(timeRange) }
        });
    }

    // --- SYSTEM / ADMIN LEVEL METHODS (Restored for SystemAnalyticsPage) ---

    async getSystemOverview(instructorId: string) {
        if (!instructorId) return { errorMessage: "Instructor ID is required." };
        return this.client.request<SystemOverview>("GET", `/instructors/${instructorId}/analytics/system-overview`);
    }

    async getSystemQueryTrend(instructorId: string, timeRange: string) {
        if (!instructorId) return { errorMessage: "Instructor ID is required." };
        return this.client.request<UsageTrendPoint[]>("GET", `/instructors/${instructorId}/analytics/system-query-trend`, {
            query: { days: timeRangeToDays(timeRange) }
        });
    }

    async getDocumentsByCourse(instructorId: string) {
        if (!instructorId) return { errorMessage: "Instructor ID is required." };
        return this.client.request<MetricBreakdownItem[]>("GET", `/instructors/${instructorId}/analytics/documents-by-course`);
    }

    async getDocumentsByInstructor(instructorId: string) {
        if (!instructorId) return { errorMessage: "Instructor ID is required." };
        return this.client.request<MetricBreakdownItem[]>("GET", `/instructors/${instructorId}/analytics/documents-by-instructor`);
    }

    async getCoursesByInstructor(instructorId: string) {
        if (!instructorId) return { errorMessage: "Instructor ID is required." };
        return this.client.request<MetricBreakdownItem[]>("GET", `/instructors/${instructorId}/analytics/courses-by-instructor`);
    }

    async getQueriesByCourse(instructorId: string, timeRange: string) {
        if (!instructorId) return { errorMessage: "Instructor ID is required." };
        return this.client.request<MetricBreakdownItem[]>("GET", `/instructors/${instructorId}/analytics/queries-by-course`, {
            query: { days: timeRangeToDays(timeRange) }
        });
    }

    /**
     * Full course Q&A history
     */
    async getAllCourseQueries(
        courseId: string,
        options?: { orderBy?: string; orderDir?: "asc" | "desc" }
    ) {
        if (!courseId) return { errorMessage: "Course ID is required." };
        return this.client.request<CourseQueriesResponse>("GET", `/courses/${courseId}/queries/all`, {
            query: {
                order_by: options?.orderBy ?? "asked_at",
                order_dir: options?.orderDir ?? "desc",
            },
        });
    }

    async topKeywords(courseId: string, limit: number, timeRange: string) {
        return this.getTopKeywords(courseId, limit, timeRange);
    }
}