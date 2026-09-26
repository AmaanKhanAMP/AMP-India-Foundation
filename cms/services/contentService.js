import api from "./api";

export function createContentService(resource) {
  const base = `/api/admin/content/${resource}`;

  return {
    list: async (params = {}) => {
      const { data } = await api.get(base, { params });
      return data;
    },
    get: async (id) => {
      const { data } = await api.get(`${base}/${id}`);
      return data;
    },
    create: async (payload) => {
      const { data } = await api.post(base, payload);
      return data;
    },
    update: async (id, payload) => {
      const { data } = await api.put(`${base}/${id}`, payload);
      return data;
    },
    remove: async (id) => {
      const { data } = await api.delete(`${base}/${id}`);
      return data;
    },
    restore: async (id) => {
      const { data } = await api.post(`${base}/${id}/restore`);
      return data;
    },
    permanentDelete: async (id) => {
      const { data } = await api.delete(`${base}/${id}/permanent`);
      return data;
    },
    duplicate: async (id) => {
      const { data } = await api.post(`${base}/${id}/duplicate`);
      return data;
    },
    reorder: async (order) => {
      const { data } = await api.post(`${base}/reorder`, { order });
      return data;
    },
    publish: async (id) => {
      const { data } = await api.post(`${base}/${id}/publish`);
      return data;
    },
    unpublish: async (id) => {
      const { data } = await api.post(`${base}/${id}/unpublish`);
      return data;
    },
    bulk: async (ids, action) => {
      const { data } = await api.post(`${base}/bulk`, { ids, action });
      return data;
    },
  };
}

const contentService = {
  for: createContentService,
};

export default contentService;
