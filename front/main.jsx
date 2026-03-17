import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import { GoogleOAuthProvider } from "@react-oauth/google";
import { env } from "./environ";
import "./index.css";
import App from "./App.jsx";
import ErrorBoundary from "./assets/components/ErrorBoundary";

createRoot(document.querySelector("#root")).render(
  <StrictMode>
    <GoogleOAuthProvider clientId={env.googleClientId}>
      <BrowserRouter>
        <ErrorBoundary>
          <App />
        </ErrorBoundary>
      </BrowserRouter>
    </GoogleOAuthProvider>
  </StrictMode>
);
