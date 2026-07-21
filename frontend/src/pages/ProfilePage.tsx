import { useAppStore } from "@/stores/app-store";
import { useDemoLogin, useMe } from "@/hooks/use-api";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { toast } from "sonner";

export function ProfilePage() {
  const { user, setUser } = useAppStore();
  const { data: me } = useMe();
  const demoLogin = useDemoLogin();
  const profile = me ?? user;

  const connectDemo = async () => {
    try {
      const u = await demoLogin.mutateAsync();
      setUser(u);
      toast.success("Signed in locally");
    } catch {
      toast.error("Backend unavailable");
    }
  };

  return (
    <div className="p-6 md:p-8 max-w-xl space-y-6">
      <div>
        <h1 className="font-display text-2xl font-semibold">Profile</h1>
        <p className="mt-1 text-sm text-muted-foreground">Local identity and connected accounts.</p>
      </div>

      <div className="rounded-xl border border-border bg-card/60 p-6">
        <div className="flex items-center gap-4">
          <div className="flex h-14 w-14 items-center justify-center rounded-full bg-primary/15 font-display text-lg font-semibold text-primary">
            {(profile?.display_name ?? "OR").slice(0, 2).toUpperCase()}
          </div>
          <div>
            <div className="font-medium">{profile?.display_name ?? "Not signed in"}</div>
            <div className="text-sm text-muted-foreground">{profile?.email ?? "dev@localhost"}</div>
          </div>
        </div>

        <div className="mt-6 space-y-2">
          <h2 className="text-sm font-medium">OAuth accounts</h2>
          {(profile?.oauth_accounts?.length ?? 0) === 0 && (
            <p className="text-xs text-muted-foreground">No OAuth accounts connected yet.</p>
          )}
          {profile?.oauth_accounts?.map((a) => (
            <div key={a.id} className="flex items-center justify-between rounded-md border border-border px-3 py-2 text-sm">
              <span>
                {a.provider} · @{a.username}
              </span>
              <Badge variant="success">Connected</Badge>
            </div>
          ))}
        </div>

        <div className="mt-6 flex flex-wrap gap-2">
          <Button size="sm" onClick={() => void connectDemo()}>
            Demo sign-in
          </Button>
          <Button size="sm" variant="secondary">
            Connect GitHub
          </Button>
          <Button size="sm" variant="outline">
            Connect GitLab
          </Button>
          <Button
            size="sm"
            variant="ghost"
            onClick={() => {
              setUser(null);
              toast.message("Signed out locally");
            }}
          >
            Logout
          </Button>
        </div>
      </div>
    </div>
  );
}
