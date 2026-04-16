import type { APIClient } from "./ApiClient";

export class InstructorClient {
    private baseClient: APIClient;

    constructor(baseClient: APIClient) {
        this.baseClient = baseClient;
    }

    async getInstructor(instructorId: string) {
        if (!instructorId) return { errorMessage: "Instructor ID is required." };
        return this.baseClient.request("GET", `/instructors/${instructorId}`, { operationId: `instructor-get-${instructorId}` });
    }

    async updateInstructor(instructorId: string, params: {name?: string; title?: string; university?: string; email?: string; password?: string;}) {
        if (!instructorId) return { errorMessage: "Instructor ID is required." };
        const query = Object.fromEntries(Object.entries(params).filter(([_, v]) => v !== undefined));
        return this.baseClient.request("PUT", `/instructors/${instructorId}`, {query, isJson: false, operationId: `instructor-update-${instructorId}`});
    }

    async deleteInstructor(instructorId: string) {
        if (!instructorId) return { errorMessage: "Instructor ID is required." };
        return this.baseClient.request("DELETE", `/instructors/${instructorId}`, { operationId: `instructor-delete-${instructorId}` });
    }

    async listInstructors(params?: {
        name?: string;
        email?: string;
        university?: string;
        limit?: number;
        offset?: number;
        order_by?: string;
        order_dir?: string;
    }) {
        const query = Object.fromEntries(
            Object.entries(params ?? {}).filter(([_, v]) => v !== undefined && v !== "")
        );

        return this.baseClient.request("GET", "/instructors", {
            query,
            operationId: "instructor-list",
        });
    }

}
