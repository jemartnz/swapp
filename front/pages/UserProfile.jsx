import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router";
import Navbar from "../assets/components/Navbar";
import Footer from "../assets/components/Footer";
import "../assets/styles/UserProfile.css";
import { env } from "../environ";
import { useStore } from "../hooks/useStore";
import CropperModal from "../assets/components/CropperModal";
import AddSkillModal from "../assets/components/AddSkillModal";
import MessagingButton from "../assets/components/MessagingButton";
import ChatModal from "../assets/components/ChatModal";
import RatingModal from "../assets/components/RatingModal";
import ExchangeModal from "../assets/components/ExchangeModal";

function UserProfile() {
  const { _, dispatch } = useStore();
  const [user, setUser] = useState(null);
  const [activeSection, setActiveSection] = useState("datos");

  // Personal data
  const [editing, setEditing] = useState(false);
  const [formData, setFormData] = useState({});
  const [msg, setMsg] = useState({});

  // Image / cropper
  const [tempImage, setTempImage] = useState(null);
  const [showCropper, setShowCropper] = useState(false);

  // Skills
  const [showSkillModal, setShowSkillModal] = useState(false);
  const [editingSkills, setEditingSkills] = useState(false);


  // Messaging
  const [showChatModal, setShowChatModal] = useState(false);

  // Rating
  const [showRatingModal, setShowRatingModal] = useState(false);
  const [ratedUser, setRatedUser] = useState(null);

  // Exchanges
  const [exchanges, setExchanges] = useState([]);
  const [showExchangeModal, setShowExchangeModal] = useState(false);

  const navigate = useNavigate();

  const me = user;

  // Load user
  useEffect(() => {
    const rawToken = localStorage.getItem("token");
    const userToken = rawToken ? rawToken.replace(/^"|"$/g, "") : null;
    const googleUser = localStorage.getItem("user");

    if (!userToken && !googleUser) {
      navigate("/login");
      return;
    }

    // If coming from Google
    if (googleUser) {
      const data = JSON.parse(googleUser);
      setUser({
        id: data.id,
        first_name: data.first_name,
        last_name: data.last_name,
        email: data.email,
        profile_picture: data.profile_picture,
        birth_date: null,
        gender: "",
        description: "",
        skills: [],
      });

      setFormData({
        first_name: data.first_name,
        last_name: data.last_name,
        email: data.email,
        profile_picture: data.profile_picture,
        birth_date: "",
        gender: "",
        description: "",
      });

      return;
    }

    const fetchUser = async () => {
      try {
        const response = await fetch(`${env.api}/api/auth/me`, {
          method: "GET",
          headers: {
            Authorization: `Bearer ${userToken}`,
            Accept: "application/json",
          },
        });

        if (!response.ok) {
          localStorage.removeItem("token");
          console.error("Error al obtener usuario:", response.status);
          return;
        }

        const data = await response.json();
        setUser(data);
        setFormData(data);
        dispatch({ type: "SET_USER", payload: data });
      } catch (error) {
        console.error("Error al cargar usuario:", error);
      }
    };

    fetchUser();
  }, [dispatch, navigate]);

// Load exchanges once user is authenticated
useEffect(() => {
  if (user?.id) fetchExchanges();
}, [user]);


// helper
const getCleanToken = () => {
  const raw = localStorage.getItem("token");
  return raw ? raw.replace(/^"|"$/g, "") : null;
};


  // Personal data handlers
  const handleChange = (e) =>
    setFormData({ ...formData, [e.target.name]: e.target.value });


// Save personal data using user endpoints
const handleSave = async () => {
  try {
    // Minimal validation
    if (!formData.first_name || !formData.last_name || !formData.email) {
      setMsg({ tipo: "danger", contenido: "Por favor completa todos los campos obligatorios." });
      return;
    }

    // Build date ONLY if day/month/year present
    let finalDate = null;
    if (formData.day && formData.month && formData.year) {
      finalDate = `${formData.year}-${String(formData.month).padStart(2, "0")}-${String(formData.day).padStart(2, "0")}`;
    }

    // Build payload without day/month/year
    const { day, month, year, ...rest } = formData;
    const payload = { ...rest };

    if (finalDate) {
      payload.birth_date = finalDate;
    } else {

      delete payload.birth_date;

    }


    const token = getCleanToken();

    const resp = await fetch(`${env.api}/api/users/${user.id}`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: JSON.stringify(payload),
    });

    if (!resp.ok) {
      const errText = await resp.text();
      console.error("PUT /api/users/:id failed:", resp.status, errText);
      throw new Error(`Error HTTP ${resp.status}`);
    }

    const data = await resp.json();

    // Update state
    setUser(data?.updated ?? user);
    dispatch({ type: "SET_USER", payload: data?.updated ?? user });
    setEditing(false);
    setMsg({ tipo: "success", contenido: data?.message || "Cambios guardados correctamente." });
  } catch (e) {
    console.error("Error al guardar:", e);
    setMsg({ tipo: "danger", contenido: "No se pudo guardar la información." });
  }
};


  // Profile picture
  const handleEditPhoto = () => {
    const input = document.createElement("input");
    input.type = "file";
    input.accept = "image/*";

    input.onchange = (e) => {
      const file = e.target.files[0];
      if (!file) return;
      const url = URL.createObjectURL(file);
      setTempImage(url);
      setShowCropper(true);
    };

    input.click();
  };



