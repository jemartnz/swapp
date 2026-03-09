import "../assets/styles/Register.css";
import React, { useState, useEffect } from "react";
import { registerUser } from "../services/api";
import { Link, useNavigate } from "react-router";
import { env } from "../environ";

function Register() {
  const [formData, setFormData] = useState({
    first_name: "",
    last_name: "",
    day: "",
    month: "",
    year: "",
    gender: null,
    category_id: "",
    skill_id: null,
    description: "",
    email: "",
    password: "",
    accepts_terms: false,
  });
  const [categories, setCategories] = useState([
    { id: 0, name: "Elige tu Habilidad..." },
  ]);
  const [skills, setSkills] = useState([
    { id: 0, name: "Elige tu Habilidad..." },
  ]);
  const [showAlert, setShowAlert] = useState(false);
  const [errors, setErrors] = useState({});
  const [showModal, setShowModal] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    fetch(`${env.api}/api/categories`)
      .then((res) => res.json())
      .then((data) => setCategories(data));
  }, []);

  useEffect(() => {
    if (formData.category_id) {
      fetch(`${env.api}/api/skills/category/${formData.category_id}`)
        .then((res) => res.json())
        .then((data) => setSkills(data));
    } else {
      setSkills([]);
    }
  }, [formData.category_id]);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    const newValue = type === "checkbox" ? checked : value;

    if (formData.day && formData.month && formData.year) {
      setFormData({
        ...formData,
        birth_date: `${formData.year}-${formData.month}-${formData.day}`,
      });
    }

    setFormData((prevData) => ({
      ...prevData,
      [name]: type === "checkbox" ? checked : value,
    }));

    if (name === "category_id") {
      setFormData((prev) => ({
        ...prev,
        category_id: newValue,
        skill_id: "",
      }));
    } else {
      setFormData((prev) => ({
        ...prev,
        [name]: newValue,
      }));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    const newErrors = {};

    if (!formData.first_name.trim()) {
      newErrors.first_name = "El nombre es obligatorio";
    } else if (!/^[a-zA-ZÀ-ÿ\s]+$/.test(formData.first_name)) {
      newErrors.first_name = "El nombre sólo puede contener letras";
    }

    if (!formData.last_name.trim()) {
      newErrors.last_name = "Los apellidos son obligatorios";
    } else if (!/^[a-zA-ZÀ-ÿ\s]+$/.test(formData.last_name)) {
      newErrors.last_name = "Los apellidos sólo pueden contener letras";
    }

    if (!formData.email.trim()) {
      newErrors.email = "El correo es obligatorio";
    } else if (
      !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)
    ) {
      newErrors.email = "El correo no es válido";
    }

    if (!formData.password.trim()) {
      newErrors.password = "La contraseña es obligatoria";
    } else if (formData.password.length < 8) {
      newErrors.password = "Debe tener al menos 8 carácteres";
    }

    if (!formData.accepts_terms) {
      setShowAlert(true);
      newErrors.accepts_terms = "Debes aceptar las condiciones de uso.";
    } else {
      setShowAlert(false);
    }

    setErrors(newErrors);

    if (Object.keys(newErrors).length > 0) return;

    try {
      const data = await registerUser(formData);

      if (data) {
        setShowModal(true);
      }
    } catch (error) {
      alert("Hubo un error al registrar!");
    }
  };

  return (
    <div className="container">
      <div className="row d-flex flex-column flex-lg-row justify-content-center">
        <div className="col-12 col-lg-5 header-responsive d-flex flex-column justify-content-center align-items-center mb-5">
          <Link
            className="logo-registro-container d-flex justify-content-start"
            to="/"
          >
            <img className="logo-registro" src="swapp sin fondo.webp"></img>
          </Link>
          <h4 className="fw-medium">¡Donde todo, tiene otro valor!</h4>
        </div>
        <div className="col-12 col-lg-7 px-2 form-container d-flex justify-content-center  align-items-center">
          <form className="text-start" onSubmit={handleSubmit}>
            <h5 className="form-title text-start fw-bold my-3">
              Únete a Swapp!
            </h5>
            <div className="d-flex gap-2">
              <div>
                <input
                  name="first_name"
                  onChange={handleChange}
                  value={formData.first_name}
                  type="text"
                  className="form-control registro-input"
                  id="first_name"
                  aria-describedby="emailHelp"
                  placeholder="Nombre*"
                />
                {errors.first_name && <p className="error">{errors.first_name}</p>}
              </div>
              <div>
                <input
                  name="last_name"
                  onChange={handleChange}
                  value={formData.last_name}
                  type="text"
                  className="form-control registro-input flex-grow-1"
                  id="last_name"
                  aria-describedby=""
                  placeholder="Apellidos*"
                />
                {errors.last_name && <p className="error">{errors.last_name}</p>}
              </div>
            </div>

            <div className="mt-1">
              <label htmlFor="fecha-nacimiento" className="form-label">
                Fecha de nacimiento
              </label>
              <div className="d-flex" style={{ gap: "12px" }}>
                <select
                  className="form-select registro-input"
                  style={{ width: "80px" }}
                  onChange={handleChange}
                  value={formData.day}
                  id="day"
                  name="day"
                >
                  <option value="">Día</option>
                  {[...Array(31)].map((_, i) => (
                    <option key={i + 1} value={i + 1}>
                      {i + 1}
                    </option>
                  ))}
                </select>

                <select
                  className="form-select registro-input"
                  style={{ width: "90px" }}
                  onChange={handleChange}
                  value={formData.month}
                  id="month"
                  name="month"
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

                <select
                  className="form-select registro-input"
                  style={{ width: "90px" }}
                  onChange={handleChange}
                  value={formData.year}
                  id="year"
                  name="year"
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
            </div>

            <div className="  mt-1">
              <label className="form-label">Género</label>
              <div className="d-flex justify-content-center align-items-center">
                <div className="input-group ">
                  <div className="input-group-prepend ">
                    <div className=" mujer-radio">
                      <input
                        className="form-check-input"
                        onChange={handleChange}
                        checked={formData.gender === "mujer"}
                        value="mujer"
                        type="radio"
                        id="mujer"
                        name="gender"
                        aria-label="Radio button for following text input"
                      />
                      <label className="label-mujer" htmlFor="mujer">
                        Mujer
                      </label>
                    </div>
                  </div>
                </div>
                <div className="input-group ">
                  <div className="input-group-prepend ">
                    <div className="hombre-radio">
                      <input
                        className="form-check-input"
                        onChange={handleChange}
                        checked={formData.gender === "hombre"}
                        type="radio"
                        id="hombre"
                        name="gender"
                        value="hombre"
                        aria-label="Radio button for following text input"
                      />
                      <label className="label-hombre" htmlFor="mujer">
                        Hombre
                      </label>
                    </div>
                  </div>
                </div>
                <div className="input-group ">
                  <div className="input-group-prepend ">
                    <div className="personalizado-radio">
                      <input
                        className="form-check-input"
                        onChange={handleChange}
                        checked={formData.gender === "personalizado"}
                        type="radio"
                        id="personalizado"
                        name="gender"
                        value="personalizado"
                        aria-label="Radio button following text input"
                      />
                      <label className="label-personalizado" htmlFor="mujer">
                        Personalizado
                      </label>
                    </div>
                  </div>
                </div>
              </div>

              <div className="input-group my-2">
                <div className="input-group-prepend">
                  <label htmlFor="inputGroupSelect01">Categorías</label>
                </div>
                <select
                  className="form-select registro-input mt-1"
                  style={{ width: "100%" }}
                  name="category_id"
                  onChange={handleChange}
                  value={formData.category_id}
                  id="selectCategoria"
                >
                  {categories &&
                    categories.map((category, idx) => (
                      <option
                        key={category.id}
                        value={category?.id}
                      >
                        {category?.name}
                      </option>
                    ))}
                </select>
              </div>

              <div className="input-group my-2">
                <div className="input-group-prepend">
                  <label htmlFor="inputGroupSelect01">Habilidades</label>
                </div>
                <select
                  className="form-select registro-input mt-1"
                  style={{ width: "100%" }}
                  name="skill_id"
                  onChange={handleChange}
                  value={formData.skill_id}
                  id="selectHabilidad"
                >
                  {skills &&
                    skills.map((skill, idx) => (
                      <option
                        key={`skill-${idx}`}
                        value={skill?.id}
                      >
                        {skill?.name}
                      </option>
                    ))}
                </select>
              </div>
              <div className=" mt-1">
                <textarea
                  className="form-control registro-input "
                  id="description"
                  name="description"
                  onChange={handleChange}
                  value={formData.description}
                  rows="4"
                  placeholder="Escribe una breve descripción..."
                ></textarea>
              </div>
            </div>

            <div className="form-group mt-2">
              <input
                name="email"
                onChange={handleChange}
                value={formData.email}
                type="email"
                className="form-control registro-input"
                id="email"
                aria-describedby="emailHelp"
                placeholder="Correo electrónico*"
              />

              {errors.email && (
                <p className="error">{errors.email}</p>
              )}
            </div>
            <div className="form-group mt-2">
              <input
                name="password"
                onChange={handleChange}
                value={formData.password}
                type="password"
                className="form-control registro-input
                "
                id="password"
                placeholder="Contraseña*"
              />
              {errors.password && (
                <p className="error">{errors.password}</p>
              )}
            </div>
            <div className="form-group form-check mt-2">
              <input
                onChange={handleChange}
                name="accepts_terms"
                checked={formData.accepts_terms}
                type="checkbox"
                className="form-check-input"
                id="accepts_terms"
              />
              <label className="form-check-label" htmlFor="exampleCheck1">
                He leído y acepto las condiciones de uso y política de
                privacidad de Swapp.
              </label>
              {errors.accepts_terms && (
                <p className="error">{errors.accepts_terms}</p>
              )}
            </div>
            <div className="d-flex justify-content-center">
              <button type="submit" className="btn btn-main1 my-3">
                Registrate
              </button>
            </div>
          </form>
          {showModal && (
            <div
              className="modal fade show d-block"
              tabIndex="-1"
              role="dialog"
              style={{ backgroundColor: "rgba(0,0,0,0.5)" }}
            >
              <div
                className="modal-dialog modal-dialog-centered"
                role="document"
              >
                <div className="modal-content p-3 text-center">
                  <div className="modal-header border-0">
                    <h5 className="modal-title w-100 fw-bold">
                      ¡Te has registrado correctamente! 🎉
                    </h5>
                  </div>
                  <div className="modal-body">
                    <p>¡Bienvenido a nuestra comunidad!</p>
                    <p>¿Qué deseas hacer ahora?</p>
                  </div>
                  <div className="modal-footer border-0 d-flex justify-content-center gap-3">
                    <button
                      className="btn btn-secondary"
                      onClick={() => {
                        setShowModal(false);
                        setFormData({
                          first_name: "",
                          last_name: "",
                          day: "",
                          month: "",
                          year: "",
                          birth_date: "",
                          gender: "",
                          category_id: "",
                          skill_id: "",
                          description: "",
                          email: "",
                          password: "",
                          accepts_terms: false,
                        });
                      }}
                    >
                      Cerrar
                    </button>

                    <button
                      className="btn btn-main1"
                      onClick={() => navigate("/login")}
                    >
                      Iniciar sesión
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
export default Register;
