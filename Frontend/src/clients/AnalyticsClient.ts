import { APIClient } from "./ApiClient.ts";
import type { CourseQueriesResponse } from "./QueryClient";

export interface OverviewSummary {
    activeUsers?: number;
    totalEnrolled?: number;
    totalQueries?: number;
    engagementRate?: number;
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

export interface TopQuestionsItem {
    queryText: string;
    count: number;
    answer?: string;
}

export interface TopKeywordsItem {
    keyword: string;
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

    async getCourseOverview(courseId: string, days?: number) {
        if (!courseId) return { errorMessage: "Course ID is required." };
        return this.client.request("GET", `/courses/${courseId}/analytics/overview`, {
            query: days ? { days } : undefined
        });
    }

    async getTopQuestions(courseId: string, limit: number = 10, _timeRange?: string) {
        if (!courseId) return { errorMessage: "Course ID is required." };
        return this.client.request("GET", `/courses/${courseId}/analytics/top-questions`, {
            query: { limit }
        });
    }

    async getTopKeywords(courseId: string, limit: number = 20, _timeRange?: string) {
        if (!courseId) return { errorMessage: "Course ID is required." };
        return this.client.request("GET", `/courses/${courseId}/analytics/top-keywords`, {
            query: { limit }
        });
    }

    async getEngagementMetrics(courseId: string) {
        if (!courseId) return { errorMessage: "Course ID is required." };
        return this.client.request("GET", `/courses/${courseId}/analytics/engagement`);
    }

    async getOverviewSummary(courseId: string, timeRange: string) {
        return this.getCourseOverview(courseId, timeRangeToDays(timeRange));
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

    /**
     * Full course Q&A history (questions and answers) via GET /courses/{id}/queries/all.
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