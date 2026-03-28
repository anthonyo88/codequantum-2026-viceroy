"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as Dialog from "@radix-ui/react-dialog";
import { X, Bookmark } from "lucide-react";
import toast from "react-hot-toast";
import { Input } from "@/components/ui/Input";
import { Button } from "@/components/ui/Button";
import { createShortlistSchema, type CreateShortlistFormData } from "@/lib/schemas/shortlist";
import { useCreateShortlist } from "@/lib/hooks/useShortlists";

interface CreateShortlistModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function CreateShortlistModal({ open, onOpenChange }: CreateShortlistModalProps) {
  const createShortlist = useCreateShortlist();
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<CreateShortlistFormData>({
    resolver: zodResolver(createShortlistSchema),
  });

  async function onSubmit(data: CreateShortlistFormData) {
    await createShortlist.mutateAsync(data);
    toast.success("Shortlist created");
    reset();
    onOpenChange(false);
  }

  return (
    <Dialog.Root open={open} onOpenChange={onOpenChange}>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 bg-black/60 backdrop-blur-sm z-40 animate-fade-in" />
        <Dialog.Content className="fixed left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 z-50 w-full max-w-md bg-surface border border-border rounded-xl shadow-card-hover p-6 animate-slide-up">
          <div className="flex items-center justify-between mb-5">
            <Dialog.Title className="text-lg font-bold text-text-primary flex items-center gap-2">
              <Bookmark className="w-5 h-5 text-accent" />
              New Shortlist
            </Dialog.Title>
            <Dialog.Close asChild>
              <button className="text-text-muted hover:text-text-primary transition-colors">
                <X className="w-5 h-5" />
              </button>
            </Dialog.Close>
          </div>

          <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-4">
            <Input
              id="name"
              label="Name"
              placeholder="2025 Junior Prospects"
              error={errors.name?.message}
              {...register("name")}
            />

            <div className="flex flex-col gap-1.5">
              <label htmlFor="description" className="text-sm font-medium text-text-secondary">
                Description (optional)
              </label>
              <textarea
                id="description"
                rows={3}
                placeholder="Describe this shortlist…"
                className="bg-surface border border-border rounded px-3 py-2 text-text-primary placeholder:text-text-muted text-sm focus:outline-none focus:ring-2 focus:ring-accent resize-none"
                {...register("description")}
              />
            </div>

            <div className="flex gap-2 justify-end pt-2">
              <Dialog.Close asChild>
                <Button variant="secondary">Cancel</Button>
              </Dialog.Close>
              <Button type="submit" loading={isSubmitting || createShortlist.isPending}>
                Create shortlist
              </Button>
            </div>
          </form>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
}
