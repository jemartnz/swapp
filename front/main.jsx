import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import { GoogleOAuthProvider } from "@react-oauth/google";
import { env } from "./environ";
import "./index.css";
import App from "./App.jsx";

createRoot(document.querySelector("#root")).render(
  <StrictMode>
    <GoogleOAuthProvider clientId={env.googleClientId}>
      <BrowserRouter>
        <App />
      </BrowserRouter>
    </GoogleOAuthProvider>
  </StrictMode>
);
