export class APIClient {
    private token: string | null = null;
    private readonly baseUrl: string;
    private readonly storageKey = "coursegpt_token";
    private readonly instructorKey = "coursegpt_instructor_id";
    private readonly instructorRoleKey = "coursegpt_instructor_role";
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

    // ===== INSTRUCTOR ROLE MANAGEMENT =====
    setInstructorRole(instructorRole: string) {
        localStorage.setItem(this.instructorRoleKey, instructorRole);
    }

    getInstructorRole(): string | null {
        return localStorage.getItem(this.instructorRoleKey);
    }

    // ===== LOGOUT =====
    logout(): void {
        this.clearToken();
        localStorage.removeItem(this.instructorKey);
        localStorage.removeItem(this.instructorRoleKey);
        for (const c of this.controllers.values()) c.abort();
        this.controllers.clear();
        window.location.href = "/login"; // main branch improvement
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
            if (isJson && !(body instanceof FormData)) finalHeaders.set("Content-Type", "application/json");

            let requestBody: BodyInit | undefined;
            if (body !== undefined) {
                if (body instanceof FormData || body instanceof URLSearchParams) requestBody = body;
                else if (typeof body === "string") requestBody = body;
                else requestBody = JSON.stringify(body);
            }

            const response = await fetch(url, {
                method,
                headers: finalHeaders,
                body: ["GET", "HEAD"].includes(method) ? undefined : requestBody,
                signal: controller?.signal,
            });

            // ===== HANDLE ERRORS =====
            if (!response.ok) {
                console.log("Error REsponse");
                if (response.status === 401 && this.isAuthenticated()) this.logout(); // auto-logout on 401

                let errorMessage = response.statusText;
                
                if (response.headers.get("content-disposition")) {
                }
                else if (response.headers.get("content-type")?.includes("application/json")) {
                    const err = await response.json().catch(() => null);
                    errorMessage = err?.detail || JSON.stringify(err) || errorMessage;
                } else {
                    const text = await response.text().catch(() => "");
                    errorMessage = text || errorMessage;
                }
                return { errorStatus: response.status, errorMessage };
            }
            console.log("Success REsponse");

            // ===== SUCCESSFUL 204 =====
            if (response.status === 204) return { data: null as T };

            // ===== SUCCESSFUL FILE STREAM DETECTED =====
            const disposition = response.headers.get("content-disposition");
            console.log(disposition);
            if (disposition) {
                const blob = await response.blob();

                let fileName = "download";
                const match = disposition.match(/filename\*?=UTF-8''(.+)|filename="(.+?)"/);
                if (match) {
                    const raw = match[1] || match[2];
                    try { fileName = decodeURIComponent(raw); } catch { fileName = raw; }
                }

                return { data: { blob, fileName } as T };
            }

            // ===== SUCCESSFUL JSON =====
            const contentType = response.headers.get("content-type");
            if (contentType?.includes("application/json")) {
                const data = (await response.text().then(t => (t ? JSON.parse(t) : {}))) as T;
                return { data };
            }

            // ===== SUCCESSFUL TEXT =====
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

}

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export const apiClient = new APIClient(API_BASE_URL);
