import { QueryClient } from "@tanstack/react-query";

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000,
      gcTime: 10 * 60 * 1000,
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

export const driverKeys = {
  all: ["drivers"] as const,
  list: (params: object) => ["drivers", "list", params] as const,
  detail: (id: string) => ["drivers", "detail", id] as const,
  seasons: (id: string) => ["drivers", "seasons", id] as const,
};

export const shortlistKeys = {
  all: ["shortlists"] as const,
  list: () => ["shortlists", "list"] as const,
  detail: (id: string) => ["shortlists", "detail", id] as const,
};
