import { apiClient } from "./client";
import type {
  DriverListResponse,
  DriverOut,
  DriverSeason,
  DriversQueryParams,
} from "@/lib/types/driver";

export async function getDrivers(
  params: DriversQueryParams = {}
): Promise<DriverListResponse> {
  // Strip empty values
  const cleaned = Object.fromEntries(
    Object.entries(params).filter(
      ([, v]) => v !== undefined && v !== "" && v !== null
    )
  );
  const res = await apiClient.get<DriverListResponse>("/api/v1/drivers", {
    params: cleaned,
  });
  return res.data;
}

export async function getDriver(id: string): Promise<DriverOut> {
  const res = await apiClient.get<DriverOut>(`/api/v1/drivers/${id}`);
  return res.data;
}

export async function getDriverSeasons(id: string): Promise<DriverSeason[]> {
  const res = await apiClient.get<DriverSeason[]>(
    `/api/v1/drivers/${id}/seasons`
  );
  return res.data;
}

export async function compareDrivers(ids: string[]): Promise<DriverOut[]> {
  const res = await apiClient.get<DriverOut[]>("/api/v1/drivers/compare", {
    params: { ids: ids.join(",") },
  });
  return res.data;
}
