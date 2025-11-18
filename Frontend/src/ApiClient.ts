export class APIClient {
    private token: string | null = null;
    private readonly baseUrl: string;
    private readonly storageKey = "coursegpt_token";
    private readonly instructorKey = "coursegpt_instructor_id";
    private controllers = new Map<string, AbortController>();

    constructor(baseUrl: string) {
        this.baseUrl = baseUrl.endsWith("/") ? baseUrl.slice(0, -1) : baseUrl;
        this.loadToken();
    }

    // ===== TOKEN MANAGEMENT =====
    setToken(token: string) {
        this.token = token;
        localStorage.setItem(this.storageKey, token);
    }

    loadToken() {
        this.token = localStorage.getItem(this.storageKey);
    }

    getToken(): string | null {
        if (this.token == null) this.loadToken();
        return this.token;
    }

    isAuthenticated(): boolean {
        return !!this.getToken();
    }

    clearToken() {
        this.token = null;
        localStorage.removeItem(this.storageKey);
    }

    // ===== INSTRUCTOR ID MANAGEMENT =====
    setInstructorId(instructorId: string) {
        localStorage.setItem(this.instructorKey, instructorId);
    }

    getInstructorId(): string | null {
        return localStorage.getItem(this.instructorKey);
    }

    // ===== LOGOUT =====
    logout(): void {
        this.clearToken();
        localStorage.removeItem(this.instructorKey);
        for (const c of this.controllers.values()) c.abort();
        this.controllers.clear();
    }

    // ===== INTERNAL CONTROLLER MANAGEMENT =====
    private getController(operationId: string): AbortController {
        if (this.controllers.has(operationId)) {
            this.controllers.get(operationId)?.abort();
        }
        const controller = new AbortController();
        this.controllers.set(operationId, controller);
        return controller;
    }

    // ===== CORE REQUEST =====
    async request<T = any>(
        method: string,
        endpoint: string,
        {
            body,
            query,
            headers,
            isJson = true,
            signal,
            operationId,
        }: {
            body?: BodyInit | Record<string, unknown>;
            query?: Record<string, string | number | boolean | undefined>;
            headers?: HeadersInit;
            isJson?: boolean;
            signal?: AbortSignal;
            operationId?: string;
        } = {}
    ): Promise<{ data?: T; errorStatus?: number; errorMessage?: string }> {
        const controller = signal
            ? { signal }
            : operationId
                ? this.getController(operationId)
                : undefined;

        try {
            const url = new URL(endpoint, this.baseUrl);
            if (query) {
                Object.entries(query).forEach(([key, value]) => {
                    if (value !== undefined) url.searchParams.append(key, String(value));
                });
            }

            const finalHeaders = new Headers(headers || {});
            if (this.token) finalHeaders.set("Authorization", `Bearer ${this.token}`);
            if (isJson && !(body instanceof FormData)) {
                finalHeaders.set("Content-Type", "application/json");
            }

            let requestBody: BodyInit | undefined;
            if (body !== undefined) {
                if (body instanceof FormData || body instanceof URLSearchParams) {
                    requestBody = body;
                } else if (typeof body === "string") {
                    requestBody = body;
                } else {
                    requestBody = JSON.stringify(body);
                }
            }

            const response = await fetch(url, {
                method,
                headers: finalHeaders,
                body: ["GET", "HEAD"].includes(method) ? undefined : requestBody,
                signal: controller?.signal,
            });

            if (!response.ok) {
                const contentType = response.headers.get("content-type");
                let errorMessage = response.statusText;
                if (contentType?.includes("application/json")) {
                    const err = await response.json().catch(() => null);
                    errorMessage = err?.detail || JSON.stringify(err) || errorMessage;
                } else {
                    const text = await response.text().catch(() => "");
                    if (text) errorMessage = text;
                }
                return { errorStatus: response.status, errorMessage };
            }

            if (response.status === 204) return { data: null as T };

            const contentType = response.headers.get("content-type");
            if (contentType?.includes("application/json")) {
                const data = (await response.text().then((t) => (t ? JSON.parse(t) : {}))) as T;
                return { data };
            }
            if (contentType?.startsWith("text/")) {
                const data = (await response.text()) as unknown as T;
                return { data };
            }

            return { data: null as T };
        } catch (err: any) {
            if (err.name === "AbortError") return { errorStatus: 0, errorMessage: undefined };
            return { errorStatus: -1, errorMessage: err.message };
        }
    }

    // ===== AUTH =====
    async login(username: string, password: string) {
        const form = new URLSearchParams();
        form.append("grant_type", "password");
        form.append("username", username);
        form.append("password", password);
        form.append("scope", "");
        form.append("client_id", "string");
        form.append("client_secret", "string");

        const { data, errorStatus, errorMessage } = await this.request(
            "POST",
            "/auth/login",
            { body: form, isJson: false, operationId: "auth-login" }
        );

        if (data?.access_token && data?.instructor_id) {
            this.setToken(data.access_token);
            this.setInstructorId(data.instructor_id);
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

        const { data, errorStatus, errorMessage } = await this.request(
            "POST",
            "/auth/register",
            { body: form, isJson: false, headers: { "Content-Type": "application/x-www-form-urlencoded" }, operationId: "auth-register" }
        );

        if (data?.access_token && data?.instructor_id) {
            this.setToken(data.access_token);
            this.setInstructorId(data.instructor_id);
            return { data, errorStatus, errorMessage };
        }
        const message = errorMessage || "Critical Error: Invalid register response structure.";
        return { data, errorStatus: errorStatus ?? -1, errorMessage: message };
    }

    // ===== DOCUMENT ENDPOINTS =====
    async uploadDocument(courseId: string, file: File) {
        if (!courseId || !file) return { errorMessage: "Course ID and file are required." };
        const formData = new FormData();
        formData.append("file", file);
        return this.request("POST", `/courses/${courseId}/documents`, { body: formData, isJson: false, operationId: `documents-upload-${courseId}` });
    }

    async listDocuments(courseId: string, filters?: { file_type?: string; limit?: number; offset?: number; order_by?: "uploaded_at" | "file_name"; order_dir?: "asc" | "desc" }) {
        const query = Object.fromEntries(Object.entries(filters || {}).filter(([_, v]) => v !== undefined && v !== null));
        return this.request("GET", `/courses/${courseId}/documents`, { query, operationId: `documents-list-${courseId}` });
    }

    async getDocument(courseId: string, docId: string) {
        if (!courseId || !docId) return { errorMessage: "Course ID and Document ID are required." };
        return this.request("GET", `/courses/${courseId}/documents/${docId}`, { operationId: `documents-get-${docId}` });
    }

    async deleteDocument(courseId: string, docId: string) {
        if (!courseId || !docId) return { errorMessage: "Course ID and Document ID are required." };
        return this.request("DELETE", `/courses/${courseId}/documents/${docId}`, { operationId: `documents-delete-${docId}` });
    }

    // ===== COURSE ENDPOINTS =====
    async listInstructorCourses(instructorId: string, options?: { institution?: string; limit?: number; offset?: number; order_by?: string; order_dir?: "asc" | "desc" }) {
        const query = Object.fromEntries(Object.entries(options || {}).filter(([_, v]) => v !== undefined));
        return this.request("GET", `/instructors/${instructorId}/courses`, { query, operationId: `instructor-courses-${instructorId}` });
    }

    async getCourse(courseId: string) {
        if (!courseId) return { errorMessage: "Course ID is required." };
        return this.request("GET", `/courses/${courseId}`, { operationId: `course-get-${courseId}` });
    }

    async deleteCourse(courseId: string) {
        if (!courseId) return { errorMessage: "Course ID is required." };
        return this.request("DELETE", `/courses/${courseId}`, { operationId: `course-delete-${courseId}` });
    }

    async createCourse(instructorId: string, params: { name: string; institution: string; semester_id: number; year: number }) {
        if (!instructorId) return { errorMessage: "Instructor ID is required." };
        return this.request("POST", `/instructors/${instructorId}/courses`, { query: params, isJson: false, operationId: `course-create-${instructorId}` });
    }

    async updateCourse(courseId: string, params: { name?: string; institution?: string; semester_id?: number; year?: number }) {
        if (!courseId) return { errorMessage: "Course ID is required." };
        const query = Object.fromEntries(Object.entries(params || {}).filter(([_, v]) => v !== undefined));
        return this.request("PUT", `/courses/${courseId}`, { query, isJson: false, operationId: `course-update-${courseId}` });
    }

    // ===== COURSE QUERY (OLD) =====
    async queryCourse(courseId: string, question: string) {
        if (!courseId || !question) return { errorMessage: "Course ID and question are required." };
        const params = { course_id: courseId, question };
        return this.request("POST", `/courses/${courseId}/queries`, { query: params, operationId: `course-query-${courseId}` });
    }
}

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
export const apiClient = new APIClient(API_BASE_URL);
