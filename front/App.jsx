import "./assets/styles/App.css";
import { StoreProvider } from "./hooks/useStore.jsx";
import { Routes, Route } from "react-router-dom";

import Home from "./pages/Home";
import Register from "./pages/Register";
import Login from "./pages/Login";
import UserProfile from "./pages/UserProfile";
import PublicProfile from "./pages/PublicProfile";
import CategoryUsers from "./pages/CategoryUsers.jsx";

export default function App() {
  return (
    <StoreProvider>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/registro" element={<Register />} />
        <Route path="/login" element={<Login />} />
        <Route path="/perfil" element={<UserProfile />} />
        <Route path="/usuario/:userId" element={<PublicProfile />} />
        <Route
          path="/usuarios/categoria/:categoryId"
          element={<CategoryUsers />}
        ></Route>
      </Routes>
    </StoreProvider>
  );
}
