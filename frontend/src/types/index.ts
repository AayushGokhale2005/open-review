export interface User {
  id: string;
  display_name: string;
  email: string | null;
  avatar_url: string | null;
  onboarding_completed: boolean;
  oauth_accounts: OAuthAccount[];
}

export interface OAuthAccount {
  id: string;
  provider: string;
  username: string;
  provider_user_id: string;
}

export interface Repository {
  id: string;
  provider: string;
  name: string;
  full_name: string;
  description: string | null;
  language: string | null;
  stars: number;
  default_branch: string;
  clone_url: string | null;
  local_path: string | null;
  html_url: string | null;
  open_pr_count: number;
  health_score: number;
  last_reviewed_at: string | null;
}

export interface PullRequest {
  id: string;
  repository_id: string;
  remote_id: string;
  number: number;
  title: string;
  body: string | null;
  state: string;
  author: string;
  author_avatar: string | null;
  source_branch: string;
  target_branch: string;
  additions: number;
  deletions: number;
  changed_files: number;
  html_url: string | null;
  draft: boolean;
  labels: string[] | null;
  created_at: string;
  updated_at: string;
}

export interface FileDiff {
  path: string;
  status: string;
  additions: number;
  deletions: number;
  patch: string | null;
  language: string | null;
}

export interface PullRequestDetail extends PullRequest {
  files: FileDiff[];
  repository: Repository | null;
}

export interface ReviewComment {
  id: string;
  agent: string;
  file_path: string | null;
  line_start: number | null;
  line_end: number | null;
  severity: string;
  title: string;
  body: string;
  suggestion: string | null;
}

export interface Review {
  id: string;
  pull_request_id: string;
  status: string;
  provider: string;
  model: string;
  summary: string | null;
  verdict: string | null;
  score: number | null;
  agent_results: Record<string, unknown> | null;
  error_message: string | null;
  started_at: string | null;
  completed_at: string | null;
  created_at: string;
  comments: ReviewComment[];
}

export interface ProviderInfo {
  id: string;
  name: string;
  description: string;
  local: boolean;
  requires_api_key: boolean;
  base_url: string | null;
  models: string[];
  available: boolean;
  configured: boolean;
}

export interface Settings {
  theme: string;
  ai_provider: string;
  ai_model: string;
  review_strictness: string;
  auto_review: boolean;
  ignored_files: string[] | null;
  custom_rules: string | null;
  repos_path: string | null;
  telemetry_enabled: boolean;
  has_openai_key: boolean;
  has_anthropic_key: boolean;
  has_openrouter_key: boolean;
}

export interface DashboardStats {
  repositories: number;
  open_pull_requests: number;
  reviews_completed: number;
  avg_health_score: number;
  comments_this_week: number;
}

export interface ActivityItem {
  id: string;
  type: string;
  title: string;
  description: string;
  timestamp: string;
  meta?: Record<string, unknown> | null;
}

export interface Dashboard {
  stats: DashboardStats;
  recent_reviews: Review[];
  latest_pull_requests: PullRequest[];
  activity: ActivityItem[];
  repositories: Repository[];
}
