import React, { createContext, useContext, useMemo } from "react";
import { APIClient, apiClient } from "./ApiClient";

// Create a Context to hold the API client instance
const ApiClientContext = createContext<APIClient>(apiClient);

// Provider component
export const ApiClientProvider: React.FC<{
  children: React.ReactNode;
}> = ({ children }) => {
  const client = useMemo(() => {
    apiClient.loadToken(); 
    return apiClient;
  }, []);

  return (
    <ApiClientContext.Provider value={client}>
      {children}
    </ApiClientContext.Provider>
  );  
};

// 4Custom hook for convenient access
export const useApiClient = (): APIClient => useContext(ApiClientContext);
