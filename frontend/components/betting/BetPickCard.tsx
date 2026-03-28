import { cn } from "@/lib/utils/cn";
import type { BetPick } from "@/lib/types/betting";

const BET_TYPE_LABELS: Record<BetPick["bet_type"], string> = {
  win: "Win",
  podium: "Podium",
  points_finish: "Points Finish",
};

const CONFIDENCE_STYLES: Record<BetPick["confidence"], string> = {
  high: "bg-green-500/15 text-green-400 border-green-500/30",
  medium: "bg-yellow-500/15 text-yellow-400 border-yellow-500/30",
  low: "bg-red-500/15 text-red-400 border-red-500/30",
};

const BET_TYPE_STYLES: Record<BetPick["bet_type"], string> = {
  win: "bg-accent/15 text-accent border-accent/30",
  podium: "bg-blue-500/15 text-blue-400 border-blue-500/30",
  points_finish: "bg-surface-elevated text-text-secondary border-border",
};

export function BetPickCard({ pick }: { pick: BetPick }) {
  return (
    <div className="bg-surface border border-border rounded-lg p-4 flex flex-col gap-3 hover:border-accent/30 transition-colors duration-150">
      <div className="flex items-start justify-between gap-2">
        <span className="text-text-primary font-semibold text-sm leading-tight">
          {pick.driver_name}
        </span>
        <span
          className={cn(
            "text-xs font-medium px-2 py-0.5 rounded border flex-shrink-0",
            BET_TYPE_STYLES[pick.bet_type]
          )}
        >
          {BET_TYPE_LABELS[pick.bet_type]}
        </span>
      </div>

      <p className="text-text-secondary text-xs leading-relaxed">{pick.reason}</p>

      <div className="flex items-center justify-between">
        <span className="text-text-muted text-xs">Confidence</span>
        <span
          className={cn(
            "text-xs font-medium px-2 py-0.5 rounded border capitalize",
            CONFIDENCE_STYLES[pick.confidence]
          )}
        >
          {pick.confidence}
        </span>
      </div>
    </div>
  );
}
