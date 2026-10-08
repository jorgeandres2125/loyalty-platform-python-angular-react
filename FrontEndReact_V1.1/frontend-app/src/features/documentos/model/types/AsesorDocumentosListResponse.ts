import type { AsesorDocumentosItem } from './AsesorDocumentosItem';

export interface AsesorDocumentosListResponse {
  items: AsesorDocumentosItem[];
  total: number;
  page: number;
  page_size: number;
}
