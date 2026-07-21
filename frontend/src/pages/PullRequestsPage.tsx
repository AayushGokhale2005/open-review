import { Link } from "react-router-dom";
import { usePullRequests } from "@/hooks/use-api";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { relativeTime } from "@/lib/utils";

export function PullRequestsPage() {
  const { data, isLoading } = usePullRequests();

  return (
    <div className="p-6 md:p-8 space-y-6">
      <div>
        <h1 className="font-display text-2xl font-semibold">Pull Requests</h1>
        <p className="mt-1 text-sm text-muted-foreground">Open PRs across connected repositories.</p>
      </div>

      {isLoading && <Skeleton className="h-40" />}

      <div className="overflow-hidden rounded-xl border border-border bg-card/60">
        <ul className="divide-y divide-border">
          {data?.map((pr) => (
            <li key={pr.id}>
              <Link
                to={`/app/pull-requests/${pr.id}`}
                className="flex flex-col gap-2 px-5 py-4 transition hover:bg-accent sm:flex-row sm:items-center sm:justify-between"
              >
                <div className="min-w-0">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="font-mono text-xs text-primary">#{pr.number}</span>
                    <span className="font-medium truncate">{pr.title}</span>
                    {pr.draft && <Badge variant="outline">draft</Badge>}
                  </div>
                  <div className="mt-1 text-xs text-muted-foreground">
                    {pr.author} · {pr.source_branch} → {pr.target_branch} ·{" "}
                    {relativeTime(pr.updated_at)}
                  </div>
                </div>
                <div className="flex items-center gap-3 text-xs">
                  <span className="text-success">+{pr.additions}</span>
                  <span className="text-destructive">−{pr.deletions}</span>
                  <span className="text-muted-foreground">{pr.changed_files} files</span>
                  {(pr.labels ?? []).map((l) => (
                    <Badge key={l} variant="outline">
                      {l}
                    </Badge>
                  ))}
                </div>
              </Link>
            </li>
          ))}
        </ul>
        {data?.length === 0 && (
          <div className="py-16 text-center text-sm text-muted-foreground">No open pull requests.</div>
        )}
      </div>
    </div>
  );
}
