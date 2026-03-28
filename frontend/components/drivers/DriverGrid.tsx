import { DriverCard } from "./DriverCard";
import { Skeleton } from "@/components/ui/Skeleton";
import type { DriverSummaryOut } from "@/lib/types/driver";

interface DriverGridProps {
  drivers: DriverSummaryOut[];
  isLoading?: boolean;
  onAddToShortlist?: (driver: DriverSummaryOut) => void;
}

export function DriverGrid({ drivers, isLoading, onAddToShortlist }: DriverGridProps) {
  if (isLoading) {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {Array.from({ length: 9 }).map((_, i) => (
          <div key={i} className="bg-surface border border-border rounded-lg p-4 flex flex-col gap-4">
            <div className="flex justify-between">
              <div className="flex flex-col gap-2">
                <Skeleton className="h-4 w-32" />
                <Skeleton className="h-3 w-20" />
              </div>
              <Skeleton className="h-5 w-16 rounded-full" />
            </div>
            <div className="grid grid-cols-3 gap-2">
              {[0, 1, 2].map((j) => (
                <Skeleton key={j} className="h-14 rounded" />
              ))}
            </div>
            <Skeleton className="h-8 rounded" />
          </div>
        ))}
      </div>
    );
  }

  if (!drivers.length) {
    return (
      <div className="flex flex-col items-center justify-center py-20 text-center">
        <div className="text-4xl mb-4">🏁</div>
        <h3 className="text-lg font-semibold text-text-primary mb-2">
          No drivers found
        </h3>
        <p className="text-text-secondary text-sm">
          Try adjusting your filters to see more results.
        </p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      {drivers.map((driver) => (
        <DriverCard
          key={driver.id}
          driver={driver}
          onAddToShortlist={onAddToShortlist}
        />
      ))}
    </div>
  );
}
