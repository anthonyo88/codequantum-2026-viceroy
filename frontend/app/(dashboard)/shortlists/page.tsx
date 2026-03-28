"use client";

import { useState } from "react";
import { Plus, Bookmark } from "lucide-react";
import { PageContainer } from "@/components/layout/PageContainer";
import { ShortlistCard } from "@/components/shortlists/ShortlistCard";
import { CreateShortlistModal } from "@/components/shortlists/CreateShortlistModal";
import { Button } from "@/components/ui/Button";
import { Skeleton } from "@/components/ui/Skeleton";
import { useShortlists } from "@/lib/hooks/useShortlists";

export default function ShortlistsPage() {
  const [createOpen, setCreateOpen] = useState(false);
  const { data: shortlists = [], isLoading } = useShortlists();

  return (
    <PageContainer>
      <div className="flex flex-col gap-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-text-primary">Shortlists</h1>
            {!isLoading && (
              <p className="text-sm text-text-muted mt-0.5">
                {shortlists.length} shortlist{shortlists.length !== 1 ? "s" : ""}
              </p>
            )}
          </div>
          <Button onClick={() => setCreateOpen(true)}>
            <Plus className="w-4 h-4" />
            New shortlist
          </Button>
        </div>

        {isLoading ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {Array.from({ length: 6 }).map((_, i) => (
              <Skeleton key={i} className="h-32 rounded-lg" />
            ))}
          </div>
        ) : shortlists.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-20 text-center">
            <Bookmark className="w-12 h-12 text-border mb-4" />
            <h3 className="text-lg font-semibold text-text-primary mb-2">
              No shortlists yet
            </h3>
            <p className="text-text-secondary text-sm mb-6">
              Create a shortlist to start organizing drivers for your team.
            </p>
            <Button onClick={() => setCreateOpen(true)}>
              <Plus className="w-4 h-4" />
              Create your first shortlist
            </Button>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {shortlists.map((shortlist) => (
              <ShortlistCard key={shortlist.id} shortlist={shortlist} />
            ))}
          </div>
        )}
      </div>

      <CreateShortlistModal open={createOpen} onOpenChange={setCreateOpen} />
    </PageContainer>
  );
}
