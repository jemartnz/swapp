import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import "../styles/UserCard.css";

function UserCard({ users = [], title = "Recomendados" }) {
  const navigate = useNavigate();

  const handleViewProfile = (userId) => {
    navigate(`/usuario/${userId}`);
  };

  return (
    <>
      <div className="container-fluid mt-5">
        <h3 className="text-center texto-recomendados">{title}</h3>
        <div className="row mt-5">
          {users.map((user) => (
            <div className="col-md-3 mb-4 " key={user.id}>
              <div className="card  h-100 mx-2">
                <div className="card-header d-flex justify-content-between">
                  <img
                    src={user.profile_picture || "/swapp-profile.png"}
                    className="card-img-top foto-perfil"
                    alt={user.first_name}
                  />
                  <button
                    className="btn btn-main1"
                    type="button"
                    onClick={() => handleViewProfile(user.id)}
                  >
                    Ver perfil
                  </button>
                </div>
                <div className="card-body">
                  <h5 className="card-title  text-center">
                    {user.first_name} {user.last_name}
                  </h5>
                  <p className="card-text  text-center text-limit ">
                    {user.description || "Sin descripción"}
                  </p>
                </div>
                <div className="d-flex justify-content-between m-2">
                  <div className="d-flex justify-content-between align-items-center">
                    <div>
                      {[1, 2, 3, 4, 5].map((num) => {
                        const score = user.rating_average || 0;
                        let star = " fa-regular fa-star text-secondary";
                        if (num <= Math.floor(score)) {
                          star = "fa-solid fa-star text-warning";
                        } else if (num - 0.5 <= score) {
                          star = "fa-solid fa-star-half-stroke text-warning";
                        } else if (score === 0) {
                          star = " fa-regular fa-star text-secondary";
                        }
                        return <i key={num} className={star}></i>;
                      })}
                    </div>
                  </div>

                  <div className="d-flex flex-column justify-content-center align-items-center">
                    <div
                      className="rounded-circle"
                      style={{
                        width: "12px",
                        height: "12px",
                        backgroundColor:
                          user.status === "online"
                            ? "green"
                            : user.status === "away"
                            ? "grey"
                            : user.status === "busy"
                            ? "red"
                            : "lightgray",
                      }}
                    ></div>
                    <p> {user.status}</p>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
        <hr></hr>
      </div>
    </>
  );
}

export default UserCard;
