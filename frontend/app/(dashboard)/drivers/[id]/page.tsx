"use client";

import { useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { ArrowLeft, BookmarkPlus, Calendar, Globe } from "lucide-react";
import { PageContainer } from "@/components/layout/PageContainer";
import { DriverStats } from "@/components/drivers/DriverStats";
import { SeasonHistory } from "@/components/drivers/SeasonHistory";
import { AddToShortlistModal } from "@/components/drivers/AddToShortlistModal";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Skeleton } from "@/components/ui/Skeleton";
import { useDriver } from "@/lib/hooks/useDriver";
import { calcAge, formatDate, nationalityFlag } from "@/lib/utils/formatters";

export default function DriverDetailPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const { data: driver, isLoading, isError } = useDriver(id);
  const [shortlistOpen, setShortlistOpen] = useState(false);

  if (isError) {
    return (
      <PageContainer>
        <div className="flex flex-col items-center justify-center py-20">
          <p className="text-text-secondary">Driver not found.</p>
          <Button
            variant="ghost"
            className="mt-4"
            onClick={() => router.push("/drivers")}
          >
            Back to drivers
          </Button>
        </div>
      </PageContainer>
    );
  }

  return (
    <PageContainer>
      <div className="flex flex-col gap-6">
        {/* Back button */}
        <button
          onClick={() => router.back()}
          className="flex items-center gap-1.5 text-sm text-text-muted hover:text-text-secondary transition-colors w-fit"
        >
          <ArrowLeft className="w-4 h-4" />
          Back
        </button>

        {/* Driver header */}
        {isLoading ? (
          <div className="flex flex-col gap-3">
            <Skeleton className="h-8 w-64" />
            <Skeleton className="h-4 w-40" />
          </div>
        ) : driver ? (
          <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
            <div>
              <div className="flex items-center gap-3 flex-wrap">
                <h1 className="text-3xl font-black text-text-primary tracking-tight">
                  {driver.full_name}
                </h1>
                <Badge variant={driver.active_status ? "active" : "retired"}>
                  {driver.active_status ? "Active" : "Retired"}
                </Badge>
                {driver.career_stats.championships_won > 0 && (
                  <Badge variant="gold">
                    {driver.career_stats.championships_won}× Champion
                  </Badge>
                )}
              </div>

              <div className="flex items-center gap-4 mt-2 text-sm text-text-secondary flex-wrap">
                <span className="flex items-center gap-1.5">
                  <Globe className="w-3.5 h-3.5" />
                  {nationalityFlag(driver.nationality)} {driver.nationality}
                </span>
                {driver.date_of_birth && (
                  <span className="flex items-center gap-1.5">
                    <Calendar className="w-3.5 h-3.5" />
                    {calcAge(driver.date_of_birth)} years old
                  </span>
                )}
                {driver.license_grade && (
                  <span className="text-text-muted">
                    License: {driver.license_grade}
                  </span>
                )}
              </div>

              {driver.biography && (
                <p className="text-sm text-text-secondary mt-3 max-w-2xl leading-relaxed">
                  {driver.biography}
                </p>
              )}
            </div>

            <Button
              onClick={() => setShortlistOpen(true)}
              className="flex-shrink-0"
            >
              <BookmarkPlus className="w-4 h-4" />
              Add to shortlist
            </Button>
          </div>
        ) : null}

        {/* Stats */}
        {isLoading ? (
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            {[0, 1, 2, 3].map((i) => (
              <Skeleton key={i} className="h-24 rounded-lg" />
            ))}
          </div>
        ) : (
          driver && <DriverStats driver={driver} />
        )}

        {/* Season history */}
        {!isLoading && driver && driver.seasons.length > 0 && (
          <SeasonHistory seasons={driver.seasons} />
        )}
      </div>

      {driver && (
        <AddToShortlistModal
          driver={{
            id: driver.id,
            full_name: driver.full_name,
            nationality: driver.nationality,
            active_status: driver.active_status,
            career_stats: driver.career_stats,
          }}
          open={shortlistOpen}
          onOpenChange={setShortlistOpen}
        />
      )}
    </PageContainer>
  );
}
