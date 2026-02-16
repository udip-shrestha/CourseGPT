import type { APIClient } from "./ApiClient.ts";

export interface OverviewSummary {
    activeUsers: number;
    totalEnrolled: number;
    engagementRate: number;
    totalQueries: number;
}

export interface UsageTrendPoint {
    date: string;
    queries: number;
    uniqueUsers: number;
}

export interface TopQuestionsItem {
    queryText: string;
    count: number;
}

export interface QueryDistributionItem {
    courseId: string;
    courseName: string;
    count: number;
}

export interface TopKeywordsItem {
    keyword: string;
    count: number;
}

export class AnalyticsClient {
    private baseClient: APIClient;

    constructor(baseClient: APIClient) {
        this.baseClient = baseClient;
    }
    async getOverviewSummary(
        courseId: string,
        range?: string
    ): Promise<{ data?: OverviewSummary; errorStatus?: number; errorMessage?: string }> {
        const query = range ? { range } : undefined;
        return this.baseClient.request<OverviewSummary>("GET", `/courses/${courseId}/analytics/overview`, {
            query,
            operationId: `analytics-overview-${courseId}`,
        });
    }

    async getUsageTrend(
        courseId: string,
        range?: string
    ): Promise<{ data?: UsageTrendPoint[]; errorStatus?: number; errorMessage?: string }> {
        const query = range ? { range } : undefined;
        return this.baseClient.request<UsageTrendPoint[]>("GET", `/courses/${courseId}/analytics/usage-trend`, {
            query,
            operationId: `analytics-usage-trend-${courseId}`,
        });
    }

    async getTopQuestions(
        courseId: string,
        limit = 10,
        range?: string
    ): Promise<{ data?: TopQuestionsItem[]; errorStatus?: number; errorMessage?: string }> {
        const query: Record<string, string | number> = { limit };
        if (range) query.range = range;
        return this.baseClient.request<TopQuestionsItem[]>("GET", `/courses/${courseId}/analytics/top-questions`, {
            query,
            operationId: `analytics-top-questions-${courseId}`,
        });
    }

    async getQueryDistribution(
        instructorId: string,
        range?: string
    ): Promise<{ data?: QueryDistributionItem[]; errorStatus?: number; errorMessage?: string }> {
        const query = range ? { range } : undefined;
        return this.baseClient.request<QueryDistributionItem[]>(
            "GET",
            `/instructors/${instructorId}/analytics/query-distribution`,
            { query, operationId: `analytics-query-distribution-${instructorId}` }
        );
    }

    async topKeywords(
        courseId: string,
        limit = 10,
        range?: string
    ): Promise<{ data?: TopKeywordsItem[]; errorStatus?: number; errorMessage?: string }> {
        const query: Record<string, string | number> = { limit };
        if (range) query.range = range;
        return this.baseClient.request<TopKeywordsItem[]>("GET", `/courses/${courseId}/analytics/top-keywords`, {
            query,
            operationId: `analytics-top-keywords-${courseId}`,
        });
    }
}
