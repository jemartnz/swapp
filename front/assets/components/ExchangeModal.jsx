import React, { useEffect, useState } from "react";
import "../styles/ExchangeModal.css";
import { env } from "../../environ";

export default function ExchangeModal({ show, close }) {
  const [me, setMe] = useState(null);
  const [categories, setCategories] = useState([]);
  const [skills, setSkills] = useState([]);
  const [categoryId, setCategoryId] = useState("");
  const [skillId, setSkillId] = useState("");
  const [msg, setMsg] = useState(null);
  const [sending, setSending] = useState(false);

  // === Helper to clean token ===
  const getCleanToken = () => {
    const raw = localStorage.getItem("token");
    return raw ? raw.replace(/^"|"$/g, "") : null;
  };

  // === Load authenticated user ===
  useEffect(() => {
    if (!show) return;
    const token = getCleanToken();
    if (!token) return;

    fetch(`${env.api}/api/auth/me`, {
      headers: { Authorization: `Bearer ${token}`, Accept: "application/json" },
    })
      .then((r) => (r.ok ? r.json() : Promise.reject()))
      .then(setMe)
      .catch((e) => console.error("Error al cargar usuario actual:", e));
  }, [show]);

  // === Load categories ===
  useEffect(() => {
    if (!show) return;
    fetch(`${env.api}/api/categories`, { headers: { Accept: "application/json" } })
      .then((r) => (r.ok ? r.json() : Promise.reject()))
      .then((data) => setCategories(data || []))
      .catch((e) => console.error("Error cargando categorías:", e));
  }, [show]);

  // === Handle category selection ===
  const handleCategoryChange = (e) => {
    const id = parseInt(e.target.value);
    setCategoryId(id);
    const category = categories.find((c) => c.id === id);
    if (category) {
      setSkills(category.skills || []);
    } else {
      setSkills([]);
    }
    setSkillId("");
  };

  // === Cancel or close modal ===
  const handleClose = () => {
    setMsg(null);
    setCategoryId("");
    setSkillId("");
    close();
  };

  // === Create new exchange ===
  const handleSubmit = async () => {
    if (!me?.id) {
      setMsg({ tipo: "danger", contenido: "⚠️ No hay sesión activa." });
      return;
    }
    if (!skillId) {
      setMsg({ tipo: "danger", contenido: "⚠️ Selecciona una habilidad." });
      return;
    }

    setSending(true);
    try {
      const body = {
        offerer_id: me.id,
        skill_id: skillId,
      };

      const res = await fetch(`${env.api}/api/exchanges`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });

      if (!res.ok) throw new Error("Error al crear el intercambio");
      await res.json();

      setMsg({
        tipo: "success",
        contenido: "✅ Intercambio creado correctamente.",
      });

      setTimeout(() => handleClose(), 1500);
    } catch (error) {
      console.error("Error al crear intercambio:", error);
      setMsg({
        tipo: "danger",
        contenido: "❌ No se pudo crear el intercambio.",
      });
    } finally {
      setSending(false);
    }
  };

  if (!show) return null;

  return (
    <div
      className="modal fade show d-block fondo-modal"
      tabIndex="-1"
      role="dialog"
      aria-modal="true"
    >
      <div className="modal-dialog modal-dialog-centered" role="document">
        <div className="modal-content">
          {/* === HEADER === */}
          <div className="modal-header bg-naranja text-white">
            <h5 className="modal-title">Crear nuevo intercambio</h5>
            <button
              type="button"
              className="btn-close btn-close-white"
              onClick={handleClose}
            />
          </div>

          {/* === BODY === */}
          <div className="modal-body">
            <label className="form-label mt-2">Categoría</label>
            <select
              className="form-select"
              value={categoryId}
              onChange={handleCategoryChange}
            >
              <option value="">Selecciona una categoría</option>
              {categories.map((cat) => (
                <option key={cat.id} value={cat.id}>
                  {cat.name}
                </option>
              ))}
            </select>

            <label className="form-label mt-3">Habilidad</label>
            <select
              className="form-select"
              value={skillId}
              onChange={(e) => setSkillId(parseInt(e.target.value))}
              disabled={!categoryId}
            >
              <option value="">Selecciona una habilidad</option>
              {skills.map((skill) => (
                <option key={skill.id} value={skill.id}>
                  {skill.name}
                </option>
              ))}
            </select>

            {msg && (
              <div className={`alert mt-3 alert-${msg.tipo}`} role="alert">
                {msg.contenido}
              </div>
            )}
          </div>

          {/* === FOOTER === */}
          <div className="modal-footer d-flex justify-content-center">
            <button
              className="btn btn-outline-dark"
              onClick={handleClose}
              disabled={sending}
            >
              Cancelar
            </button>
            <button
              className="btn btn-naranja"
              onClick={handleSubmit}
              disabled={sending}
            >
              {sending ? "Enviando..." : "Crear intercambio"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
