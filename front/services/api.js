import { env } from "../environ";

const getToken = () => {
  const raw = localStorage.getItem("token");
  return raw ? raw.replace(/^"|"$/g, "") : null;
};

let isRefreshing = false;
let refreshQueue = [];

const processQueue = (error, token = null) => {
  refreshQueue.forEach((prom) => {
    if (error) prom.reject(error);
    else prom.resolve(token);
  });
  refreshQueue = [];
};

export const refreshAccessToken = async () => {
  const refreshToken = localStorage.getItem("refresh_token");
  if (!refreshToken) return null;

  try {
    const response = await fetch(`${env.api}/api/auth/refresh`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${refreshToken}`,
        Accept: "application/json",
      },
    });

    if (!response.ok) {
      localStorage.removeItem("token");
      localStorage.removeItem("refresh_token");
      return null;
    }

    const data = await response.json();
    const newToken = data?.data?.token;
    if (newToken) {
      localStorage.setItem("token", JSON.stringify(newToken));
    }
    return newToken || null;
  } catch {
    localStorage.removeItem("token");
    localStorage.removeItem("refresh_token");
    return null;
  }
};

export const apiFetch = async (url, options = {}) => {
  const token = getToken();
  const headers = {
    Accept: "application/json",
    ...(options.headers || {}),
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };

  const response = await fetch(url, { ...options, headers });
  if (response.status !== 401) return response;

  // 401 — attempt token refresh
  if (isRefreshing) {
    return new Promise((resolve, reject) => {
      refreshQueue.push({ resolve, reject });
    }).then((newToken) => {
      const retryHeaders = { ...headers, Authorization: `Bearer ${newToken}` };
      return fetch(url, { ...options, headers: retryHeaders });
    });
  }

  isRefreshing = true;
  const newToken = await refreshAccessToken();
  isRefreshing = false;

  if (!newToken) {
    processQueue(new Error("Session expired"), null);
    return response; // return original 401
  }

  processQueue(null, newToken);
  const retryHeaders = { ...headers, Authorization: `Bearer ${newToken}` };
  return fetch(url, { ...options, headers: retryHeaders });
};

export const registerUser = async (formData) => {
  try {
    const response = await fetch(`${env.api}/api/users`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(formData),
    });

    if (!response.ok) {
      throw new Error("Error al registrar el usuario");
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error("Error en el registro:", error);
    throw error;
  }
};
