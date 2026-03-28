import { apiClient } from "./client";
import type {
  ShortlistOut,
  ShortlistCreate,
  ShortlistUpdate,
  AddDriversRequest,
} from "@/lib/types/shortlist";

export async function getShortlists(): Promise<ShortlistOut[]> {
  const res = await apiClient.get<ShortlistOut[]>("/api/v1/shortlists");
  return res.data;
}

export async function getShortlist(id: string): Promise<ShortlistOut> {
  const res = await apiClient.get<ShortlistOut>(`/api/v1/shortlists/${id}`);
  return res.data;
}

export async function createShortlist(
  data: ShortlistCreate
): Promise<ShortlistOut> {
  const res = await apiClient.post<ShortlistOut>("/api/v1/shortlists", data);
  return res.data;
}

export async function updateShortlist(
  id: string,
  data: ShortlistUpdate
): Promise<ShortlistOut> {
  const res = await apiClient.patch<ShortlistOut>(
    `/api/v1/shortlists/${id}`,
    data
  );
  return res.data;
}

export async function deleteShortlist(id: string): Promise<void> {
  await apiClient.delete(`/api/v1/shortlists/${id}`);
}

export async function addDriversToShortlist(
  shortlistId: string,
  data: AddDriversRequest
): Promise<ShortlistOut> {
  const res = await apiClient.post<ShortlistOut>(
    `/api/v1/shortlists/${shortlistId}/drivers`,
    data
  );
  return res.data;
}

export async function removeDriverFromShortlist(
  shortlistId: string,
  driverId: string
): Promise<ShortlistOut> {
  const res = await apiClient.delete<ShortlistOut>(
    `/api/v1/shortlists/${shortlistId}/drivers/${driverId}`
  );
  return res.data;
}
