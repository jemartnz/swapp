import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import Navbar from "../assets/components/Navbar";
import Footer from "../assets/components/Footer";
import ChatModal from "../assets/components/ChatModal";
import ExchangeModal from "../assets/components/ExchangeModal";
import "../assets/styles/PublicProfile.css";
import { env } from "../environ";

  function PublicProfile() {
    const { userId } = useParams();
    const navigate = useNavigate();

    // Main states
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [showModal, setShowModal] = useState(false);
    const [showExchangeModal, setShowExchangeModal] = useState(false);
    const [msg, setMsg] = useState(null);


    // Helper to get authenticated user
    const getCurrentUser = async () => {
      const rawToken = localStorage.getItem("token");
      const token = rawToken ? rawToken.replace(/^"|"$/g, "") : null;
      if (!token) return null;

      try {
        const res = await fetch(`${env.api}/api/auth/me`, {
          method: "GET",
          headers: {
            Authorization: `Bearer ${token}`,
            Accept: "application/json",
          },
        });
        if (!res.ok) return null;
        const data = await res.json();
        return data.data || data;
      } catch (err) {
        console.error("Error obteniendo usuario actual:", err);
        return null;
      }
    };


    // Exchanges created by the public user
    const [exchanges, setExchanges] = useState([]);

    // Get user data
    useEffect(() => {
      const fetchUser = async () => {
        try {
          const res = await fetch(`${env.api}/api/users/${userId}`);
          if (!res.ok) throw new Error("Error al obtener usuario");
          const data = await res.json();
          setUser(data.data || data);
        } catch (err) {
          console.error(err);
          setError("No se pudo cargar el perfil del usuario.");
        } finally {
          setLoading(false);
        }
      };
      fetchUser();
    }, [userId]);

    // Get exchanges created by this user (offerer)
    useEffect(() => {
      if (!userId) return;

      const fetchExchanges = async () => {
        try {
          const res = await fetch(
            `${env.api}/api/exchanges/offerer/${userId}`,
            {
              method: "GET",
              headers: {
                Accept: "application/json",
                "Content-Type": "application/json",
              },
            }
          );

          const text = await res.text();

          if (res.status === 404) {
            console.warn("Usuario sin intercambios.");
            setExchanges([]);
            return;
          }

          if (!res.ok) throw new Error(`HTTP ${res.status}: ${text}`);

          const data = JSON.parse(text);
          setExchanges(Array.isArray(data.data) ? data.data : []);
        } catch (err) {
          console.error("Error al cargar intercambios:", err);
          setExchanges([]);
        }


      };

      fetchExchanges();
    }, [userId]);


    // Contact
    const handleContact = () => {
      const localUser = localStorage.getItem("usuario");

      if (!localUser) {
        alert("⚠️ Debes iniciar sesión para contactar con otros usuarios.");
        navigate("/login");
        return;
      }

      // open modal instead of alert
      setShowModal(true);
    };


// Join an exchange
    const handleJoin = async (exchangeId) => {
      try {
        const me = await getCurrentUser(); // get current user via /api/auth/me

        if (!me?.id) {
          setMsg({
            tipo: "warning",
            contenido: "⚠️ Debes iniciar sesión para concretar un intercambio.",
          });
          setTimeout(() => setMsg(null), 4000);
          return;
        }

        const token = localStorage.getItem("token")?.replace(/^"|"$/g, "");

        // Correct field per backend
        const body = {
          user_id: me.id,
        };

        const res = await fetch(`${env.api}/api/exchanges/join/${exchangeId}`, {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
            ...(token ? { Authorization: `Bearer ${token}` } : {}),
          },
          body: JSON.stringify(body),
        });

        const data = await res.json();

        if (!res.ok) throw new Error(data.error || "Error al unirse al intercambio");

        // Show real backend message
        setMsg({
          tipo: "success",
          contenido: `✅ ${data.mensaje || "Intercambio concretado correctamente."}`,
        });

        setTimeout(() => setMsg(null), 3000);
      } catch (err) {
        console.error("Error uniendo al intercambio:", err);
        setMsg({
          tipo: "danger",
          contenido: "❌ No se pudo concretar el intercambio.",
        });
        setTimeout(() => setMsg(null), 4000);
      }
    };



    if (loading)
      return (
        <div className="d-flex flex-column justify-content-center align-items-center">
          <div
            className="spinner-border"
            style={{ color: "#ff7517" }}
            role="status"
          >
            <span className="visually-hidden"></span>
          </div>
          <h4 className="mt-3">Cargando perfil...</h4>
        </div>
      );

    if (error) return <p className="text-center mt-5 text-danger">{error}</p>;

  return (
    <>
      <Navbar />
      <div className="container-fluid perfil-publico-container py-5">
        <div className="row justify-content-center">
          {/* Sidebar */}
          <div className="col-12 col-md-3 perfil-publico-sidebar text-center p-4">
            <div className="perfil-publico-avatar-container">
              <img
                src={user.profile_picture || "/swapp-profile.png"}
                alt="Foto de perfil"
                className="perfil-publico-avatar mb-3"
                style={{
                  objectFit: "cover",
                  objectPosition: "center",
                  aspectRatio: "1/1",
                }}
              />
              <h4 className="perfil-publico-nombre mb-4">
                {user.first_name} {user.last_name}
              </h4>

              {/* Contact Button */}
              <button
                className="btn btn-naranja mb-2"
                onClick={() => setShowModal(true)}
              >
                Contactar
              </button>

            </div>
          </div>

          {/* Main content */}
          <div className="col-12 col-md-8 perfil-publico-content p-4 text-center">
            {/* Description */}
            <h2 className="text-dark fw-bold mb-4">Descripción</h2>
            <p>
              {user.description ? (
                user.description
              ) : (
                <span className="text-muted">
                  Este usuario no tiene una descripción.
                </span>
              )}
            </p>

            {/* Skills */}
            <h2 className="text-dark fw-bold mb-4">Habilidades</h2>
            {user.skills && user.skills.length > 0 ? (
              <div className="habilidades-contenedor">
                {user.skills.map((skill, index) => (
                  <div key={index} className="habilidad-card">
                    <div className="habilidad-nombre">
                      <h5>{skill?.name || "Sin nombre"}</h5>
                    </div>
                    <div className="habilidad-descripcion">
                      <p>{skill?.description || "Sin descripción"}</p>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-muted">
                Este usuario aún no ha agregado habilidades.
              </p>
            )}

            {/* Exchanges created by this user */}
            <h2 className="text-dark fw-bold mb-4 mt-5">Intercambios</h2>

            {exchanges.length === 0 ? (
              <p className="text-muted">
                Este usuario aún no ha creado intercambios.
              </p>
            ) : (
              <div className="tabla-intercambios-container mt-3">
                <table className="tabla-intercambios w-100">
                  <thead>
                    <tr>
                      <th>ID</th>
                      <th>Habilidad que busca</th>
                      <th>Estado</th>
                      <th>Acción</th>
                    </tr>
                  </thead>
                  <tbody>
                    {exchanges.map((exchange) => (
                      <tr key={exchange.id}>
                        <td>#{exchange.id}</td>
                        <td>{exchange.skill?.name || "—"}</td>
                        <td>{exchange.status || "Activo"}</td>
                        <td>
                          {localStorage.getItem("token") ? (
                            <button
                              className="btn btn-naranja btn-sm"
                              onClick={() => handleJoin(exchange.id)}
                            >
                              Concretar intercambio
                            </button>
                          ) : (
                            <span className="text-muted">
                              Inicia sesión para unirte
                            </span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
                {msg && msg.contenido && (
                  <div className={`alert alert-${msg.tipo} text-center mt-3`} role="alert">
                    {msg.contenido}
                  </div>
                )}
              </div>
            )}
          </div>
          </div>
          </div>


      {/* Chat modal */}
      {showModal && (
        <ChatModal
          show={showModal}
          close={() => setShowModal(false)}
          receiverId={user.id}
        />
      )}



      <Footer />
    </>
  );
}

export default PublicProfile;
