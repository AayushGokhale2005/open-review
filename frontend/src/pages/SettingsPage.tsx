import { useEffect, useState } from "react";
import { toast } from "sonner";
import { useSettings, useUpdateSettings } from "@/hooks/use-api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";

export function SettingsPage() {
  const { data, isLoading } = useSettings();
  const update = useUpdateSettings();
  const [form, setForm] = useState({
    theme: "dark",
    ai_provider: "ollama",
    ai_model: "llama3.2",
    review_strictness: "balanced",
    auto_review: false,
    ignored_files: "",
    custom_rules: "",
    repos_path: "",
    telemetry_enabled: false,
  });

  useEffect(() => {
    if (!data) return;
    setForm({
      theme: data.theme,
      ai_provider: data.ai_provider,
      ai_model: data.ai_model,
      review_strictness: data.review_strictness,
      auto_review: data.auto_review,
      ignored_files: (data.ignored_files ?? []).join("\n"),
      custom_rules: data.custom_rules ?? "",
      repos_path: data.repos_path ?? "",
      telemetry_enabled: data.telemetry_enabled,
    });
  }, [data]);

  const save = async () => {
    try {
      await update.mutateAsync({
        theme: form.theme,
        ai_provider: form.ai_provider,
        ai_model: form.ai_model,
        review_strictness: form.review_strictness,
        auto_review: form.auto_review,
        ignored_files: form.ignored_files
          .split("\n")
          .map((s) => s.trim())
          .filter(Boolean),
        custom_rules: form.custom_rules || null,
        repos_path: form.repos_path || null,
        telemetry_enabled: form.telemetry_enabled,
      });
      toast.success("Settings saved");
    } catch {
      toast.error("Failed to save settings");
    }
  };

  if (isLoading) {
    return (
      <div className="p-8 space-y-4">
        <Skeleton className="h-8 w-40" />
        <Skeleton className="h-64" />
      </div>
    );
  }

  return (
    <div className="p-6 md:p-8 max-w-2xl space-y-8">
      <div>
        <h1 className="font-display text-2xl font-semibold">Settings</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Theme, AI, review rules, accounts, and privacy.
        </p>
      </div>

      <Field label="Theme">
        <select
          className="h-10 w-full rounded-md border border-input bg-muted px-3 text-sm"
          value={form.theme}
          onChange={(e) => setForm({ ...form, theme: e.target.value })}
        >
          <option value="dark">Dark</option>
          <option value="light">Light</option>
          <option value="system">System</option>
        </select>
      </Field>

      <Field label="AI provider">
        <Input
          value={form.ai_provider}
          onChange={(e) => setForm({ ...form, ai_provider: e.target.value })}
        />
      </Field>

      <Field label="Model">
        <Input
          value={form.ai_model}
          onChange={(e) => setForm({ ...form, ai_model: e.target.value })}
        />
      </Field>

      <Field label="Review strictness">
        <select
          className="h-10 w-full rounded-md border border-input bg-muted px-3 text-sm"
          value={form.review_strictness}
          onChange={(e) => setForm({ ...form, review_strictness: e.target.value })}
        >
          <option value="lenient">Lenient</option>
          <option value="balanced">Balanced</option>
          <option value="strict">Strict</option>
        </select>
      </Field>

      <label className="flex items-center gap-3 text-sm">
        <input
          type="checkbox"
          checked={form.auto_review}
          onChange={(e) => setForm({ ...form, auto_review: e.target.checked })}
        />
        Auto-review new pull requests
      </label>

      <Field label="Ignored files (one pattern per line)">
        <textarea
          className="min-h-24 w-full rounded-md border border-input bg-muted px-3 py-2 text-sm font-mono"
          value={form.ignored_files}
          onChange={(e) => setForm({ ...form, ignored_files: e.target.value })}
          placeholder={"node_modules/**\n*.lock\ndist/**"}
        />
      </Field>

      <Field label="Custom review rules">
        <textarea
          className="min-h-24 w-full rounded-md border border-input bg-muted px-3 py-2 text-sm"
          value={form.custom_rules}
          onChange={(e) => setForm({ ...form, custom_rules: e.target.value })}
          placeholder="Prefer early returns. Flag TODOs in production paths."
        />
      </Field>

      <Field label="Repository location">
        <Input
          value={form.repos_path}
          onChange={(e) => setForm({ ...form, repos_path: e.target.value })}
          placeholder="~/AIReviewer/repos"
        />
      </Field>

      <label className="flex items-center gap-3 text-sm">
        <input
          type="checkbox"
          checked={form.telemetry_enabled}
          onChange={(e) => setForm({ ...form, telemetry_enabled: e.target.checked })}
        />
        Enable telemetry (default OFF)
      </label>

      <div className="rounded-xl border border-border bg-card/50 p-4 text-sm">
        <h2 className="font-medium">Connected accounts</h2>
        <p className="mt-1 text-muted-foreground">
          Configure GitHub / GitLab OAuth client IDs via environment variables, then connect from
          Profile. Tokens are encrypted locally.
        </p>
      </div>

      <Button onClick={() => void save()} disabled={update.isPending}>
        Save settings
      </Button>
    </div>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <label className="block space-y-1.5">
      <span className="text-xs text-muted-foreground">{label}</span>
      {children}
    </label>
  );
}
