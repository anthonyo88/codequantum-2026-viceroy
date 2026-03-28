export interface ShortlistOut {
  id: string;
  name: string;
  description: string | null;
  driver_ids: string[];
  notes: Record<string, string>;
  created_at: string;
  updated_at: string;
}

export interface ShortlistCreate {
  name: string;
  description?: string;
}

export interface ShortlistUpdate {
  name?: string;
  description?: string;
}

export interface AddDriversRequest {
  driver_ids: string[];
  notes?: Record<string, string>;
}
