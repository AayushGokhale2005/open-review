import { test, expect } from "@playwright/test";

test("landing page shows brand and CTA", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByText("Open Review").first()).toBeVisible();
  await expect(page.getByText(/Your code stays on your machine/i).first()).toBeVisible();
  await expect(page.getByRole("link", { name: /Get Started/i }).first()).toBeVisible();
});

test("onboarding wizard is reachable", async ({ page }) => {
  await page.goto("/onboarding");
  await expect(page.getByText(/Welcome to Open Review/i)).toBeVisible();
});
