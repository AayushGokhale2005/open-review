import { useNavigate } from "react-router-dom";
import { Command } from "cmdk";
import {
  LayoutDashboard,
  GitBranch,
  GitPullRequest,
  Settings,
  Bot,
  Home,
} from "lucide-react";

const commands = [
  { label: "Go to Dashboard", to: "/app", icon: LayoutDashboard },
  { label: "Repositories", to: "/app/repositories", icon: GitBranch },
  { label: "Pull Requests", to: "/app/pull-requests", icon: GitPullRequest },
  { label: "AI Providers", to: "/app/providers", icon: Bot },
  { label: "Settings", to: "/app/settings", icon: Settings },
  { label: "Landing page", to: "/", icon: Home },
];

export function CommandPalette({
  open,
  onOpenChange,
}: {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}) {
  const navigate = useNavigate();
  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50">
      <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={() => onOpenChange(false)} />
      <div className="relative mx-auto mt-[15vh] w-full max-w-lg overflow-hidden rounded-xl border border-border bg-card shadow-2xl">
        <Command className="[&_[cmdk-group-heading]]:px-2 [&_[cmdk-group-heading]]:text-xs [&_[cmdk-group-heading]]:text-muted-foreground">
          <Command.Input
            placeholder="Type a command or search…"
            className="h-12 w-full border-b border-border bg-transparent px-4 text-sm outline-none placeholder:text-muted-foreground"
            autoFocus
          />
          <Command.List className="max-h-72 overflow-y-auto p-2">
            <Command.Empty className="py-6 text-center text-sm text-muted-foreground">
              No results found.
            </Command.Empty>
            <Command.Group heading="Navigation">
              {commands.map((c) => (
                <Command.Item
                  key={c.to}
                  value={c.label}
                  onSelect={() => {
                    navigate(c.to);
                    onOpenChange(false);
                  }}
                  className="flex cursor-pointer items-center gap-2 rounded-md px-2 py-2 text-sm aria-selected:bg-accent"
                >
                  <c.icon className="h-4 w-4 text-muted-foreground" />
                  {c.label}
                </Command.Item>
              ))}
            </Command.Group>
          </Command.List>
        </Command>
      </div>
    </div>
  );
}
