import type { APIClient } from "./ApiClient";

export class InstructorClient {
    private baseClient: APIClient;

    constructor(baseClient: APIClient) {
        this.baseClient = baseClient;
    }

    async createInstructor(params: {name: string; title: string; university: string; email: string; password: string;}) {
        return this.baseClient.request("POST", `/instructors`, {query: params, isJson: false, operationId: `instructors-create`});
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
}
