import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  getShortlists,
  getShortlist,
  createShortlist,
  deleteShortlist,
  addDriversToShortlist,
  removeDriverFromShortlist,
} from "@/lib/api/shortlists";
import { shortlistKeys } from "@/lib/utils/queryClient";
import type { ShortlistCreate, AddDriversRequest } from "@/lib/types/shortlist";

export function useShortlists() {
  return useQuery({
    queryKey: shortlistKeys.list(),
    queryFn: getShortlists,
  });
}

export function useShortlist(id: string) {
  return useQuery({
    queryKey: shortlistKeys.detail(id),
    queryFn: () => getShortlist(id),
    enabled: !!id,
  });
}

export function useCreateShortlist() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: ShortlistCreate) => createShortlist(data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: shortlistKeys.list() });
    },
  });
}

export function useDeleteShortlist() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => deleteShortlist(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: shortlistKeys.list() });
    },
  });
}

export function useAddDriversToShortlist() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({
      shortlistId,
      data,
    }: {
      shortlistId: string;
      data: AddDriversRequest;
    }) => addDriversToShortlist(shortlistId, data),
    onSuccess: (_, { shortlistId }) => {
      qc.invalidateQueries({ queryKey: shortlistKeys.detail(shortlistId) });
      qc.invalidateQueries({ queryKey: shortlistKeys.list() });
    },
  });
}

export function useRemoveDriverFromShortlist() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({
      shortlistId,
      driverId,
    }: {
      shortlistId: string;
      driverId: string;
    }) => removeDriverFromShortlist(shortlistId, driverId),
    onMutate: async ({ shortlistId, driverId }) => {
      await qc.cancelQueries({ queryKey: shortlistKeys.detail(shortlistId) });
      const previous = qc.getQueryData(shortlistKeys.detail(shortlistId));
      qc.setQueryData(shortlistKeys.detail(shortlistId), (old: any) => {
        if (!old) return old;
        return {
          ...old,
          driver_ids: old.driver_ids.filter((id: string) => id !== driverId),
        };
      });
      return { previous };
    },
    onError: (_err, { shortlistId }, context) => {
      if (context?.previous) {
        qc.setQueryData(shortlistKeys.detail(shortlistId), context.previous);
      }
    },
    onSettled: (_data, _err, { shortlistId }) => {
      qc.invalidateQueries({ queryKey: shortlistKeys.detail(shortlistId) });
    },
  });
}