// DELETE SKILL FROM USER (dissociate)
const handleRemoveSkill = async (skillId) => {
  try {
    const res = await fetch(
      `${env.api}/api/users/${user.id}/skill`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Accept: "application/json",
        },
        body: JSON.stringify({ disassociate: skillId }),
      }
    );

    if (!res.ok) {
      throw new Error("Error al desasociar habilidad");
    }

    // Refresh user data from backend
    const ref = await fetch(`${env.api}/api/users/${user.id}`);
    if (!ref.ok) throw new Error("Error al refrescar usuario");
    const data = await ref.json();

    setUser(data);
    setMsg({
      tipo: "success",
      contenido: "Habilidad eliminada correctamente.",
    });
  } catch (error) {
    console.error("Error al eliminar habilidad:", error);
    setMsg({
      tipo: "danger",
      contenido: "No se pudo eliminar la habilidad.",
    });
  }
};



// SAVE SKILL CHANGES
const handleSaveSkillChanges = () => {
  setEditingSkills(false);
  setMsg({
    tipo: "success",
    contenido: "Cambios guardados correctamente.",
  });
};


// helpers
const fetchUserById = async (id) => {
  if (!id) return null;
  try {
    const r = await fetch(`${env.api}/api/users/${id}`, {
      headers: { Accept: "application/json" },
    });
    if (!r.ok) return null;
    return await r.json();
  } catch {
    return null;
  }
};

// Exchanges - get all for authenticated user (resolves offerer/demander)
const fetchExchanges = async () => {
  try {
    if (!user?.id) return;

    const res = await fetch(
      `${env.api}/api/exchanges/user/${user.id}`,
      { headers: { Accept: "application/json" } }
    );
    if (!res.ok) throw new Error("Error al obtener intercambios");

    const raw = await res.json();
    const list = Array.isArray(raw) ? raw : [];

    // collect unique user ids to minimize calls
    const ids = new Set();
    for (const item of list) {
      if (item.offerer_id) ids.add(item.offerer_id);
      if (item.demander_id) ids.add(item.demander_id);
    }

    // fetch users in parallel
    const idsArr = Array.from(ids);
    const users = await Promise.all(idsArr.map((id) => fetchUserById(id)));
    const userMap = new Map(idsArr.map((id, idx) => [id, users[idx]]));

    const normalized = list.map((item) => {
      const offerer = item.offerer_id ? userMap.get(item.offerer_id) : null;
      const demander = item.demander_id ? userMap.get(item.demander_id) : null;

      const offererName = offerer
        ? `${offerer.first_name || ""} ${offerer.last_name || ""}`.trim() || `#${item.offerer_id}`
        : item.offerer_id ? `#${item.offerer_id}` : "—";

      const demanderName = demander
        ? `${demander.first_name || ""} ${demander.last_name || ""}`.trim() || `#${item.demander_id}`
        : item.demander_id ? `#${item.demander_id}` : "—";

      return {
        ...item,
        offerer_user: offerer,
        demander_user: demander,
        offerer_name: offererName,
        demander_name: demanderName,
      };
    });

    setExchanges(normalized);
  } catch (err) {
    console.error("Error al cargar intercambios:", err);
    setExchanges([]);
  }
};


