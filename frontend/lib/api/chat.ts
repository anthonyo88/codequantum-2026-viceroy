import { apiClient } from "./client";
import type {
  NaturalLanguageSearchRequest,
  RecommendRequest,
  ChatQueryResponse,
} from "@/lib/types/chat";

export async function chatSearch(
  data: NaturalLanguageSearchRequest
): Promise<ChatQueryResponse> {
  const res = await apiClient.post<ChatQueryResponse>(
    "/api/v1/chat/search",
    data
  );
  return res.data;
}

export async function chatRecommend(
  data: RecommendRequest
): Promise<ChatQueryResponse> {
  const res = await apiClient.post<ChatQueryResponse>(
    "/api/v1/chat/recommend",
    data
  );
  return res.data;
}
