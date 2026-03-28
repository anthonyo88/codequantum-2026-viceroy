import { apiClient } from "./client";
import type { BettingRequest, BettingResponse } from "@/lib/types/betting";

export async function getBettingPrediction(
  data: BettingRequest
): Promise<BettingResponse> {
  const res = await apiClient.post<BettingResponse>(
    "/api/v1/betting/predict",
    data
  );
  return res.data;
}
