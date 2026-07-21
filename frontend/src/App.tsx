import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "sonner";
import { AppShell } from "@/components/layout/AppShell";
import { LandingPage } from "@/pages/LandingPage";
import { OnboardingPage } from "@/pages/OnboardingPage";
import { DashboardPage } from "@/pages/DashboardPage";
import { RepositoriesPage } from "@/pages/RepositoriesPage";
import { PullRequestsPage } from "@/pages/PullRequestsPage";
import { PullRequestDetailPage } from "@/pages/PullRequestDetailPage";
import { ReviewsPage } from "@/pages/ReviewsPage";
import { ProvidersPage } from "@/pages/ProvidersPage";
import { SettingsPage } from "@/pages/SettingsPage";
import { ProfilePage } from "@/pages/ProfilePage";
import { useAppStore } from "@/stores/app-store";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30_000,
      refetchOnWindowFocus: false,
    },
  },
});

function OnboardingGate({ children }: { children: React.ReactNode }) {
  const onboardingDone = useAppStore((s) => s.onboardingDone);
  if (!onboardingDone) return <Navigate to="/onboarding" replace />;
  return children;
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/onboarding" element={<OnboardingPage />} />
          <Route
            path="/app"
            element={
              <OnboardingGate>
                <AppShell />
              </OnboardingGate>
            }
          >
            <Route index element={<DashboardPage />} />
            <Route path="repositories" element={<RepositoriesPage />} />
            <Route path="pull-requests" element={<PullRequestsPage />} />
            <Route path="pull-requests/:id" element={<PullRequestDetailPage />} />
            <Route path="reviews" element={<ReviewsPage />} />
            <Route path="providers" element={<ProvidersPage />} />
            <Route path="settings" element={<SettingsPage />} />
            <Route path="profile" element={<ProfilePage />} />
          </Route>
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
      <Toaster theme="dark" position="bottom-right" richColors />
    </QueryClientProvider>
  );
}
