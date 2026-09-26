import api from "./api";

const trashService = {
  list: async (params = {}) => {
    const { data } = await api.get("/api/admin/content/trash", { params });
    return data;
  },
  restore: async (resource, id) => {
    const { data } = await api.post(`/api/admin/content/trash/${resource}/${id}/restore`);
    return data;
  },
  permanentDelete: async (resource, id) => {
    const { data } = await api.delete(`/api/admin/content/trash/${resource}/${id}`);
    return data;
  },
};

export default trashService;
