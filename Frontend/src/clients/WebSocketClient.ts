import { API_BASE_URL } from "./ApiClient";


export class WebSocketClient {
    private readonly baseUrl: string;
    private sockets = new Map<string, WebSocket>();
    private listeners = new Map<string, Set<(msg: any) => void>>();
    private reconnectEnabled = new Map<string, boolean>();

    constructor(baseApiUrl: string) {
        this.baseUrl = baseApiUrl.replace(/^http/, "ws");
        this.baseUrl = this.baseUrl.endsWith("/") ? this.baseUrl.slice(0, -1) : this.baseUrl;
    }

    private makeUrl(path: string): string {
        if (!path.startsWith("/")) path = `/${path}`;
        return `${this.baseUrl}${path}`;
    }

    private connect(url: string): WebSocket {
        const existing = this.sockets.get(url);
        if (existing && (existing.readyState === WebSocket.OPEN || existing.readyState === WebSocket.CONNECTING)) {
            return existing;
        }

        const ws = new WebSocket(url);
        this.sockets.set(url, ws);
        this.reconnectEnabled.set(url, true);

        ws.onopen = () => console.log("[WS] Connected:", url);

        ws.onmessage = (event) => {
            const subs = this.listeners.get(url);
            if (!subs) return;

            let parsed: any = event.data;
            try {
                parsed = JSON.parse(event.data);
            } catch {}

            subs.forEach(cb => cb(parsed));
        };

        ws.onerror = (err) => console.error("[WS] Error:", url, err);

        ws.onclose = () => {
            console.warn("[WS] Closed:", url);
            if (this.reconnectEnabled.get(url)) {
                console.log("[WS] Reconnecting in 1s:", url);
                setTimeout(() => this.connect(url), 1000);
            }
        };

        return ws;
    }

    private subscribe(path: string, callback: (msg: any) => void) {
        const url = this.makeUrl(path);
        this.connect(url);

        if (!this.listeners.has(url)) {
            this.listeners.set(url, new Set());
        }

        const set = this.listeners.get(url)!;
        set.add(callback);

        return {
            unsubscribe: () => {
                set.delete(callback);
                if (set.size === 0) {
                    this.reconnectEnabled.set(url, false);
                    this.sockets.get(url)?.close();
                    this.sockets.delete(url);
                }
            }
        };
    }

    subscribeCourseDocuments(courseId: string, callback: (msg: any) => void) {
        if (!courseId) return { errorMessage: "Course ID required.", unsubscribe: () => {} };
        return this.subscribe(`/courses/${courseId}/documents`, callback);
    }

    subscribeCourseQueries(courseId: string, callback: (msg: any) => void) {
        if (!courseId) return { errorMessage: "Course ID required.", unsubscribe: () => {} };
        return this.subscribe(`/courses/${courseId}/queries`, callback);
    }
}

export const webSocketClient = new WebSocketClient(API_BASE_URL)
