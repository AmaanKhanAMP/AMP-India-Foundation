import api from "@/services/api";

export async function getNavbarSettings() {
  const { data } = await api.get("/api/admin/layout/navbar");
  return data;
}

export async function updateNavbarSettings(payload) {
  const { data } = await api.put("/api/admin/layout/navbar", payload);
  return data;
}

export async function getFooterSettings() {
  const { data } = await api.get("/api/admin/layout/footer");
  return data;
}

export async function updateFooterSettings(payload) {
  const { data } = await api.put("/api/admin/layout/footer", payload);
  return data;
}
