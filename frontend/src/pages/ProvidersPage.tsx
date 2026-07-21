import { useProviders, useUpdateSettings } from "@/hooks/use-api";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { toast } from "sonner";

export function ProvidersPage() {
  const { data, isLoading, refetch } = useProviders();
  const update = useUpdateSettings();

  const select = async (id: string, model?: string) => {
    try {
      await update.mutateAsync({ ai_provider: id, ai_model: model });
      toast.success(`Active provider: ${id}`);
    } catch {
      toast.error("Failed to update provider");
    }
  };

  return (
    <div className="p-6 md:p-8 space-y-6">
      <div className="flex items-end justify-between gap-4">
        <div>
          <h1 className="font-display text-2xl font-semibold">AI Providers</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Ollama is the default for a free, fully local setup.
          </p>
        </div>
        <Button variant="outline" size="sm" onClick={() => void refetch()}>
          Refresh
        </Button>
      </div>

      {isLoading && (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <Skeleton key={i} className="h-40" />
          ))}
        </div>
      )}

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {data?.map((p) => (
          <article key={p.id} className="flex flex-col rounded-xl border border-border bg-card/60 p-5">
            <div className="flex items-start justify-between gap-2">
              <div>
                <h2 className="font-medium">{p.name}</h2>
                <p className="mt-1 text-xs text-muted-foreground">{p.description}</p>
              </div>
              <div className="flex flex-col items-end gap-1">
                {p.local && <Badge>Local</Badge>}
                <Badge variant={p.available ? "success" : "outline"}>
                  {p.available ? "Online" : "Offline"}
                </Badge>
              </div>
            </div>
            <div className="mt-3 text-xs text-muted-foreground">
              Models: {p.models.slice(0, 3).join(", ") || "—"}
              {p.models.length > 3 ? "…" : ""}
            </div>
            <Button
              className="mt-auto pt-4"
              size="sm"
              variant="secondary"
              onClick={() => void select(p.id, p.models[0])}
            >
              Use {p.name}
            </Button>
          </article>
        ))}
      </div>
    </div>
  );
}
