import { APIClient } from "./ApiClient.ts";

export class AnalyticsClient {
    private client: APIClient;

    constructor(client: APIClient) {
        this.client = client;
    }

    /**
     * Uses the core .request method from APIClient
     */
    async getCourseOverview(courseId: string, days?: number) {
        return this.client.request("GET", `/courses/${courseId}/analytics/overview`, {
            query: days ? { days } : undefined
        });
    }

    async getTopQuestions(courseId: string, limit: number = 10) {
        return this.client.request("GET", `/courses/${courseId}/analytics/top-questions`, {
            query: { limit }
        });
    }

    async getTopKeywords(courseId: string, limit: number = 20) {
        return this.client.request("GET", `/courses/${courseId}/analytics/top-keywords`, {
            query: { limit }
        });
    }

    async getEngagementMetrics(courseId: string) {
        return this.client.request("GET", `/courses/${courseId}/analytics/engagement`);
    }
}