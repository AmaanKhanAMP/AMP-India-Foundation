import axios from "axios";
import { AUTH_COOKIE, TOKEN_KEY } from "@/utils/constants";
import { getApiBaseUrl } from "@/lib/api";

const api = axios.create({
  baseURL: getApiBaseUrl(),
  headers: { "Content-Type": "application/json" },
});

function readToken() {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(TOKEN_KEY);
}

export function setAuthToken(token, remember = false) {
  if (typeof window === "undefined") return;
  if (token) {
    localStorage.setItem(TOKEN_KEY, token);
    const maxAge = remember ? 60 * 60 * 24 * 30 : 60 * 60 * 24;
    document.cookie = `${AUTH_COOKIE}=1; path=/; max-age=${maxAge}; SameSite=Lax`;
  } else {
    localStorage.removeItem(TOKEN_KEY);
    document.cookie = `${AUTH_COOKIE}=; path=/; max-age=0; SameSite=Lax`;
  }
}

export function clearAuthToken() {
  setAuthToken(null);
}

api.interceptors.request.use((config) => {
  config.baseURL = getApiBaseUrl();
  const token = readToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  if (config.data instanceof FormData) {
    delete config.headers["Content-Type"];
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401 && typeof window !== "undefined") {
      // Allow endpoints to return 401 for business rules (e.g. wrong current password)
      // without wiping the JWT session.
      if (error.config?.skipAuthRedirect) {
        return Promise.reject(error);
      }
      const path = window.location.pathname;
      const publicAuth =
        path === "/login" ||
        path === "/forgot-password" ||
        path === "/reset-password";
      if (!publicAuth) {
        clearAuthToken();
        window.location.href = "/login";
      }
    }
    return Promise.reject(error);
  }
);

export default api;
