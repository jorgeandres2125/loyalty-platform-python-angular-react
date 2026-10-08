import { useQuery } from '@tanstack/react-query';
import {
  listarProgramasApi,
  listarSubprogramasApi,
} from './apiProgramas';
import type { ProgramaItem, SubprogramaItem } from './types';

export function useProgramas() {
  return useQuery<ProgramaItem[]>({
    queryKey: ['programas'],
    queryFn: () => listarProgramasApi(),
    staleTime: 5 * 60_000,
  });
}

export function useSubprogramas(cpid?: number) {
  return useQuery<SubprogramaItem[]>({
    queryKey: ['subprogramas', cpid ?? 'all'],
    queryFn: () => listarSubprogramasApi(cpid),
    staleTime: 5 * 60_000,
  });
}
