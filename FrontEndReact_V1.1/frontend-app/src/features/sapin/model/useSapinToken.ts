import { useQuery } from '@tanstack/react-query';
import { getSapinTokenApi } from './apiSapin';
import { QUERY_KEYS } from '../../../shared/config/constants';
import { useAuthStore } from '../../../entities/user/model/authStore';

export function useSapinToken() {
  const canAccess = useAuthStore((s) => s.canAccessSapin());

  return useQuery({
    queryKey: [QUERY_KEYS.SAPIN_TOKEN],
    queryFn: getSapinTokenApi,
    enabled: canAccess,
    staleTime: 5 * 60 * 1000, // 5 minutes
    refetchInterval: 4 * 60 * 1000, // refresh every 4 min
  });
}
