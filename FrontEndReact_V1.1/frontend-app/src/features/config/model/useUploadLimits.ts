import { useQuery } from "@tanstack/react-query";
import { getUploadLimits } from "./apiConfig";
import { MAX_UPLOAD_BYTES_FALLBACK } from "../../../shared/lib/archivos";

// AP-0137: limite de subida que publica el backend; cacheado 1 hora.
export function useUploadLimits() {
  return useQuery({
    queryKey: ["config", "upload-limits"],
    queryFn: getUploadLimits,
    staleTime: 3_600_000,
  });
}

// Devuelve el limite vigente en bytes: el del backend si cargo, o el respaldo.
export function useMaxUploadBytes(): number {
  const { data } = useUploadLimits();
  return data?.max_upload_bytes ?? MAX_UPLOAD_BYTES_FALLBACK;
}
