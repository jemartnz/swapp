import "./assets/styles/App.css";
import { StoreProvider } from "./hooks/useStore.jsx";
import { Routes, Route } from "react-router-dom";

import Home from "./pages/Home";
import Register from "./pages/Register";
import Login from "./pages/Login";
import UserProfile from "./pages/UserProfile";
import PublicProfile from "./pages/PublicProfile";
import CategoryUsers from "./pages/CategoryUsers.jsx";
import ErrorBoundary from "./assets/components/ErrorBoundary";

export default function App() {
  return (
    <StoreProvider>
      <Routes>
        <Route path="/" element={<ErrorBoundary><Home /></ErrorBoundary>} />
        <Route path="/registro" element={<ErrorBoundary><Register /></ErrorBoundary>} />
        <Route path="/login" element={<ErrorBoundary><Login /></ErrorBoundary>} />
        <Route path="/perfil" element={<ErrorBoundary><UserProfile /></ErrorBoundary>} />
        <Route path="/usuario/:userId" element={<ErrorBoundary><PublicProfile /></ErrorBoundary>} />
        <Route
          path="/usuarios/categoria/:categoryId"
          element={<ErrorBoundary><CategoryUsers /></ErrorBoundary>}
        />
      </Routes>
    </StoreProvider>
  );
}
