"use client";

import { useRouter } from "next/navigation";
import { Users, Calendar } from "lucide-react";
import { Card } from "@/components/ui/Card";
import { formatDate } from "@/lib/utils/formatters";
import type { ShortlistOut } from "@/lib/types/shortlist";

interface ShortlistCardProps {
  shortlist: ShortlistOut;
}

export function ShortlistCard({ shortlist }: ShortlistCardProps) {
  const router = useRouter();

  return (
    <Card
      hover
      onClick={() => router.push(`/shortlists/${shortlist.id}`)}
      className="flex flex-col gap-3 animate-fade-in"
    >
      <div>
        <h3 className="font-bold text-text-primary text-base leading-tight">
          {shortlist.name}
        </h3>
        {shortlist.description && (
          <p className="text-sm text-text-secondary mt-1 line-clamp-2">
            {shortlist.description}
          </p>
        )}
      </div>

      <div className="flex items-center justify-between text-xs text-text-muted mt-auto pt-2 border-t border-border-subtle">
        <span className="flex items-center gap-1.5">
          <Users className="w-3.5 h-3.5" />
          {shortlist.driver_ids.length} driver{shortlist.driver_ids.length !== 1 ? "s" : ""}
        </span>
        <span className="flex items-center gap-1.5">
          <Calendar className="w-3.5 h-3.5" />
          {formatDate(shortlist.created_at)}
        </span>
      </div>
    </Card>
  );
}
