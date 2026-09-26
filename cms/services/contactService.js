import api from "./api";

export async function listMessages(params = {}) {
  const { data } = await api.get("/api/admin/contact/messages", { params });
  return data;
}

export async function markMessageRead(id) {
  const { data } = await api.patch(`/api/admin/contact/messages/${id}/read`);
  return data;
}

export async function toggleImportant(id, isImportant) {
  const { data } = await api.patch(`/api/admin/contact/messages/${id}/important`, {
    is_important: isImportant,
  });
  return data;
}

export async function deleteMessage(id) {
  const { data } = await api.delete(`/api/admin/contact/messages/${id}`);
  return data;
}

export async function bulkDeleteMessages(ids) {
  const { data } = await api.post("/api/admin/contact/messages/bulk-delete", { ids });
  return data;
}

const contactService = {
  listMessages,
  markMessageRead,
  toggleImportant,
  deleteMessage,
  bulkDeleteMessages,
};

export default contactService;
