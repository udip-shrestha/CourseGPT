import React, { createContext, useContext, useMemo } from "react";
import { APIClient, apiClient } from "./ApiClient.ts";
import { AuthClient } from "./AuthClient.ts";
import { DocumentClient } from "./DocumentClient.ts";
import { CourseClient } from "./CourseClient.ts";
import { InstructorClient } from "./InstructorClient.ts";
import { QueryClient } from "./QueryClient.ts";

interface APIClients {
    apiClient: APIClient
    authClient: AuthClient;
    documentClient: DocumentClient;
    courseClient: CourseClient;
    instructorClient: InstructorClient;
    queryClient: QueryClient;
}

// Create a Context to hold the API client instance
const ApiClientContext = createContext<APIClients | null>(null);

// Provider component
export const ApiClientProvider: React.FC<{
    children: React.ReactNode;
}> = ({ children }) => {
    const client: APIClients = useMemo(() => {
        apiClient.loadToken();

        return {
            apiClient: apiClient,
            authClient: new AuthClient(apiClient),
            documentClient: new DocumentClient(apiClient),
            courseClient: new CourseClient(apiClient),
            instructorClient: new InstructorClient(apiClient),
            queryClient: new QueryClient(apiClient)
        };
    }, []);

    return (
        <ApiClientContext.Provider value={client}>
            {children}
        </ApiClientContext.Provider>
    );
};

// 4Custom hook for convenient access
export const useApiClient = () => {
    const ctx = useContext(ApiClientContext);

    if (!ctx) {
        throw new Error("useApiClient must be used inside ApiClientProvider");
    }

    return ctx;
};