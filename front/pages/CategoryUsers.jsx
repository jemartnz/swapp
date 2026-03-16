import Navbar from "../assets/components/Navbar";
import Footer from "../assets/components/Footer";
import UserCard from "../assets/components/UserCard";
import { useParams } from "react-router";
import { useEffect, useState } from "react";
import { env } from "../environ";

function CategoryUsers() {
  const { categoryId } = useParams();
  const [users, setUsers] = useState([]);
  const [category, setCategory] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);

    Promise.all([
      fetch(`${env.api}/api/users/category/${categoryId}`).then(
        (response) => response.json()
      ),
      fetch(`${env.api}/api/categories/${categoryId}`).then((res) =>
        res.json()
      ),
    ])

      .then(([usersData, categoryData]) => {
        setUsers(usersData.data || []);
        setCategory(categoryData.data || categoryData);
      })
      .catch((err) => {
        console.error("Error al cargar datos:", err);
      })
      .finally(() => {
        setLoading(false);
      });
  }, [categoryId]);

  return (
    <div className="d-flex flex-column min-vh-100">
      <Navbar></Navbar>
      <div className="flex-grow-1 d-flex align-items-center justify-content-center">
        {loading ? (
          <div className="text-center">
            <div
              className="spinner-border"
              style={{ color: "#ff7517" }}
              role="status"
            >
              <span className="visually-hidden">Cargando...</span>
            </div>
            <h4 className="mt-3">Cargando usuarios...</h4>
          </div>
        ) : users && users.length > 0 ? (
          <UserCard users={users} title=""></UserCard>
        ) : (
          <div className="m-5">
            <h4 className="text-center m-5">
              No existen usuarios para la categoría seleccionada!
            </h4>
          </div>
        )}
      </div>
      <Footer></Footer>
    </div>
  );
}

export default CategoryUsers;
