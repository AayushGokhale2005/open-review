import { useState } from "react";
import { Search, Star, GitPullRequest } from "lucide-react";
import { useRepositories } from "@/hooks/use-api";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { formatNumber, relativeTime } from "@/lib/utils";

export function RepositoriesPage() {
  const [q, setQ] = useState("");
  const { data, isLoading } = useRepositories(q || undefined);

  return (
    <div className="p-6 md:p-8 space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h1 className="font-display text-2xl font-semibold">Repositories</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Connect, clone, and import repositories into ~/AIReviewer/repos/
          </p>
        </div>
        <div className="relative w-full sm:w-72">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            className="pl-9"
            placeholder="Search repositories…"
            value={q}
            onChange={(e) => setQ(e.target.value)}
          />
        </div>
      </div>

      {isLoading && (
        <div className="grid gap-4 sm:grid-cols-2">
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} className="h-36" />
          ))}
        </div>
      )}

      <div className="grid gap-4 sm:grid-cols-2">
        {data?.map((repo) => (
          <article
            key={repo.id}
            className="rounded-xl border border-border bg-card/60 p-5 transition hover:border-primary/30"
          >
            <div className="flex items-start justify-between gap-3">
              <div>
                <h2 className="font-medium">{repo.full_name}</h2>
                <p className="mt-1 text-sm text-muted-foreground line-clamp-2">
                  {repo.description ?? "No description"}
                </p>
              </div>
              <Badge variant="outline">{repo.provider}</Badge>
            </div>
            <div className="mt-4 flex flex-wrap items-center gap-3 text-xs text-muted-foreground">
              <span>{repo.language ?? "Unknown"}</span>
              <span className="inline-flex items-center gap-1">
                <Star className="h-3 w-3" /> {formatNumber(repo.stars)}
              </span>
              <span>branch · {repo.default_branch}</span>
              <span className="inline-flex items-center gap-1">
                <GitPullRequest className="h-3 w-3" /> {repo.open_pr_count} open
              </span>
              <span>health {repo.health_score}%</span>
              {repo.last_reviewed_at && (
                <span>reviewed {relativeTime(repo.last_reviewed_at)}</span>
              )}
            </div>
          </article>
        ))}
      </div>

      {data?.length === 0 && (
        <div className="rounded-xl border border-dashed border-border py-16 text-center text-sm text-muted-foreground">
          No repositories found. Import a local folder or connect GitHub / GitLab.
        </div>
      )}
    </div>
  );
}
