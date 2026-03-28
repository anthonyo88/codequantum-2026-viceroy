import { Trophy } from "lucide-react";
import type { DriverSeason } from "@/lib/types/driver";

interface SeasonHistoryProps {
  seasons: DriverSeason[];
}

export function SeasonHistory({ seasons }: SeasonHistoryProps) {
  const sorted = [...seasons].sort((a, b) => b.season_year - a.season_year);

  return (
    <div>
      <h3 className="text-sm font-semibold text-text-secondary mb-3 uppercase tracking-wider">
        Season history
      </h3>
      <div className="overflow-x-auto rounded-lg border border-border">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-border bg-surface-elevated">
              <th className="text-left px-4 py-2.5 text-text-muted font-medium">Year</th>
              <th className="text-left px-4 py-2.5 text-text-muted font-medium hidden sm:table-cell">Team</th>
              <th className="text-right px-4 py-2.5 text-text-muted font-medium">Pos</th>
              <th className="text-right px-4 py-2.5 text-text-muted font-medium">Pts</th>
              <th className="text-right px-4 py-2.5 text-text-muted font-medium">W</th>
              <th className="text-right px-4 py-2.5 text-text-muted font-medium">Pd</th>
              <th className="text-right px-4 py-2.5 text-text-muted font-medium">PP</th>
              <th className="text-right px-4 py-2.5 text-text-muted font-medium hidden md:table-cell">DNFs</th>
            </tr>
          </thead>
          <tbody>
            {sorted.map((season) => (
              <tr
                key={season.season_year}
                className="border-b border-border last:border-0 hover:bg-surface-hover transition-colors"
              >
                <td className="px-4 py-2.5">
                  <div className="flex items-center gap-1.5">
                    <span className="font-medium text-text-primary">
                      {season.season_year}
                    </span>
                    {season.championship_position === 1 && (
                      <Trophy className="w-3.5 h-3.5 text-gold" />
                    )}
                  </div>
                </td>
                <td className="px-4 py-2.5 text-text-secondary hidden sm:table-cell">
                  {season.team_name ?? "—"}
                </td>
                <td className="px-4 py-2.5 text-right font-mono text-text-primary">
                  {season.championship_position != null
                    ? `P${season.championship_position}`
                    : "—"}
                </td>
                <td className="px-4 py-2.5 text-right font-mono text-text-secondary">
                  {season.points}
                </td>
                <td className="px-4 py-2.5 text-right font-mono text-accent font-semibold">
                  {season.wins}
                </td>
                <td className="px-4 py-2.5 text-right font-mono text-text-primary">
                  {season.podiums}
                </td>
                <td className="px-4 py-2.5 text-right font-mono text-text-secondary">
                  {season.poles}
                </td>
                <td className="px-4 py-2.5 text-right font-mono text-text-muted hidden md:table-cell">
                  {season.dnfs}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
