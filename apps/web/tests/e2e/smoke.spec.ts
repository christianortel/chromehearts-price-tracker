import { expect, test } from "@playwright/test";

test("home, browse, and submit routes render core text", async ({ page }) => {
  await page.addInitScript(() => {
    Object.defineProperty(navigator, "clipboard", {
      configurable: true,
      value: {
        writeText: async () => undefined,
      },
    });
  });

  await page.goto("/");
  await expect(page.getByText("Fragmented prices, made legible.")).toBeVisible();

  await page.goto("/browse");
  await expect(page.getByText("Browse collector-facing product intelligence")).toBeVisible();
  await expect(page.getByText("Source classes")).toBeVisible();
  await expect(page.getByRole("option", { name: "Highest premium" })).toBeVisible();
  await expect(page.getByRole("button", { name: "Copy share link" })).toBeVisible();
  await expect(page.getByText("Quick views")).toBeVisible();
  await expect(page.getByText(/Showing .* of .* matching products/)).toBeVisible();
  await expect(page.getByRole("button", { name: "Next" })).toBeVisible();
  await page.getByRole("button", { name: /^rings \(/ }).click();
  await expect.poll(() => page.url()).toContain("categories=ring");
  await page.getByRole("button", { name: "High premium" }).click();
  await expect.poll(() => page.url()).toContain("sort=premium_desc");
  await page.getByRole("button", { name: "Copy share link" }).click();
  await expect(page.getByText("Link copied for sharing.")).toBeVisible();

  await page.goto("/submit");
  await expect(page.getByText("Submit a retail sighting")).toBeVisible();
  await expect(page.getByText("Upload receipt image or PDF")).toBeVisible();

  await page.goto("/admin/login");
  await expect(page.getByText("Authenticate before reviewing source data")).toBeVisible();
});
