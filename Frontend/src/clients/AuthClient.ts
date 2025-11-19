import type { APIClient } from "./ApiClient";

export class AuthClient {
    private baseClient: APIClient;
    constructor(baseClient: APIClient) {
        this.baseClient = baseClient
    }

    async login(username: string, password: string) {
        const form = new URLSearchParams();
        form.append("grant_type", "password");
        form.append("username", username);
        form.append("password", password);
        form.append("scope", "");
        form.append("client_id", "string");
        form.append("client_secret", "string");

        const { data, errorStatus, errorMessage } = await this.baseClient.request("POST", "/auth/login", {
            body: form,
            isJson: false,
            operationId: "auth-login",
        });

        if (data?.access_token && data?.instructor_id) {
            this.baseClient.setToken(data.access_token);
            this.baseClient.setInstructorId(data.instructor_id);
            return { data, errorStatus, errorMessage };
        }
        const message = errorMessage || "Critical Error: Invalid login response structure.";
        return { data, errorStatus: errorStatus ?? -1, errorMessage: message };
    }

    async register(name: string, title: string, university: string, email: string, password: string) {
        const form = new URLSearchParams();
        form.append("name", name);
        form.append("title", title);
        form.append("university", university);
        form.append("email", email);
        form.append("password", password);

        const { data, errorStatus, errorMessage } = await this.baseClient.request("POST", "/auth/register", {
            body: form,
            isJson: false,
            headers: { "Content-Type": "application/x-www-form-urlencoded" },
            operationId: "auth-register",
        });

        if (data?.access_token && data?.instructor_id) {
            this.baseClient.setToken(data.access_token);
            this.baseClient.setInstructorId(data.instructor_id);
            return { data, errorStatus, errorMessage };
        }
        const message = errorMessage || "Critical Error: Invalid register response structure.";
        return { data, errorStatus: errorStatus ?? -1, errorMessage: message };
    }

}