// Exchange section
const handleCompleteExchange = (exchange) => {
  const isDemander =
    exchange.demander_user?.id === user?.id ||
    exchange.demander_id === user?.id;

  const targetUser = isDemander
    ? exchange.offerer_user || { first_name: "Usuario" }
    : exchange.demander_user || { first_name: "Usuario" };

  setRatedUser({
    exchange_id: exchange.id,
    nombre: targetUser?.first_name || "Usuario",
  });

  setShowRatingModal(true);
};



// Delete an exchange
const handleDeleteExchange = async (exchangeId) => {
  try {
    const res = await fetch(`${env.api}/api/exchanges/${exchangeId}`, {
      method: "DELETE",
      headers: { "Content-Type": "application/json" },
    });

    if (!res.ok) throw new Error("Error al eliminar el intercambio");

    setMsg({
      tipo: "success",
      contenido: "✅ Intercambio eliminado correctamente.",
    });

    // Refresh exchange list
    fetchExchanges();

    setTimeout(() => {
      setMsg(null);
    }, 3000);
  } catch (err) {
    console.error("Error eliminando intercambio:", err);
    setMsg({
      tipo: "danger",
      contenido: "❌ No se pudo eliminar el intercambio.",
    });

    setTimeout(() => {
      setMsg(null);
    }, 4000);
  }
};

// Complete and refresh
const handleSubmitRating = async (_payload) => {
  try {
    const token = getCleanToken();
    const id = ratedUser?.exchange_id;
    if (!id) throw new Error("Falta exchange_id");

    const r = await fetch(`${env.api}/api/exchanges/${id}/complete`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
    });

    if (!r.ok) {
      const txt = await r.text();
      throw new Error(`Error al finalizar intercambio: ${r.status} ${txt}`);
    }

    await fetchExchanges();
    setMsg({ tipo: "success", contenido: "Intercambio finalizado correctamente." });
    setTimeout(() => setMsg(null), 3000);
  } catch (err) {
    console.error(err);
    setMsg({ tipo: "danger", contenido: "No se pudo finalizar el intercambio." });
    setTimeout(() => setMsg(null), 3000);
  } finally {
    setShowRatingModal(false);
  }
};


