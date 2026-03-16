import React, { useState } from "react";
import "../assets/styles/Login.css";
import { Link, useNavigate } from "react-router";
import { GoogleLogin } from "@react-oauth/google";
import { env } from "../environ";
import { useStore } from "../hooks/useStore";

const Login = () => {
  const { _, dispatch } = useStore();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const saveTokensAndRedirect = (token, refreshToken) => {
    localStorage.setItem("token", JSON.stringify(token));
    if (refreshToken) localStorage.setItem("refresh_token", refreshToken);
    dispatch({ type: "SET_TOKEN", payload: token });
    navigate("/perfil");
  };

  const handleGoogleSuccess = async (credentialResponse) => {
    try {
      const response = await fetch(`${env.api}/api/auth/google/verify`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id_token: credentialResponse.credential }),
      });

      if (!response.ok) throw new Error("Error de autenticación con Google");

      const data = await response.json();
      const token = data?.data?.token;
      const refreshToken = data?.data?.refresh_token;

      if (token) {
        saveTokensAndRedirect(token, refreshToken);
      } else {
        setError("No se pudo iniciar sesión con Google.");
      }
    } catch (err) {
      console.error("Error Google login:", err);
      setError("Error al iniciar sesión con Google");
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!email || !password) {
      setError("Por favor completa todos los campos.");
      return;
    }

    setError("");

    try {
      const response = await fetch(`${env.api}/api/auth/login`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Accept: "application/json",
        },
        body: JSON.stringify({
          email: email,
          password: password,
        }),
      });

      if (!response.ok) {
        throw new Error("Error al conectar con el servidor");
      }
      const data = await response.json();
      const token = data?.data?.token;
      const refreshToken = data?.data?.refresh_token;

      if (token) {
        saveTokensAndRedirect(token, refreshToken);
      } else {
        setError("Correo o contraseña incorrectos.");
      }
    } catch (err) {
      console.error("Error al iniciar sesión:", err);
      setError("Error al iniciar sesión");
    }
  };

  return (
    <div className="login-page-swapp container-fluid">
      <div className="row justify-content-center align-items-center">
        {/* Columna izquierda - Logo */}
        <div className="col-12 col-md-5 d-flex flex-column justify-content-center align-items-center mb-5 mb-md-0">
          <Link className="logo-login-container" to="/">
            <img
              src="swapp sin fondo.webp"
              alt="Swapp"
              className="logo-login"
            />
          </Link>

          <h4 className="slogan-login">¡Donde todo, tiene otro valor!</h4>
        </div>

        {/* Columna derecha - Formulario */}
        <div className="col-12 col-md-7 d-flex justify-content-center">
          <div className="login-box-swapp">
            <h5 className="form-title-login fw-bold mb-3">
              Inicia sesión en <span className="text-naranja">Swapp</span>
            </h5>

            <form onSubmit={handleSubmit}>
              {/* Correo */}
              <div className="mb-3">
                <label className="form-label">Correo electrónico</label>
                <input
                  type="email"
                  className="form-control login-input-swapp"
                  placeholder="Ingresa tu correo"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                />
              </div>

              {/* Contraseña */}
              <div className="mb-3">
                <label className="form-label">Contraseña</label>
                <input
                  type="password"
                  className="form-control login-input-swapp"
                  placeholder="Ingresa tu contraseña"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
              </div>

              {error && (
                <div className="login-error-swapp text-danger mb-3">
                  {error}
                </div>
              )}

              {/* Botón principal */}
              <button type="submit" className="btn-login-swapp fw-bold w-100">
                Iniciar sesión
              </button>
            </form>

            <div className="text-center mt-3 mb-2">
              <span className="text-muted" style={{ fontSize: "0.85rem" }}>— O continúa con —</span>
            </div>

            <div className="d-flex justify-content-center mb-3">
              <GoogleLogin
                onSuccess={handleGoogleSuccess}
                onError={() => setError("Error al iniciar sesión con Google")}
                locale="es"
                text="signin_with"
                shape="rectangular"
              />
            </div>

            <p className="mt-3 text-center">
              ¿No tienes cuenta?{" "}
              <a href="/registro" className="enlace-login-swapp">
                Regístrate aquí
              </a>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;
