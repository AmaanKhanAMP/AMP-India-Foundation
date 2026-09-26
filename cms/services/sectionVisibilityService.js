import api from "@/services/api";

export async function getSectionVisibility(sectionName) {
  const { data } = await api.get(`/api/admin/sections/${sectionName}/visibility`);
  return data;
}

export async function updateSectionVisibility(sectionName, isVisible) {
  const { data } = await api.put(`/api/admin/sections/${sectionName}/visibility`, {
    is_visible: Boolean(isVisible),
  });
  return data;
}
