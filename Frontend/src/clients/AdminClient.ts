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

    async createDiscordAdmin(discordId: string) {
        if (!discordId) return { errorMessage: "Discord ID is required." };

        return this.baseClient.request("POST", `/discord-admins`, {
            body: { discord_id: discordId },
            operationId: `discord-admin-create-${discordId}`,
        });
    }

    async listDiscordAdmins(options?: { limit?: number; offset?: number }) {
        return this.baseClient.request("GET", `/discord-admins`, {
            query: {
                ...(options?.limit !== undefined && { limit: options.limit }),
                ...(options?.offset !== undefined && { offset: options.offset }),
            },
            operationId: "discord-admins-list",
        });
    }

    async getDiscordAdmin(discordId: string) {
        if (!discordId) return { errorMessage: "Discord ID is required." };

        const id = encodeURIComponent(discordId);
        return this.baseClient.request("GET", `/discord-admins/${id}`, {
            operationId: `discord-admin-get-${id}`,
        });
    }

    async deleteDiscordAdmin(discordId: string) {
        if (!discordId) return { errorMessage: "Discord ID is required." };

        const id = encodeURIComponent(discordId);
        return this.baseClient.request("DELETE", `/discord-admins/${id}`, {
            operationId: `discord-admin-delete-${id}`,
        });
    }
}