import type { CanalListItem } from './CanalListItem';

export interface CanalListResponse {
  items: CanalListItem[];
  total: number;
  page: number;
  page_size: number;
}
