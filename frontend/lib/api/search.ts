import { apiClient } from "./client";
import type { DriverListResponse, DriverFilterRequest } from "@/lib/types/driver";

export async function filterDrivers(
  filters: DriverFilterRequest
): Promise<DriverListResponse> {
  const res = await apiClient.post<DriverListResponse>(
    "/api/v1/search/filter",
    filters
  );
  return res.data;
}
