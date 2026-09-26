import api from "./api";

export async function getDashboardStats() {
  const { data } = await api.get("/api/admin/dashboard/stats");
  return data;
}

const dashboardService = { getDashboardStats };

export default dashboardService;
