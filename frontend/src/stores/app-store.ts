import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { User } from "@/types";

interface AppState {
  user: User | null;
  onboardingDone: boolean;
  sidebarCollapsed: boolean;
  setUser: (user: User | null) => void;
  setOnboardingDone: (done: boolean) => void;
  toggleSidebar: () => void;
}

export const useAppStore = create<AppState>()(
  persist(
    (set) => ({
      user: null,
      onboardingDone: false,
      sidebarCollapsed: false,
      setUser: (user) => set({ user }),
      setOnboardingDone: (onboardingDone) => set({ onboardingDone }),
      toggleSidebar: () => set((s) => ({ sidebarCollapsed: !s.sidebarCollapsed })),
    }),
    { name: "openreview-app" },
  ),
);
