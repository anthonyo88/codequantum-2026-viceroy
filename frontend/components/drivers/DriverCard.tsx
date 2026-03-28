"use client";

import { useRouter } from "next/navigation";
import { Trophy, Flag, TrendingUp, Plus } from "lucide-react";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { formatPct, nationalityFlag } from "@/lib/utils/formatters";
import type { DriverSummaryOut } from "@/lib/types/driver";

interface DriverCardProps {
  driver: DriverSummaryOut;
  onAddToShortlist?: (driver: DriverSummaryOut) => void;
}

export function DriverCard({ driver, onAddToShortlist }: DriverCardProps) {
  const router = useRouter();
  const stats = driver.career_stats;

  return (
    <Card
      hover
      onClick={() => router.push(`/drivers/${driver.id}`)}
      className="flex flex-col gap-4 animate-fade-in"
    >
      {/* Header */}
      <div className="flex items-start justify-between gap-2">
        <div className="flex-1 min-w-0">
          <h3 className="font-bold text-text-primary text-base leading-tight truncate">
            {driver.full_name}
          </h3>
          <div className="flex items-center gap-2 mt-1">
            <span className="text-sm text-text-secondary">
              {nationalityFlag(driver.nationality)} {driver.nationality}
            </span>
          </div>
        </div>
        <Badge variant={driver.active_status ? "active" : "retired"}>
          {driver.active_status ? "Active" : "Retired"}
        </Badge>
      </div>

      {/* Stats grid */}
      <div className="grid grid-cols-3 gap-2">
        <div className="flex flex-col items-center bg-surface-elevated rounded p-2">
          <Trophy className="w-3.5 h-3.5 text-gold mb-1" />
          <span className="text-lg font-bold text-text-primary leading-none">
            {stats.championships_won}
          </span>
          <span className="text-xs text-text-muted mt-0.5">Titles</span>
        </div>
        <div className="flex flex-col items-center bg-surface-elevated rounded p-2">
          <Flag className="w-3.5 h-3.5 text-accent mb-1" />
          <span className="text-lg font-bold text-text-primary leading-none">
            {stats.total_wins}
          </span>
          <span className="text-xs text-text-muted mt-0.5">Wins</span>
        </div>
        <div className="flex flex-col items-center bg-surface-elevated rounded p-2">
          <TrendingUp className="w-3.5 h-3.5 text-text-secondary mb-1" />
          <span className="text-lg font-bold text-text-primary leading-none">
            {stats.total_podiums}
          </span>
          <span className="text-xs text-text-muted mt-0.5">Podiums</span>
        </div>
      </div>

      {/* Win rate */}
      <div className="flex items-center justify-between text-xs">
        <span className="text-text-muted">Win rate</span>
        <span className="text-text-secondary font-medium">
          {formatPct(stats.career_win_rate)}
        </span>
      </div>

      {/* Add to shortlist */}
      <Button
        variant="secondary"
        size="sm"
        className="w-full"
        onClick={(e) => {
          e.stopPropagation();
          onAddToShortlist?.(driver);
        }}
      >
        <Plus className="w-3.5 h-3.5" />
        Shortlist
      </Button>
    </Card>
  );
}
