"use client";

import { useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { ArrowLeft, Users, Plus } from "lucide-react";
import { PageContainer } from "@/components/layout/PageContainer";
import { ShortlistDriverRow } from "@/components/shortlists/ShortlistDriverRow";
import { Button } from "@/components/ui/Button";
import { Skeleton } from "@/components/ui/Skeleton";
import { useShortlist, useRemoveDriverFromShortlist } from "@/lib/hooks/useShortlists";
import { useDriver } from "@/lib/hooks/useDriver";
import { formatDate } from "@/lib/utils/formatters";
import toast from "react-hot-toast";
import Link from "next/link";

export default function ShortlistDetailPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const { data: shortlist, isLoading } = useShortlist(id);
  const removeDriver = useRemoveDriverFromShortlist();
  const [removingId, setRemovingId] = useState<string | null>(null);

  async function handleRemove(driverId: string) {
    setRemovingId(driverId);
    try {
      await removeDriver.mutateAsync({ shortlistId: id, driverId });
      toast.success("Driver removed from shortlist");
    } catch {
      toast.error("Failed to remove driver");
    } finally {
      setRemovingId(null);
    }
  }

  return (
    <PageContainer>
      <div className="flex flex-col gap-6">
        <button
          onClick={() => router.back()}
          className="flex items-center gap-1.5 text-sm text-text-muted hover:text-text-secondary transition-colors w-fit"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to shortlists
        </button>

        {isLoading ? (
          <div className="flex flex-col gap-3">
            <Skeleton className="h-8 w-48" />
            <Skeleton className="h-4 w-32" />
          </div>
        ) : shortlist ? (
          <>
            <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
              <div>
                <h1 className="text-2xl font-bold text-text-primary">
                  {shortlist.name}
                </h1>
                {shortlist.description && (
                  <p className="text-text-secondary text-sm mt-1">
                    {shortlist.description}
                  </p>
                )}
                <p className="text-xs text-text-muted mt-2">
                  Created {formatDate(shortlist.created_at)} ·{" "}
                  {shortlist.driver_ids.length} driver{shortlist.driver_ids.length !== 1 ? "s" : ""}
                </p>
              </div>
              <Link href="/drivers">
                <Button variant="secondary">
                  <Plus className="w-4 h-4" />
                  Add drivers
                </Button>
              </Link>
            </div>

            {shortlist.driver_ids.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-16 text-center">
                <Users className="w-10 h-10 text-border mb-4" />
                <h3 className="text-base font-semibold text-text-primary mb-2">
                  No drivers yet
                </h3>
                <p className="text-sm text-text-secondary mb-4">
                  Browse drivers and add them to this shortlist.
                </p>
                <Link href="/drivers">
                  <Button>Browse drivers</Button>
                </Link>
              </div>
            ) : (
              <div className="flex flex-col gap-2">
                {shortlist.driver_ids.map((driverId) => (
                  <DriverRowWrapper
                    key={driverId}
                    driverId={driverId}
                    note={shortlist.notes[driverId]}
                    onRemove={() => handleRemove(driverId)}
                    isRemoving={removingId === driverId}
                  />
                ))}
              </div>
            )}
          </>
        ) : (
          <p className="text-text-secondary">Shortlist not found.</p>
        )}
      </div>
    </PageContainer>
  );
}

function DriverRowWrapper({
  driverId,
  note,
  onRemove,
  isRemoving,
}: {
  driverId: string;
  note?: string;
  onRemove: () => void;
  isRemoving?: boolean;
}) {
  const { data: driver, isLoading } = useDriver(driverId);

  if (isLoading) {
    return <Skeleton className="h-16 rounded-lg" />;
  }

  if (!driver) return null;

  return (
    <ShortlistDriverRow
      driver={{
        id: driver.id,
        full_name: driver.full_name,
        nationality: driver.nationality,
        active_status: driver.active_status,
        career_stats: driver.career_stats,
      }}
      note={note}
      onRemove={onRemove}
      isRemoving={isRemoving}
    />
  );
}
