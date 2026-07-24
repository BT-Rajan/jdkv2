import { apiFetch, apiUpload, apiDownload } from "./api";
import { qs } from "./query";
import type { Attachment } from "../types";

export const attachmentsApi = {
  list: (entityType: string, entityId: string | number) =>
    apiFetch<Attachment[]>(`/api/attachments${qs({ entity_type: entityType, entity_id: entityId })}`),

  upload: (entityType: string, entityId: string | number, file: File, label?: string) => {
    const formData = new FormData();
    formData.append("entity_type", entityType);
    formData.append("entity_id", String(entityId));
    if (label) formData.append("label", label);
    formData.append("file", file);
    return apiUpload<Attachment>("/api/attachments", formData);
  },

  download: (attachmentId: string) => apiDownload(`/api/attachments/${attachmentId}/download`),

  delete: (attachmentId: string) => apiFetch(`/api/attachments/${attachmentId}`, { method: "DELETE" }),
};
