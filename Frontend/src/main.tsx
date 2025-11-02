import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from "react-router-dom";
import './index.css'
import App from './App.tsx'
import { ApiClientProvider } from './ApiClientContext.tsx';

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <BrowserRouter>
      <ApiClientProvider>
        <App/>
      </ApiClientProvider>
    </BrowserRouter>      
  </StrictMode>
)
