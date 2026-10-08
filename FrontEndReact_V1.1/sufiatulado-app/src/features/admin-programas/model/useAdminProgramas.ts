import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { actualizarAdminProgramaApi, listarAdminProgramasApi } from './apiAdminProgramas';
import type { AdminProgramaFormPayload, AdminProgramaItem } from './types';

const QK_LIST = 'admin-programas-list' as const;

export function useAdminProgramasList() {
  return useQuery<AdminProgramaItem[]>({
    queryKey: [QK_LIST],
    queryFn: listarAdminProgramasApi,
    staleTime: 60_000,
  });
}

export function useActualizarAdminPrograma() {
  const qc = useQueryClient();
  return useMutation<AdminProgramaItem, Error, { cpid: number; payload: AdminProgramaFormPayload }>({
    mutationFn: ({ cpid, payload }) => actualizarAdminProgramaApi(cpid, payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: [QK_LIST] }),
  });
}
