"use client";

import Link from "next/link";
import { Trash2, Trophy, Flag } from "lucide-react";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { nationalityFlag } from "@/lib/utils/formatters";
import type { DriverSummaryOut } from "@/lib/types/driver";

interface ShortlistDriverRowProps {
  driver: DriverSummaryOut;
  note?: string;
  onRemove: () => void;
  isRemoving?: boolean;
}

export function ShortlistDriverRow({
  driver,
  note,
  onRemove,
  isRemoving,
}: ShortlistDriverRowProps) {
  return (
    <div className="flex items-center gap-4 p-3 rounded-lg bg-surface-elevated border border-border hover:border-accent/20 transition-colors group">
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 flex-wrap">
          <Link
            href={`/drivers/${driver.id}`}
            className="font-semibold text-text-primary hover:text-accent transition-colors"
          >
            {driver.full_name}
          </Link>
          <Badge variant={driver.active_status ? "active" : "retired"}>
            {driver.active_status ? "Active" : "Retired"}
          </Badge>
        </div>
        <div className="flex items-center gap-3 mt-1 text-xs text-text-muted flex-wrap">
          <span>{nationalityFlag(driver.nationality)} {driver.nationality}</span>
          <span className="flex items-center gap-1">
            <Trophy className="w-3 h-3 text-gold" />
            {driver.career_stats.championships_won}
          </span>
          <span className="flex items-center gap-1">
            <Flag className="w-3 h-3 text-accent" />
            {driver.career_stats.total_wins} wins
          </span>
        </div>
        {note && (
          <p className="mt-1.5 text-xs text-text-secondary italic bg-surface rounded px-2 py-1 border-l-2 border-accent/40">
            {note}
          </p>
        )}
      </div>

      <Button
        variant="ghost"
        size="icon"
        onClick={onRemove}
        loading={isRemoving}
        className="opacity-0 group-hover:opacity-100 transition-opacity text-text-muted hover:text-red-400"
        title="Remove from shortlist"
      >
        <Trash2 className="w-4 h-4" />
      </Button>
    </div>
  );
}
