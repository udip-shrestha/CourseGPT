import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter } from "react-router-dom";


import './index.css';

import App from './App.tsx';

import { ApiClientProvider } from './clients/ApiClientContext.tsx';
import { WebSocketClientProvider } from './clients/WebSocketClientContext.tsx';

createRoot(document.getElementById('root')!).render(
    <StrictMode>
        {/* 2. BrowserRouter wraps everything */}
        <BrowserRouter>
            {/* 3. ApiClientProvider wraps App */}
            <ApiClientProvider>
                <WebSocketClientProvider>
                    <App />
                </WebSocketClientProvider>
            </ApiClientProvider>
        </BrowserRouter>
    </StrictMode>
);