"use client";

import { Trophy, Flag, Star, Zap } from "lucide-react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";
import { formatPct } from "@/lib/utils/formatters";
import type { DriverOut } from "@/lib/types/driver";

interface DriverStatsProps {
  driver: DriverOut;
}

export function DriverStats({ driver }: DriverStatsProps) {
  const stats = driver.career_stats;

  const chartData = driver.seasons
    .sort((a, b) => a.season_year - b.season_year)
    .map((s) => ({ year: s.season_year, wins: s.wins, podiums: s.podiums }));

  return (
    <div className="flex flex-col gap-6">
      {/* Stat row */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <StatTile
          icon={<Trophy className="w-5 h-5 text-gold" />}
          value={stats.championships_won}
          label="Championships"
        />
        <StatTile
          icon={<Flag className="w-5 h-5 text-accent" />}
          value={stats.total_wins}
          label="Race wins"
        />
        <StatTile
          icon={<Star className="w-5 h-5 text-text-secondary" />}
          value={stats.total_podiums}
          label="Podiums"
        />
        <StatTile
          icon={<Zap className="w-5 h-5 text-text-secondary" />}
          value={formatPct(stats.career_win_rate)}
          label="Win rate"
        />
      </div>

      {/* Secondary stats */}
      <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
        <MiniStat label="Pole positions" value={stats.total_pole_positions} />
        <MiniStat label="Fastest laps" value={stats.total_fastest_laps} />
        <MiniStat label="Podium rate" value={formatPct(stats.career_podium_rate)} />
        <MiniStat label="DNF rate" value={formatPct(stats.dnf_rate)} />
        <MiniStat label="Races started" value={stats.total_race_starts} />
        <MiniStat
          label="Avg quali pos"
          value={
            stats.avg_qualifying_position != null
              ? `P${stats.avg_qualifying_position.toFixed(1)}`
              : "—"
          }
        />
      </div>

      {/* Season wins chart */}
      {chartData.length > 0 && (
        <div>
          <h3 className="text-sm font-semibold text-text-secondary mb-3 uppercase tracking-wider">
            Wins per season
          </h3>
          <div className="h-40">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData} barSize={16}>
                <XAxis
                  dataKey="year"
                  tick={{ fill: "#666", fontSize: 11 }}
                  axisLine={false}
                  tickLine={false}
                />
                <YAxis
                  tick={{ fill: "#666", fontSize: 11 }}
                  axisLine={false}
                  tickLine={false}
                  allowDecimals={false}
                />
                <Tooltip
                  contentStyle={{
                    background: "#1a1a1a",
                    border: "1px solid #2a2a2a",
                    borderRadius: "8px",
                    fontSize: "12px",
                    color: "#fff",
                  }}
                  cursor={{ fill: "rgba(225, 6, 0, 0.08)" }}
                />
                <Bar dataKey="wins" radius={[3, 3, 0, 0]}>
                  {chartData.map((_, i) => (
                    <Cell key={i} fill="#e10600" opacity={0.85} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}
    </div>
  );
}

function StatTile({
  icon,
  value,
  label,
}: {
  icon: React.ReactNode;
  value: string | number;
  label: string;
}) {
  return (
    <div className="bg-surface border border-border rounded-lg p-4 flex flex-col gap-2">
      {icon}
      <div className="text-2xl font-bold text-text-primary font-mono leading-none">
        {value}
      </div>
      <div className="text-xs text-text-muted">{label}</div>
    </div>
  );
}

function MiniStat({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="bg-surface-elevated rounded-lg px-3 py-2.5 flex justify-between items-center">
      <span className="text-xs text-text-muted">{label}</span>
      <span className="text-sm font-semibold text-text-primary font-mono">
        {value}
      </span>
    </div>
  );
}
