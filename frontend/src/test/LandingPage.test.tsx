import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { LandingPage } from "@/pages/LandingPage";
import { cn } from "@/lib/utils";

describe("cn", () => {
  it("merges class names", () => {
    expect(cn("px-2", "px-4")).toBe("px-4");
  });
});

describe("LandingPage", () => {
  it("renders brand and privacy message", () => {
    const client = new QueryClient();
    render(
      <QueryClientProvider client={client}>
        <MemoryRouter>
          <LandingPage />
        </MemoryRouter>
      </QueryClientProvider>,
    );
    expect(screen.getAllByText("Open Review").length).toBeGreaterThan(0);
    expect(screen.getAllByText(/Your code stays on your machine/i).length).toBeGreaterThan(0);
    expect(screen.getAllByRole("link", { name: /Get Started/i }).length).toBeGreaterThan(0);
  });
});
