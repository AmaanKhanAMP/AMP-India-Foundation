import api from "./api";

export async function uploadFile(file, folder = "general") {
  const form = new FormData();
  form.append("file", file);
  if (folder) form.append("folder", folder);
  const { data } = await api.post("/api/admin/upload", form);
  return data;
}

const uploadService = { uploadFile };

export default uploadService;
