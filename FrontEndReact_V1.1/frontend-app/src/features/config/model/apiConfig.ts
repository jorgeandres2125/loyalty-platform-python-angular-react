import { apiClient } from "../../../shared/api/client";

export interface UploadLimits {
  max_upload_bytes: number;
  max_upload_mb: number;
}

export async function getUploadLimits(): Promise<UploadLimits> {
  const { data } = await apiClient.get<UploadLimits>("/config/uploads");
  return data;
}
