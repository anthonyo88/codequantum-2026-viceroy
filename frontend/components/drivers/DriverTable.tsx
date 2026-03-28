"use client";

import { useRouter } from "next/navigation";
import { ChevronUp, ChevronDown, Plus } from "lucide-react";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Skeleton } from "@/components/ui/Skeleton";
import { formatPct, nationalityFlag } from "@/lib/utils/formatters";
import type { DriverSummaryOut, SortBy } from "@/lib/types/driver";

interface DriverTableProps {
  drivers: DriverSummaryOut[];
  isLoading?: boolean;
  sortBy?: SortBy;
  sortOrder?: "asc" | "desc";
  onSort?: (col: SortBy) => void;
  onAddToShortlist?: (driver: DriverSummaryOut) => void;
}

const SORTABLE_COLUMNS: { key: SortBy; label: string }[] = [
  { key: "championships_won", label: "Titles" },
  { key: "total_wins", label: "Wins" },
  { key: "total_podiums", label: "Podiums" },
  { key: "win_rate", label: "Win %" },
];

export function DriverTable({
  drivers,
  isLoading,
  sortBy,
  sortOrder,
  onSort,
  onAddToShortlist,
}: DriverTableProps) {
  const router = useRouter();

  if (isLoading) {
    return (
      <div className="space-y-2">
        {Array.from({ length: 10 }).map((_, i) => (
          <Skeleton key={i} className="h-12 rounded" />
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
          Try adjusting your filters.
        </p>
      </div>
    );
  }

  return (
    <div className="overflow-x-auto rounded-lg border border-border">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-border bg-surface-elevated">
            <th className="text-left px-4 py-3 text-text-muted font-medium">
              Driver
            </th>
            <th className="text-left px-4 py-3 text-text-muted font-medium">
              Status
            </th>
            {SORTABLE_COLUMNS.map(({ key, label }) => (
              <th
                key={key}
                className="text-right px-4 py-3 text-text-muted font-medium cursor-pointer hover:text-text-primary select-none transition-colors"
                onClick={() => onSort?.(key)}
              >
                <div className="flex items-center justify-end gap-1">
                  {label}
                  {sortBy === key ? (
                    sortOrder === "asc" ? (
                      <ChevronUp className="w-3.5 h-3.5" />
                    ) : (
                      <ChevronDown className="w-3.5 h-3.5" />
                    )
                  ) : (
                    <ChevronDown className="w-3.5 h-3.5 opacity-30" />
                  )}
                </div>
              </th>
            ))}
            <th className="px-4 py-3" />
          </tr>
        </thead>
        <tbody>
          {drivers.map((driver) => (
            <tr
              key={driver.id}
              onClick={() => router.push(`/drivers/${driver.id}`)}
              className="border-b border-border last:border-0 hover:bg-surface-hover cursor-pointer transition-colors"
            >
              <td className="px-4 py-3">
                <div>
                  <p className="font-medium text-text-primary">
                    {driver.full_name}
                  </p>
                  <p className="text-xs text-text-muted">
                    {nationalityFlag(driver.nationality)} {driver.nationality}
                  </p>
                </div>
              </td>
              <td className="px-4 py-3">
                <Badge variant={driver.active_status ? "active" : "retired"}>
                  {driver.active_status ? "Active" : "Retired"}
                </Badge>
              </td>
              <td className="px-4 py-3 text-right font-mono text-text-primary">
                {driver.career_stats.championships_won}
              </td>
              <td className="px-4 py-3 text-right font-mono text-text-primary">
                {driver.career_stats.total_wins}
              </td>
              <td className="px-4 py-3 text-right font-mono text-text-primary">
                {driver.career_stats.total_podiums}
              </td>
              <td className="px-4 py-3 text-right font-mono text-text-secondary">
                {formatPct(driver.career_stats.career_win_rate)}
              </td>
              <td className="px-4 py-3">
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={(e) => {
                    e.stopPropagation();
                    onAddToShortlist?.(driver);
                  }}
                  title="Add to shortlist"
                >
                  <Plus className="w-4 h-4" />
                </Button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
