import { useQuery } from "@tanstack/react-query";
import { getDriver, getDriverSeasons } from "@/lib/api/drivers";
import { driverKeys } from "@/lib/utils/queryClient";

export function useDriver(id: string) {
  return useQuery({
    queryKey: driverKeys.detail(id),
    queryFn: () => getDriver(id),
    enabled: !!id,
  });
}

export function useDriverSeasons(id: string) {
  return useQuery({
    queryKey: driverKeys.seasons(id),
    queryFn: () => getDriverSeasons(id),
    enabled: !!id,
  });
}
