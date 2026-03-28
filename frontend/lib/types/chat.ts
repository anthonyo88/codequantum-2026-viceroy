export interface NaturalLanguageSearchRequest {
  query: string;
  limit?: number;
}

export interface RecommendRequest {
  criteria: string;
  max_results?: number;
}

export interface ChatQueryResponse {
  response: string;
  session_id: string;
  driver_ids_referenced: string[];
  token_count: number;
}
