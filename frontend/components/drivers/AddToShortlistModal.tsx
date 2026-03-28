"use client";

import { useState } from "react";
import * as Dialog from "@radix-ui/react-dialog";
import { X, Plus, BookmarkPlus } from "lucide-react";
import toast from "react-hot-toast";
import { Button } from "@/components/ui/Button";
import {
  useShortlists,
  useAddDriversToShortlist,
  useCreateShortlist,
} from "@/lib/hooks/useShortlists";
import type { DriverSummaryOut } from "@/lib/types/driver";

interface AddToShortlistModalProps {
  driver: DriverSummaryOut | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function AddToShortlistModal({
  driver,
  open,
  onOpenChange,
}: AddToShortlistModalProps) {
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [note, setNote] = useState("");
  const [creatingNew, setCreatingNew] = useState(false);
  const [newName, setNewName] = useState("");

  const { data: shortlists = [], isLoading } = useShortlists();
  const addDrivers = useAddDriversToShortlist();
  const createShortlist = useCreateShortlist();

  async function handleSubmit() {
    if (!driver) return;

    let targetId = selectedId;

    if (creatingNew) {
      if (!newName.trim()) return;
      const created = await createShortlist.mutateAsync({ name: newName.trim() });
      targetId = created.id;
    }

    if (!targetId) return;

    await addDrivers.mutateAsync({
      shortlistId: targetId,
      data: {
        driver_ids: [driver.id],
        notes: note.trim() ? { [driver.id]: note.trim() } : undefined,
      },
    });

    toast.success(`${driver.full_name} added to shortlist`);
    onOpenChange(false);
    setSelectedId(null);
    setNote("");
    setCreatingNew(false);
    setNewName("");
  }

  return (
    <Dialog.Root open={open} onOpenChange={onOpenChange}>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 bg-black/60 backdrop-blur-sm z-40 animate-fade-in" />
        <Dialog.Content className="fixed left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 z-50 w-full max-w-md bg-surface border border-border rounded-xl shadow-card-hover p-6 animate-slide-up">
          <div className="flex items-center justify-between mb-5">
            <Dialog.Title className="text-lg font-bold text-text-primary flex items-center gap-2">
              <BookmarkPlus className="w-5 h-5 text-accent" />
              Add to Shortlist
            </Dialog.Title>
            <Dialog.Close asChild>
              <button className="text-text-muted hover:text-text-primary transition-colors">
                <X className="w-5 h-5" />
              </button>
            </Dialog.Close>
          </div>

          {driver && (
            <p className="text-sm text-text-secondary mb-4">
              Adding{" "}
              <span className="font-semibold text-text-primary">
                {driver.full_name}
              </span>{" "}
              to a shortlist
            </p>
          )}

          {!creatingNew ? (
            <>
              {isLoading ? (
                <p className="text-sm text-text-muted">Loading shortlists…</p>
              ) : shortlists.length === 0 ? (
                <p className="text-sm text-text-secondary mb-4">
                  You have no shortlists yet.
                </p>
              ) : (
                <div className="flex flex-col gap-2 mb-4 max-h-48 overflow-y-auto">
                  {shortlists.map((sl) => (
                    <button
                      key={sl.id}
                      type="button"
                      onClick={() => setSelectedId(sl.id)}
                      className={`flex items-center justify-between px-3 py-2.5 rounded-lg border text-sm transition-colors ${
                        selectedId === sl.id
                          ? "border-accent bg-accent-muted text-text-primary"
                          : "border-border bg-surface-elevated text-text-secondary hover:border-accent/40"
                      }`}
                    >
                      <span className="font-medium">{sl.name}</span>
                      <span className="text-xs text-text-muted">
                        {sl.driver_ids.length} drivers
                      </span>
                    </button>
                  ))}
                </div>
              )}

              <button
                type="button"
                onClick={() => setCreatingNew(true)}
                className="flex items-center gap-2 text-sm text-accent hover:text-accent-hover transition-colors mb-4"
              >
                <Plus className="w-4 h-4" />
                Create new shortlist
              </button>
            </>
          ) : (
            <div className="mb-4">
              <input
                autoFocus
                placeholder="Shortlist name"
                value={newName}
                onChange={(e) => setNewName(e.target.value)}
                className="w-full bg-surface border border-border rounded px-3 py-2 text-text-primary placeholder:text-text-muted text-sm focus:outline-none focus:ring-2 focus:ring-accent mb-2"
              />
              <button
                type="button"
                onClick={() => setCreatingNew(false)}
                className="text-xs text-text-muted hover:text-text-secondary transition-colors"
              >
                ← Back to existing
              </button>
            </div>
          )}

          <textarea
            placeholder="Note (optional)"
            value={note}
            onChange={(e) => setNote(e.target.value)}
            rows={2}
            className="w-full bg-surface border border-border rounded px-3 py-2 text-text-primary placeholder:text-text-muted text-sm focus:outline-none focus:ring-2 focus:ring-accent resize-none mb-4"
          />

          <div className="flex gap-2 justify-end">
            <Dialog.Close asChild>
              <Button variant="secondary">Cancel</Button>
            </Dialog.Close>
            <Button
              onClick={handleSubmit}
              loading={addDrivers.isPending || createShortlist.isPending}
              disabled={!creatingNew && !selectedId}
            >
              Add to shortlist
            </Button>
          </div>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
}
