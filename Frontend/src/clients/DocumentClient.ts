import type { APIClient } from "./ApiClient";

export class DocumentClient {
    private baseClient: APIClient;
    constructor(baseClient: APIClient) {
        this.baseClient = baseClient
    }

    async uploadDocument(courseId: string, file: File) {
        if (!courseId || !file) return { errorMessage: "Course ID and file are required." };
        const formData = new FormData();
        formData.append("file", file);
        return this.baseClient.request("POST", `/courses/${courseId}/documents`, {
            body: formData,
            isJson: false,
            operationId: `documents-upload-${courseId}`,
        });
    }

    async listDocuments(courseId: string, filters?: { file_type?: string; limit?: number; offset?: number; order_by?: "uploaded_at" | "file_name"; order_dir?: "asc" | "desc" }) {
        const query = Object.fromEntries(Object.entries(filters || {}).filter(([_, v]) => v !== undefined && v !== null));
        return this.baseClient.request("GET", `/courses/${courseId}/documents`, { query, operationId: `documents-list-${courseId}` });
    }

    async getDocument(courseId: string, docId: string) {
        if (!courseId || !docId) return { errorMessage: "Course ID and Document ID are required." };
        return this.baseClient.request("GET", `/courses/${courseId}/documents/${docId}`, { operationId: `documents-get-${docId}` });
    }

    async deleteDocument(courseId: string, docId: string) {
        if (!courseId || !docId) return { errorMessage: "Course ID and Document ID are required." };
        return this.baseClient.request("DELETE", `/courses/${courseId}/documents/${docId}`, { operationId: `documents-delete-${docId}` });
    }

    async downloadDocument(courseId: string, docId: string) {
        console.log("HI!");
        if (!courseId || !docId) return { errorMessage: "Course ID and Document ID are required." };

        return this.baseClient.request("GET", `/courses/${courseId}/documents/${docId}/download`, { operationId: `documents-download-${docId}`,});
    }
    
    async previewDocument(courseId: string, docId: string) {
        if (!courseId || !docId) return { errorMessage: "Course ID and Document ID are required." };
        return this.baseClient.request("GET", `/courses/${courseId}/documents/${docId}/preview`, { operationId: `documents-preview-${docId}`,});
    }
    
}
