import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter } from "react-router-dom";

// Import Tailwind base styles (order matters)
import './index.css';

// Import your global design system styles (theme, font sizing, etc.)
// (Assuming you have this file from your branch)
//import './globals.css';

import App from './App.tsx';
// --- 1. Import the ApiClientProvider ---
import { ApiClientProvider } from './ApiClientContext.tsx';

createRoot(document.getElementById('root')!).render(
    <StrictMode>
        {/* 2. BrowserRouter wraps everything */}
        <BrowserRouter>
            {/* 3. ApiClientProvider wraps App */}
            <ApiClientProvider>
                <App />
            </ApiClientProvider>
        </BrowserRouter>
    </StrictMode>
);