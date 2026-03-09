import React, { useState, useEffect } from "react";
import "../styles/AddSkillModal.css";
import { env } from "../../environ";

const AddSkillModal = ({ user, onClose, onSuccess }) => {
  const [categories, setCategories] = useState([]);
  const [skills, setSkills] = useState([]);
  const [categoryId, setCategoryId] = useState("");
  const [skillId, setSkillId] = useState("");
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState(null);

  // Load categories when modal opens
  useEffect(() => {
    fetch(`${env.api}/api/categories`)
      .then((res) => res.json())
      .then((data) => setCategories(data))
      .catch((err) => console.error("Error al cargar categorías:", err));
  }, []);

  // Update skills list when category is selected
  const handleCategoryChange = (e) => {
    const id = parseInt(e.target.value);
    setCategoryId(id);
    const category = categories.find((c) => c.id === id);
    if (category) {
      setSkills(category.skills);
    } else {
      setSkills([]);
    }
    setSkillId("");
  };

  // Add skill to user
  const handleAdd = async () => {
    if (!skillId) {
      setMessage({ tipo: "error", texto: "Selecciona una habilidad" });
      return;
    }

    setLoading(true);
    try {
      const body = { associate: skillId };

      const response = await fetch(
        `${env.api}/api/users/${user.id}/skill`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Accept: "application/json",
          },
          body: JSON.stringify(body),
        }
      );

      const data = await response.json();

      if (response.ok) {
        setMessage({
          tipo: "success",
          texto: "✅ Habilidad agregada correctamente",
        });
        setTimeout(() => {
          onSuccess && onSuccess();
          onClose();
        }, 1200);
      } else {
        setMessage({
          tipo: "error",
          texto: data.msj || "No se pudo agregar la habilidad",
        });
      }
    } catch (error) {
      console.error("Error al agregar habilidad:", error);
      setMessage({
        tipo: "error",
        texto: "❌ Error en la conexión con el servidor",
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay">
      <div className="modal-agregar-habilidad animate-fadeIn">
        <h3 className="text-center fw-bold mb-3">Agregar Habilidad</h3>

        {/* Category Selection */}
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

        {/* Skill Selection */}
        <label className="form-label mt-3">Habilidad</label>
        <select
          className="form-select"
          value={skillId}
          onChange={(e) => setSkillId(parseInt(e.target.value))}
        >
          <option value="">Selecciona una habilidad</option>
          {skills.map((skill) => (
            <option key={skill.id} value={skill.id}>
              {skill.name}
            </option>
          ))}
        </select>

        {/* Messages */}
        {message && (
          <div
            className={`alert mt-3 ${
              message.tipo === "success" ? "alert-success" : "alert-error"
            }`}
          >
            {message.texto}
          </div>
        )}

        {/* Buttons */}
        <div className="modal-buttons mt-4 d-flex justify-content-between">
          <button className="btn-oscuro" onClick={onClose}>
            Cancelar
          </button>
          <button
            className="btn-naranja"
            onClick={handleAdd}
            disabled={loading}
          >
            {loading ? "Guardando..." : "Agregar"}
          </button>
        </div>
      </div>
    </div>
  );
};

export default AddSkillModal;
