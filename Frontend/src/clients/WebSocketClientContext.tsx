import React, { createContext, useContext, useMemo } from "react";
import { webSocketClient, WebSocketClient } from "./WebSocketClient";

// Create context
const WebSocketClientContext = createContext<WebSocketClient>(webSocketClient);

// Provider
export const WebSocketClientProvider: React.FC<{
    children: React.ReactNode;
}> = ({ children }) => {
    const client = useMemo(() => {
        return webSocketClient;
    }, []);

    return (
        <WebSocketClientContext.Provider value={client}>
            {children}
        </WebSocketClientContext.Provider>
    );
};

// Hook
export const useWebSocketClient = (): WebSocketClient => useContext(WebSocketClientContext);
