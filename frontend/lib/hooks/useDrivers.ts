import { useQuery } from "@tanstack/react-query";
import { getDrivers } from "@/lib/api/drivers";
import { driverKeys } from "@/lib/utils/queryClient";
import type { DriversQueryParams } from "@/lib/types/driver";

export function useDrivers(params: DriversQueryParams = {}) {
  return useQuery({
    queryKey: driverKeys.list(params),
    queryFn: () => getDrivers(params),
  });
}
