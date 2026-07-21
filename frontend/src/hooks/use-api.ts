import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import type {
  Dashboard,
  ProviderInfo,
  PullRequest,
  PullRequestDetail,
  Repository,
  Review,
  Settings,
  User,
} from "@/types";

export function useDashboard() {
  return useQuery({
    queryKey: ["dashboard"],
    queryFn: () => api.get<Dashboard>("/dashboard"),
  });
}

export function useRepositories(q?: string) {
  return useQuery({
    queryKey: ["repositories", q],
    queryFn: () => api.get<Repository[]>(`/repositories${q ? `?q=${encodeURIComponent(q)}` : ""}`),
  });
}

export function usePullRequests(repositoryId?: string) {
  return useQuery({
    queryKey: ["pullrequests", repositoryId],
    queryFn: () =>
      api.get<PullRequest[]>(
        `/pullrequests${repositoryId ? `?repository_id=${repositoryId}` : ""}`,
      ),
  });
}

export function usePullRequest(id: string) {
  return useQuery({
    queryKey: ["pullrequest", id],
    queryFn: () => api.get<PullRequestDetail>(`/pullrequests/${id}`),
    enabled: !!id,
  });
}

export function useStartReview() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (pull_request_id: string) =>
      api.post<Review>("/reviews/start", { pull_request_id }),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ["dashboard"] });
    },
  });
}

export function useReview(id: string) {
  return useQuery({
    queryKey: ["review", id],
    queryFn: () => api.get<Review>(`/reviews/${id}`),
    enabled: !!id,
  });
}

export function useProviders() {
  return useQuery({
    queryKey: ["providers"],
    queryFn: () => api.get<ProviderInfo[]>("/providers"),
  });
}

export function useSettings() {
  return useQuery({
    queryKey: ["settings"],
    queryFn: () => api.get<Settings>("/settings"),
  });
}

export function useUpdateSettings() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (body: Partial<Settings> & Record<string, unknown>) =>
      api.patch<Settings>("/settings", body),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ["settings"] });
    },
  });
}

export function useMe() {
  return useQuery({
    queryKey: ["me"],
    queryFn: () => api.get<User>("/auth/me"),
    retry: false,
  });
}

export function useDemoLogin() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: () => api.post<User>("/auth/demo-login"),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ["me"] });
    },
  });
}
