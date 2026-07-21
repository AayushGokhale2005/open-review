import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import {
  GitBranch,
  GitPullRequest,
  MessageSquareCode,
  Activity,
  Star,
} from "lucide-react";
import {
  Area,
  AreaChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { useDashboard } from "@/hooks/use-api";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { formatNumber, relativeTime } from "@/lib/utils";

const chartData = [
  { day: "Mon", reviews: 2 },
  { day: "Tue", reviews: 4 },
  { day: "Wed", reviews: 3 },
  { day: "Thu", reviews: 6 },
  { day: "Fri", reviews: 5 },
  { day: "Sat", reviews: 1 },
  { day: "Sun", reviews: 3 },
];

export function DashboardPage() {
  const { data, isLoading, isError } = useDashboard();

  return (
    <div className="p-6 md:p-8 space-y-8">
      <div>
        <h1 className="font-display text-2xl font-semibold tracking-tight">Dashboard</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Local workspace overview — repositories, reviews, and activity.
        </p>
      </div>

      {isLoading && (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} className="h-24" />
          ))}
        </div>
      )}

      {isError && (
        <div className="rounded-xl border border-warning/30 bg-warning/10 p-4 text-sm">
          Backend unreachable. Start the API on port 8741 to load live data. Demo UI remains available.
        </div>
      )}

      {data && (
        <>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {[
              { label: "Repositories", value: data.stats.repositories, icon: GitBranch },
              { label: "Open PRs", value: data.stats.open_pull_requests, icon: GitPullRequest },
              { label: "Reviews", value: data.stats.reviews_completed, icon: MessageSquareCode },
              { label: "Avg health", value: `${data.stats.avg_health_score}%`, icon: Activity },
            ].map((stat, i) => (
              <motion.div
                key={stat.label}
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.05 }}
                className="rounded-xl border border-border bg-card/60 p-4"
              >
                <div className="flex items-center justify-between">
                  <span className="text-xs text-muted-foreground">{stat.label}</span>
                  <stat.icon className="h-4 w-4 text-primary" />
                </div>
                <div className="mt-2 font-display text-2xl font-semibold">{stat.value}</div>
              </motion.div>
            ))}
          </div>

          <div className="grid gap-6 lg:grid-cols-3">
            <div className="lg:col-span-2 rounded-xl border border-border bg-card/60 p-5">
              <h2 className="font-medium">Review activity</h2>
              <div className="mt-4 h-48">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={chartData}>
                    <defs>
                      <linearGradient id="rev" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stopColor="#2dd4bf" stopOpacity={0.35} />
                        <stop offset="100%" stopColor="#2dd4bf" stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <XAxis dataKey="day" stroke="#8b929e" fontSize={11} tickLine={false} axisLine={false} />
                    <YAxis stroke="#8b929e" fontSize={11} tickLine={false} axisLine={false} width={24} />
                    <Tooltip
                      contentStyle={{
                        background: "#0e1015",
                        border: "1px solid #1c2028",
                        borderRadius: 8,
                        fontSize: 12,
                      }}
                    />
                    <Area type="monotone" dataKey="reviews" stroke="#2dd4bf" fill="url(#rev)" strokeWidth={2} />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>

            <div className="rounded-xl border border-border bg-card/60 p-5">
              <h2 className="font-medium">Activity feed</h2>
              <ul className="mt-4 space-y-3">
                {data.activity.map((a) => (
                  <li key={a.id} className="text-sm">
                    <div className="font-medium">{a.title}</div>
                    <div className="text-xs text-muted-foreground">{a.description}</div>
                    <div className="mt-0.5 text-[10px] text-muted-foreground/70">
                      {relativeTime(a.timestamp)}
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          <div className="grid gap-6 lg:grid-cols-2">
            <div className="rounded-xl border border-border bg-card/60 p-5">
              <div className="flex items-center justify-between">
                <h2 className="font-medium">Connected repositories</h2>
                <Link to="/app/repositories" className="text-xs text-primary hover:underline">
                  View all
                </Link>
              </div>
              <ul className="mt-4 space-y-3">
                {data.repositories.slice(0, 4).map((r) => (
                  <li key={r.id} className="flex items-center justify-between gap-3 text-sm">
                    <div className="min-w-0">
                      <div className="truncate font-medium">{r.full_name}</div>
                      <div className="text-xs text-muted-foreground">
                        {r.language ?? "—"} · health {r.health_score}%
                      </div>
                    </div>
                    <span className="inline-flex items-center gap-1 text-xs text-muted-foreground">
                      <Star className="h-3 w-3" />
                      {formatNumber(r.stars)}
                    </span>
                  </li>
                ))}
              </ul>
            </div>

            <div className="rounded-xl border border-border bg-card/60 p-5">
              <div className="flex items-center justify-between">
                <h2 className="font-medium">Latest pull requests</h2>
                <Link to="/app/pull-requests" className="text-xs text-primary hover:underline">
                  View all
                </Link>
              </div>
              <ul className="mt-4 space-y-3">
                {data.latest_pull_requests.map((pr) => (
                  <li key={pr.id}>
                    <Link
                      to={`/app/pull-requests/${pr.id}`}
                      className="block rounded-lg p-2 -mx-2 hover:bg-accent transition"
                    >
                      <div className="flex items-start justify-between gap-2">
                        <span className="text-sm font-medium">
                          #{pr.number} {pr.title}
                        </span>
                        <Badge variant="outline">{pr.state}</Badge>
                      </div>
                      <div className="mt-1 text-xs text-muted-foreground">
                        {pr.author} · +{pr.additions} −{pr.deletions}
                      </div>
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          <div className="rounded-xl border border-border bg-card/60 p-5">
            <h2 className="font-medium">Recent reviews</h2>
            <ul className="mt-4 divide-y divide-border">
              {data.recent_reviews.length === 0 && (
                <li className="py-6 text-center text-sm text-muted-foreground">No reviews yet.</li>
              )}
              {data.recent_reviews.map((r) => (
                <li key={r.id} className="flex items-center justify-between py-3 text-sm">
                  <div>
                    <div className="font-medium">{r.summary?.slice(0, 80) ?? "Review"}…</div>
                    <div className="text-xs text-muted-foreground">
                      {r.provider}/{r.model} · {r.verdict}
                    </div>
                  </div>
                  <Badge variant={r.score && r.score >= 80 ? "success" : "warning"}>
                    {r.score ?? "—"}
                  </Badge>
                </li>
              ))}
            </ul>
          </div>
        </>
      )}
    </div>
  );
}
