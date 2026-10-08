import { apiClient } from '../../../shared/api/client';
import type { SapinTokenResponse } from './types';

export async function getSapinTokenApi(): Promise<SapinTokenResponse> {
  const { data } = await apiClient.get<SapinTokenResponse>('/sapin/token');
  return data;
}
