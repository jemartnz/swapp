import Navbar from "../assets/components/Navbar";
import Carousel from "../assets/components/Carousel";
import UserCard from "../assets/components/UserCard";
import Footer from "../assets/components/Footer";
import ChatModal from "../assets/components/ChatModal";
import MessagingButton from "../assets/components/MessagingButton";
import { useState, useEffect } from "react";
import { env } from "../environ";
import { useStore } from "../hooks/useStore";

function Home() {
  const { store, dispatch } = useStore();
  const [showModal, setShowModal] = useState(false);
  const [user, setUser] = useState();
  const [users, setUsers] = useState([]);

  useEffect(() => {
    const token = localStorage.getItem("token");

    if (token) {
      fetch(`${env.api}/api/auth/me`, {
        method: "GET",
        headers: {
          Authorization: `Bearer ${token}`,
          Accept: "application/json",
        },
      })
        .then((res) => {
          if (!res.ok) {
            localStorage.removeItem("token");
            return null;
          }
          return res.json();
        })
        .then((data) => {
          if (data) {
            setUser(data);
            dispatch({ type: "SET_USER", payload: data });
          }
        })
        .catch((err) => console.error("Error al cargar usuario:", err));
      dispatch({ type: "SET_TOKEN", payload: token });
    }

    fetch(`${env.api}/api/users`)
      .then((res) => res.json())
      .then((data) => {
        if (data) {
          dispatch({ type: "SET_USERS", payload: data });
        }
      })
      .catch((err) => console.error("Error al cargar usuarios:", err));

    fetch(`${env.api}/api/categories`)
      .then((res) => res.json())
      .then((data) => {
        if (data) {
          dispatch({ type: "SET_CATEGORIES", payload: data });
        }
      })
      .catch((err) => console.error("Error al cargar Categorias:", err));
  }, []);

  useEffect(() => {
    fetch(`${env.api}/api/users`)
      .then((res) => res.json())
      .then((data) => setUsers(data.slice(0, 8)))
      .catch((err) => console.error("Error al cargar usuarios:", err));
  }, []);

  return (
    <>
      <Navbar></Navbar>
      <Carousel></Carousel>
      <UserCard users={users} title="Recomendados"></UserCard>
      <Footer></Footer>

      {user ? (
        <>
          <MessagingButton
            onClick={() => setShowModal(true)}
          ></MessagingButton>
          <ChatModal
            show={showModal}
            close={() => setShowModal(false)}
          ></ChatModal>
        </>
      ) : (
        ""
      )}
    </>
  );
}

export default Home;
