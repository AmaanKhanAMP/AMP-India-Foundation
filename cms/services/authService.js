import api, { clearAuthToken, setAuthToken } from "./api";
import { REMEMBER_KEY } from "@/utils/constants";

export async function login({ email, password, remember }) {
  const { data } = await api.post("/api/auth/login", { email, password, remember });
  if (data?.token) {
    setAuthToken(data.token, Boolean(remember));
    if (typeof window !== "undefined") {
      localStorage.setItem(REMEMBER_KEY, remember ? "1" : "0");
    }
  }
  return data;
}

export async function getMe() {
  const { data } = await api.get("/api/auth/me");
  return data;
}

export async function updateProfile(payload) {
  const { data } = await api.put("/api/auth/profile", payload, {
    // Wrong current password returns 401 — do not force logout
    skipAuthRedirect: true,
  });
  return data;
}

export async function changePassword(payload) {
  const { data } = await api.put("/api/auth/change-password", payload);
  return data;
}

export async function forgotPassword(email) {
  const { data } = await api.post("/api/auth/forgot-password", { email });
  return data;
}

export async function resetPassword({ token, new_password }) {
  const { data } = await api.post("/api/auth/reset-password", { token, new_password });
  return data;
}

export async function logout() {
  try {
    await api.post("/api/auth/logout");
  } catch {
    // ignore — clear local session anyway
  } finally {
    clearAuthToken();
    if (typeof window !== "undefined") {
      localStorage.removeItem(REMEMBER_KEY);
    }
  }
}

const authService = {
  login,
  getMe,
  updateProfile,
  changePassword,
  forgotPassword,
  resetPassword,
  logout,
};

export default authService;
