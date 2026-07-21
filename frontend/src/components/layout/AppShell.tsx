import { NavLink, Outlet, useNavigate } from "react-router-dom";
import {
  LayoutDashboard,
  GitBranch,
  GitPullRequest,
  MessageSquareCode,
  Bot,
  Settings,
  User,
  Search,
  PanelLeftClose,
  PanelLeft,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useAppStore } from "@/stores/app-store";
import { Button } from "@/components/ui/button";
import { CommandPalette } from "@/components/layout/CommandPalette";
import { useEffect, useState } from "react";

const nav = [
  { to: "/app", label: "Dashboard", icon: LayoutDashboard, end: true },
  { to: "/app/repositories", label: "Repositories", icon: GitBranch },
  { to: "/app/pull-requests", label: "Pull Requests", icon: GitPullRequest },
  { to: "/app/reviews", label: "Reviews", icon: MessageSquareCode },
  { to: "/app/providers", label: "AI Providers", icon: Bot },
  { to: "/app/settings", label: "Settings", icon: Settings },
  { to: "/app/profile", label: "Profile", icon: User },
];

export function AppShell() {
  const { sidebarCollapsed, toggleSidebar } = useAppStore();
  const [cmdOpen, setCmdOpen] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        setCmdOpen((v) => !v);
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  return (
    <div className="flex min-h-screen">
      <aside
        className={cn(
          "sticky top-0 flex h-screen flex-col border-r border-sidebar-border bg-sidebar transition-all",
          sidebarCollapsed ? "w-[68px]" : "w-60",
        )}
      >
        <div className="flex h-14 items-center gap-2 border-b border-sidebar-border px-3">
          <button
            type="button"
            onClick={() => navigate("/")}
            className="flex items-center gap-2 overflow-hidden"
          >
            <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-md bg-primary/15 text-primary font-display font-bold text-sm">
              OR
            </div>
            {!sidebarCollapsed && (
              <span className="font-display text-sm font-semibold tracking-tight truncate">
                Open Review
              </span>
            )}
          </button>
        </div>

        <nav className="flex-1 space-y-0.5 p-2">
          {nav.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              className={({ isActive }) =>
                cn(
                  "flex items-center gap-3 rounded-md px-2.5 py-2 text-sm text-muted-foreground transition-colors hover:bg-accent hover:text-foreground",
                  isActive && "bg-accent text-foreground",
                  sidebarCollapsed && "justify-center px-0",
                )
              }
            >
              <item.icon className="h-4 w-4 shrink-0" />
              {!sidebarCollapsed && <span>{item.label}</span>}
            </NavLink>
          ))}
        </nav>

        <div className="border-t border-sidebar-border p-2 space-y-1">
          <Button
            variant="ghost"
            size="sm"
            className={cn("w-full justify-start gap-2 text-muted-foreground", sidebarCollapsed && "justify-center px-0")}
            onClick={() => setCmdOpen(true)}
          >
            <Search className="h-4 w-4" />
            {!sidebarCollapsed && (
              <>
                <span className="flex-1 text-left">Search</span>
                <kbd className="rounded border border-border px-1.5 text-[10px]">⌘K</kbd>
              </>
            )}
          </Button>
          <Button
            variant="ghost"
            size="icon"
            className="w-full text-muted-foreground"
            onClick={toggleSidebar}
          >
            {sidebarCollapsed ? <PanelLeft className="h-4 w-4" /> : <PanelLeftClose className="h-4 w-4" />}
          </Button>
        </div>
      </aside>

      <main className="flex-1 min-w-0">
        <Outlet />
      </main>

      <CommandPalette open={cmdOpen} onOpenChange={setCmdOpen} />
    </div>
  );
}
