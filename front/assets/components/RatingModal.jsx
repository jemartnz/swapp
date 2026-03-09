import React, { useState } from "react";
import "../styles/RatingModal.css";
import { env } from "../../environ";

// helper token
const getCleanToken = () => {
  const raw = localStorage.getItem("token");
  return raw ? raw.replace(/^"|"$/g, "") : null;
};

const RatingModal = ({ show, onClose, ratedUser, onSubmit }) => {
  const [score, setScore] = useState(0);
  const [comment, setComment] = useState("");
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState(null);

  if (!show) return null;

  const handleSubmit = async () => {
    // minimal local validation
    if (!ratedUser || !ratedUser.exchange_id) {
      setMessage({ tipo: "error", texto: "Falta el id del intercambio." });
      return;
    }
    if (!score || Number(score) < 1 || Number(score) > 5) {
      setMessage({ tipo: "error", texto: "Selecciona una puntuación válida (1-5)." });
      return;
    }

    setLoading(true);
    try {
      const token = getCleanToken();
      if (!token) throw new Error("Token no encontrado");

      // authenticated user
      const rUser = await fetch(`${env.api}/api/auth/me`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!rUser.ok) throw new Error("No se pudo obtener usuario autenticado");
      const me = await rUser.json();

      const rater_id = me?.id ?? me?.id;
      if (!rater_id) throw new Error("Falta id del usuario autenticado");

      // exact body that backend expects
      const body = {
        exchange_id: ratedUser.exchange_id,
        rater_id,
        score: Number(score),
        comment,
      };

      const res = await fetch(`${env.api}/api/ratings`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(body),
      });

      // backend error handling
      let data = null;
      try { data = await res.json(); } catch (_) {}
      if (!res.ok) {
        const msg = (data && (data.error || data.mensaje)) || "Error al enviar puntuación";
        throw new Error(msg);
      }

      setMessage({ tipo: "success", texto: "Puntuación enviada correctamente." });

      // notify finalize and refresh
      onSubmit?.({
        score: Number(score),
        comment,
      });

      setTimeout(() => {
        setScore(0);
        setComment("");
        setMessage(null);
        setLoading(false);
        onClose();
      }, 800);
    } catch (err) {
      console.error("Error al enviar puntuación:", err);
      setMessage({ tipo: "error", texto: "Hubo un error al enviar la puntuación." });
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay">
      <div className="modal-contenido animate-fadeIn">
        <h3 className="modal-titulo">
          Califica a <span className="nombre-usuario">{ratedUser?.nombre || "el usuario"}</span>
        </h3>

        <div className="modal-estrellas">
          {[1, 2, 3, 4, 5].map((n) => (
            <span
              key={n}
              className={`estrella ${n <= score ? "activa" : ""}`}
              onClick={() => setScore(n)}
            >
              ★
            </span>
          ))}
        </div>

        <textarea
          className="modal-comentario"
          placeholder="Agrega un comentario (opcional)"
          value={comment}
          onChange={(e) => setComment(e.target.value)}
          maxLength={250}
        />

        {message && (
          <div className={`alert mt-3 ${message.tipo === "success" ? "alert-success" : "alert-danger"}`} role="alert">
            {message.texto}
          </div>
        )}

        <div className="modal-puntuacion-botones mt-4">
          <button className="btn-cancelar-puntuacion" onClick={onClose} disabled={loading}>
            Cancelar
          </button>
          <button className="btn-guardar-puntuacion" onClick={handleSubmit} disabled={loading}>
            {loading ? "Guardando..." : "Enviar"}
          </button>
        </div>
      </div>
    </div>
  );
};

export default RatingModal;
