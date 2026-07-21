import { useMemo, useState } from "react";
import { useParams } from "react-router-dom";
import { toast } from "sonner";
import {
  Check,
  MessageSquare,
  XCircle,
  Play,
  FileCode,
} from "lucide-react";
import { usePullRequest, useStartReview } from "@/hooks/use-api";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Separator } from "@/components/ui/separator";
import type { Review, ReviewComment } from "@/types";
import { cn } from "@/lib/utils";

export function PullRequestDetailPage() {
  const { id = "" } = useParams();
  const { data: pr, isLoading } = usePullRequest(id);
  const startReview = useStartReview();
  const [activeFile, setActiveFile] = useState<string | null>(null);
  const [review, setReview] = useState<Review | null>(null);

  const files = pr?.files ?? [];
  const selected = useMemo(
    () => files.find((f) => f.path === (activeFile ?? files[0]?.path)) ?? null,
    [files, activeFile],
  );

  const runReview = async () => {
    try {
      const result = await startReview.mutateAsync(id);
      setReview(result);
      toast.success("AI review completed");
    } catch {
      toast.error("Could not start review — is the backend running?");
    }
  };

  if (isLoading) {
    return (
      <div className="p-8 space-y-4">
        <Skeleton className="h-10 w-1/2" />
        <Skeleton className="h-[60vh]" />
      </div>
    );
  }

  if (!pr) {
    return <div className="p-8 text-muted-foreground">Pull request not found.</div>;
  }

  return (
    <div className="flex h-[calc(100vh)] flex-col">
      <header className="shrink-0 border-b border-border px-6 py-4">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 text-xs text-muted-foreground">
              <span>{pr.repository?.full_name}</span>
              <span>·</span>
              <span className="font-mono text-primary">#{pr.number}</span>
            </div>
            <h1 className="mt-1 font-display text-xl font-semibold">{pr.title}</h1>
            <p className="mt-1 text-sm text-muted-foreground">
              {pr.author} wants to merge {pr.source_branch} → {pr.target_branch}
            </p>
          </div>
          <div className="flex flex-wrap gap-2">
            <Button size="sm" onClick={() => void runReview()} disabled={startReview.isPending}>
              <Play className="h-3.5 w-3.5" />
              {startReview.isPending ? "Reviewing…" : "Run AI Review"}
            </Button>
            <Button size="sm" variant="secondary">
              <Check className="h-3.5 w-3.5" /> Approve
            </Button>
            <Button size="sm" variant="outline">
              <XCircle className="h-3.5 w-3.5" /> Request changes
            </Button>
            <Button size="sm" variant="ghost">
              <MessageSquare className="h-3.5 w-3.5" /> Comment
            </Button>
          </div>
        </div>
        {review && (
          <div className="mt-4 rounded-lg border border-primary/20 bg-primary/5 p-3 text-sm">
            <div className="flex flex-wrap items-center gap-3">
              <Badge>{review.verdict}</Badge>
              <span className="font-medium">Score {review.score}/100</span>
              <span className="text-muted-foreground">{review.summary}</span>
            </div>
          </div>
        )}
      </header>

      <div className="grid min-h-0 flex-1 grid-cols-1 lg:grid-cols-[220px_1fr_320px]">
        {/* File explorer */}
        <aside className="hidden overflow-y-auto border-r border-border lg:block">
          <div className="px-3 py-3 text-xs font-medium text-muted-foreground">Changed files</div>
          <ul>
            {files.map((f) => (
              <li key={f.path}>
                <button
                  type="button"
                  onClick={() => setActiveFile(f.path)}
                  className={cn(
                    "flex w-full items-start gap-2 px-3 py-2 text-left text-xs hover:bg-accent",
                    (activeFile ?? files[0]?.path) === f.path && "bg-accent",
                  )}
                >
                  <FileCode className="mt-0.5 h-3.5 w-3.5 shrink-0 text-muted-foreground" />
                  <span className="min-w-0">
                    <span className="block truncate font-mono">{f.path.split("/").pop()}</span>
                    <span className="text-muted-foreground">
                      <span className="text-success">+{f.additions}</span>{" "}
                      <span className="text-destructive">−{f.deletions}</span>
                    </span>
                  </span>
                </button>
              </li>
            ))}
          </ul>
        </aside>

        {/* Diff viewer */}
        <section className="min-w-0 overflow-auto border-r border-border">
          <div className="sticky top-0 z-10 border-b border-border bg-card/90 px-4 py-2 font-mono text-xs backdrop-blur">
            {selected?.path ?? "No file selected"}
            {selected && (
              <Badge variant="outline" className="ml-2">
                {selected.status}
              </Badge>
            )}
          </div>
          <pre className="p-4 font-mono text-xs leading-6">
            {(selected?.patch ?? "No diff available").split("\n").map((line, i) => (
              <div
                key={i}
                className={cn(
                  "px-2 -mx-2",
                  line.startsWith("+") && !line.startsWith("+++") && "bg-success/10 text-success",
                  line.startsWith("-") && !line.startsWith("---") && "bg-destructive/10 text-destructive",
                  line.startsWith("@@") && "text-primary",
                )}
              >
                {line || " "}
              </div>
            ))}
          </pre>
        </section>

        {/* Conversation / comments */}
        <aside className="overflow-y-auto">
          <div className="px-4 py-3 text-sm font-medium">Conversation</div>
          <Separator />
          <div className="space-y-3 p-4">
            <TimelineItem
              title="Pull request opened"
              body={`${pr.author} opened this pull request`}
            />
            {review?.comments.map((c) => (
              <CommentCard key={c.id} comment={c} />
            ))}
            {!review && (
              <p className="text-xs text-muted-foreground">
                Run an AI review to populate inline findings from security, performance, and other
                specialist agents.
              </p>
            )}
          </div>
        </aside>
      </div>
    </div>
  );
}

function TimelineItem({ title, body }: { title: string; body: string }) {
  return (
    <div className="rounded-lg border border-border bg-muted/40 p-3 text-sm">
      <div className="font-medium">{title}</div>
      <div className="mt-1 text-xs text-muted-foreground">{body}</div>
    </div>
  );
}

function CommentCard({ comment }: { comment: ReviewComment }) {
  const severityVariant =
    comment.severity === "critical" || comment.severity === "error"
      ? "destructive"
      : comment.severity === "warning"
        ? "warning"
        : "default";

  return (
    <div className="rounded-lg border border-border bg-card p-3 text-sm">
      <div className="flex flex-wrap items-center gap-2">
        <Badge variant={severityVariant}>{comment.severity}</Badge>
        <Badge variant="outline">{comment.agent}</Badge>
      </div>
      <div className="mt-2 font-medium">{comment.title}</div>
      <p className="mt-1 text-xs text-muted-foreground">{comment.body}</p>
      {comment.file_path && (
        <p className="mt-2 font-mono text-[10px] text-muted-foreground">
          {comment.file_path}
          {comment.line_start ? `:${comment.line_start}` : ""}
        </p>
      )}
      {comment.suggestion && (
        <pre className="mt-2 overflow-x-auto rounded-md bg-muted p-2 font-mono text-[10px] text-success">
          {comment.suggestion}
        </pre>
      )}
    </div>
  );
}
