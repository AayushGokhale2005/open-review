import { useDashboard } from "@/hooks/use-api";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";

export function ReviewsPage() {
  const { data, isLoading } = useDashboard();
  const reviews = data?.recent_reviews ?? [];

  return (
    <div className="p-6 md:p-8 space-y-6">
      <div>
        <h1 className="font-display text-2xl font-semibold">Reviews</h1>
        <p className="mt-1 text-sm text-muted-foreground">AI review history for this machine.</p>
      </div>
      {isLoading && <Skeleton className="h-40" />}
      <div className="space-y-3">
        {reviews.map((r) => (
          <article key={r.id} className="rounded-xl border border-border bg-card/60 p-5">
            <div className="flex flex-wrap items-center gap-2">
              <Badge>{r.status}</Badge>
              <Badge variant="outline">{r.verdict ?? "—"}</Badge>
              <span className="text-sm text-muted-foreground">
                {r.provider} / {r.model}
              </span>
              {r.score != null && (
                <span className="ml-auto font-display text-lg font-semibold">{r.score}</span>
              )}
            </div>
            <p className="mt-3 text-sm">{r.summary}</p>
            <p className="mt-2 text-xs text-muted-foreground">
              {r.comments.length} comments · {r.completed_at ?? r.created_at}
            </p>
          </article>
        ))}
        {!isLoading && reviews.length === 0 && (
          <div className="rounded-xl border border-dashed border-border py-16 text-center text-sm text-muted-foreground">
            No reviews yet. Open a pull request and run an AI review.
          </div>
        )}
      </div>
    </div>
  );
}