const openRatingModal = (exchange) => {
  setRatedUser({
    exchange_id: exchange.id,
    nombre:
      exchange.demander_user?.first_name ||
      exchange.offerer_user?.first_name ||
      "Usuario",
  });
  setShowRatingModal(true);
};




  if (!user) return <p className="text-center mt-5">Cargando perfil...</p>;

  return (
    <>
      <Navbar />

      <div className="container-fluid perfil-container py-5">
        <div className="row justify-content-center">
          {/* Sidebar */}
          <div className="col-12 col-md-3 perfil-sidebar text-center p-4">
            <div className="perfil-avatar-container">
              <img
                src={
                  user.profile_picture && user.profile_picture.trim() !== ""
                    ? user.profile_picture
                    : "/swapp-profile.png"
                }
                alt="Foto de perfil"
                className="perfil-avatar mb-3"
              />
              <button className="btn btn-editar-foto mb-2" onClick={handleEditPhoto}>
                📷 Editar Foto
              </button>
              <h4 className="perfil-nombre mb-4">
                {user.first_name} {user.last_name}
              </h4>
            </div>

            <div className="perfil-secciones mt-4">
              <button
                className={`list-group-item ${activeSection === "datos" ? "active" : ""}`}
                onClick={() => setActiveSection("datos")}
              >
                Datos Personales
              </button>

              <div className="perfil-divider"></div>

              <button
                className={`list-group-item ${activeSection === "habilidades" ? "active" : ""}`}
                onClick={() => {
                  setActiveSection("habilidades");
                  // refresh to get updated descriptions from backend
                  fetch(`${env.api}/api/users/${user.id}`)
                    .then((r) => r.json())
                    .then((d) => setUser(d))
                    .catch((e) => console.error("Error refrescando usuario:", e));
                }}
              >
                Habilidades
              </button>

              <div className="perfil-divider"></div>

              <button
                className={`list-group-item ${activeSection === "intercambios" ? "active" : ""}`}
                onClick={() => setActiveSection("intercambios")}
              >
                Intercambios
              </button>
            </div>
          </div>

          {/* Content */}
          <div className="col-12 col-md-8 perfil-content p-4">
            {activeSection === "datos" ? (
              <>
                <h2 className="text-dark fw-bold mb-4 text-center">Datos Personales</h2>

                <form className="row g-3">
                  {/* First Name */}
                  <div className="col-md-6">
                    <label className="form-label">Nombre</label>
                    <input
                      type="text"
                      className="form-control"
                      name="first_name"
                      value={formData.first_name || ""}
                      onChange={handleChange}
                      disabled={!editing}
                    />
                  </div>

                  {/* Last Name */}
                  <div className="col-md-6">
                    <label className="form-label">Apellidos</label>
                    <input
                      type="text"
                      className="form-control"
                      name="last_name"
                      value={formData.last_name || ""}
                      onChange={handleChange}
                      disabled={!editing}
                    />
                  </div>

                  {/* Email */}
                  <div className="col-md-6">
                    <label className="form-label">Correo electrónico</label>
                    <input
                      type="email"
                      className="form-control"
                      name="email"
                      value={formData.email || ""}
                      onChange={handleChange}
                      disabled={!editing}
                    />
                  </div>

                  {/* Birth date with Day/Month/Year */}
                  <div className="col-md-6">
                    <label className="form-label">Fecha de nacimiento</label>
                    {editing ? (
                      <div className="d-flex" style={{ gap: "10px" }}>
                        {/* Day */}
                        <select
                          className="form-select"
                          name="day"
                          value={formData.day || ""}
                          onChange={handleChange}
                        >
                          <option value="">Día</option>
                          {[...Array(31)].map((_, i) => (
                            <option key={i + 1} value={i + 1}>
                              {i + 1}
                            </option>
                          ))}
                        </select>

                        {/* Month */}
                        <select
                          className="form-select"
                          name="month"
                          value={formData.month || ""}
                          onChange={handleChange}
                        >
                          <option value="">Mes</option>
                          {[
                            "Enero",
                            "Febrero",
                            "Marzo",
                            "Abril",
                            "Mayo",
                            "Junio",
                            "Julio",
                            "Agosto",
                            "Septiembre",
                            "Octubre",
                            "Noviembre",
                            "Diciembre",
                          ].map((monthName, i) => (
                            <option key={i + 1} value={i + 1}>
                              {monthName}
                            </option>
                          ))}
                        </select>

                        {/* Year */}
                        <select
                          className="form-select"
                          name="year"
                          value={formData.year || ""}
                          onChange={handleChange}
                        >
                          <option value="">Año</option>
                          {Array.from(
                            { length: 100 },
                            (_, i) => new Date().getFullYear() - i
                          ).map((yr) => (
                            <option key={yr} value={yr}>
                              {yr}
                            </option>
                          ))}
                        </select>
                      </div>
                    ) : (
                      <input
                        type="text"
                        className="form-control"
                        value={user.birth_date?.split("T")[0] || ""}
                        disabled
                      />
                    )}
                  </div>

                  {/* Gender */}
                  <div className="col-md-6">
                    <label className="form-label">Género</label>
                    {editing ? (
                      <select
                        name="gender"
                        className="form-select"
                        value={formData.gender || ""}
                        onChange={handleChange}
                      >
                        <option value="">Seleccionar...</option>
                        <option value="Hombre">Hombre</option>
                        <option value="Mujer">Mujer</option>
                        <option value="Personalizado">Personalizado</option>
                      </select>
                    ) : (
                      <input
                        type="text"
                        className="form-control"
                        value={user.gender}
                        disabled
                      />
                    )}
                  </div>

                  {/* Description */}
                  <div className="col-12">
                    <label className="form-label">Descripción</label>
                    <textarea
                      className="form-control"
                      name="description"
                      value={formData.description || ""}
                      onChange={handleChange}
                      disabled={!editing}
                      rows="3"
                    />
                  </div>

                  {/* Message */}
                  {Object.keys(msg).length > 0 && (
                    <div className={`alert alert-${msg.tipo}`} role="alert">
                      {msg.contenido}
                    </div>
                  )}

                  {/* Save/Edit button */}
                  <div className="col-12 text-center mt-4">
                    <button
                      type="button"
                      className="btn btn-lg perfil-accion-btn"
                      onClick={editing ? handleSave : () => setEditing(true)}
                    >
                      {editing ? "Guardar Cambios" : "Editar Información"}
                    </button>
                  </div>
                </form>
              </>
              ) : activeSection === "habilidades" ? (
                <>
                  <h2 className="fw-bold mb-4 text-center">Habilidades</h2>

                    <div className="habilidades-contenedor">
                      {user.skills && user.skills.length > 0 ? (
                        user.skills.map((skill, index) => (
                          <div key={index} className="habilidad-card">
                            <div className="d-flex justify-content-between align-items-center">
                              <h5 className="m-0" style={{ color: "var(--naranja)" }}>
                                {skill.name}
                              </h5>
                              {editingSkills && (
                                <button
                                  className="btn btn-outline-danger btn-sm"
                                  onClick={() => handleRemoveSkill(skill.id)}
                                >
                                  ✖
                                </button>
                              )}
                            </div>
                            <p className="text-muted mt-2 mb-0">
                              {skill.description && skill.description.trim() !== ""
                                ? skill.description
                                : "Sin descripción"}
                            </p>
                          </div>
                        ))
                      ) : (
                        <p className="text-muted text-center">
                          Aún no has agregado habilidades.
                        </p>
                      )}
                    </div>

                    {/* Alert below the list and above the buttons */}
                    {msg && msg.tipo && (
                      <div className={`alert alert-${msg.tipo} text-center mt-3`} role="alert">
                        {msg.contenido}
                      </div>
                    )}

                    <div className="d-flex justify-content-center gap-3 mt-4 flex-wrap">
                      {!editingSkills ? (
                        <button className="btn-naranja" onClick={() => setEditingSkills(true)}>
                          ✏️ Editar habilidades
                        </button>
                      ) : (
                        <>
                          <button className="btn-agregar" onClick={() => setShowSkillModal(true)}>
                            ➕ Agregar habilidad
                          </button>

                          <button className="btn-naranja" onClick={handleSaveSkillChanges}>
                            💾 Guardar cambios
                          </button>

                          <button className="btn-oscuro" onClick={() => setEditingSkills(false)}>
                            Cancelar
                          </button>
                        </>
                      )}
                    </div>


                  {showSkillModal && (
                    <AddSkillModal
                      user={user}
                      onClose={() => setShowSkillModal(false)}
                      onSuccess={() => {
                        setShowSkillModal(false);
                        // refresh user to see new skill
                        fetch(`${env.api}/api/users/${user.id}`)
                          .then((r) => r.json())
                          .then((d) => setUser(d))
                          .catch((e) => console.error("Error al actualizar habilidades:", e));
                      }}
                    />
                  )}
                </>
              ) : (

                // Exchange Section
                <div className="seccion-intercambios">
                  <h2 className="fw-bold mb-4 text-center">Intercambios</h2>

                  <div className="text-center mb-4">
                    <button
                      className="btn-naranja"
                      onClick={() => setShowExchangeModal(true)}
                    >
                      Crear nuevo intercambio
                    </button>
                  </div>

                  <div className="tabla-intercambios-container">
                    <table className="tabla-intercambios">
                      <thead>
                        <tr>
                          <th>ID</th>
                          <th>Habilidad</th>
                          <th>Usuario oferta</th>
                          <th>Usuario demanda</th>
                          <th>Estado</th>
                          <th>Acción</th>
                        </tr>
                      </thead>

                      <tbody>
                        {exchanges.length === 0 ? (
                          <tr>
                            <td colSpan="6" className="text-center text-muted">
                              No tienes intercambios registrados.
                            </td>
                          </tr>
                        ) : (
                          exchanges.map((exchange) => {
                              const isCompleted = exchange.is_completed === true;
                              const isDemander =
                                exchange.demander_user?.id === me?.id ||
                                exchange.demander_id === me?.id;

                            return (
                              <tr key={exchange.id}>
                                <td>#{exchange.id}</td>
                                <td>{exchange.skill?.name || "—"}</td>
                                <td>{exchange.offerer_name || "—"}</td>
                                <td>{exchange.demander_name || "—"}</td>
                                <td>{isCompleted ? "Finalizado" : "Activo"}</td>

                                <td className="d-flex gap-2 justify-content-center flex-wrap">
                                  {isCompleted ? (
                                    <span className="text-success fw-semibold">
                                      Intercambio finalizado
                                    </span>
                                  ) : (
                                    <>
                                      {/* Only demander can complete */}
                                      {isDemander && (
                                        <button
                                          className="btn btn-oscuro btn-sm"
                                          onClick={() => handleCompleteExchange(exchange)}
                                        >
                                          Finalizar
                                        </button>
                                      )}

                                      {/* Anyone can delete */}
                                      <button
                                        className="btn btn-outline-danger btn-sm"
                                        onClick={() => handleDeleteExchange(exchange.id)}
                                      >
                                        Eliminar
                                      </button>
                                    </>
                                  )}
                                </td>
                              </tr>
                            );
                          })
                        )}
                      </tbody>
                    </table>
                  </div>
                </div>



            )}
          </div>
        </div>
      </div>

      {/* Modals */}

      {/* Cropper */}
      {showCropper && (
        <CropperModal
          image={tempImage}
          onClose={() => setShowCropper(false)}
          onCropDone={async (croppedBase64) => {
            setShowCropper(false);
            const blob = await (await fetch(croppedBase64)).blob();
            const fd = new FormData();
            fd.append("imagen", blob, "recorte.jpg");

            try {
              const userData = JSON.parse(localStorage.getItem("user"));
              const userId = userData?.id || user?.id;

              const res = await fetch(`${env.api}/api/users/${userId}/profile-picture`, {
                method: "POST",
                body: fd,
              });

              const data = await res.json();
              if (res.ok) {
                setUser((prev) => ({
                  ...prev,
                  profile_picture: data.profile_picture,
                }));
                const img = document.querySelector(".perfil-avatar");
                if (img) img.src = data.profile_picture;
                setMsg({
                  tipo: "success",
                  contenido: "Foto actualizada correctamente",
                });
              } else {
                throw new Error(data.error || "Error al subir la foto");
              }
            } catch (err) {
              console.error(err);
              setMsg({
                tipo: "danger",
                contenido: "No se pudo subir la imagen recortada",
              });
            }
          }}
        />
      )}

      {/* Rating */}
      {showRatingModal && (
        <RatingModal
          show={showRatingModal}
          onClose={() => setShowRatingModal(false)}
          ratedUser={ratedUser}
          onSubmit={handleSubmitRating}
        />
      )}



      {/* Floating button + Messaging */}
      <MessagingButton onClick={() => setShowChatModal(true)} />
      {showChatModal && (
        <ChatModal
          show={showChatModal}
          close={() => setShowChatModal(false)}
        />
      )}


      {showExchangeModal && (
      <ExchangeModal
        show={showExchangeModal}
        close={() => {
          setShowExchangeModal(false);
          fetchExchanges(); // refresh list on close
        }}
      />
    )}

      <Footer />
    </>
  );
}

export default UserProfile;
