import { test, expect } from "@playwright/test";
for (const width of [390, 768, 1440]) {
  test(`layout and voice fallback at ${width}px`, async ({ page }) => {
    await page.setViewportSize({ width, height: width === 390 ? 844 : 1000 });
    const errors: string[] = [];
    page.on("pageerror", (e) => errors.push(e.message));
    let sessions = 0;
    page.on("request", (r) => {
      if (r.url().includes("/api/voice/session")) sessions++;
    });
    await page.goto("/");
    await expect(page.getByRole("heading", { level: 1 })).toBeVisible();
    const start = page.getByRole("button", {
      name: "Start Voice Conversation",
      exact: true,
    });
    await expect(start).toBeVisible();
    if (width === 390) {
      const box = await start.boundingBox();
      expect(box!.y + box!.height).toBeLessThan(844);
    }
    expect(
      await page.evaluate(
        () => document.documentElement.scrollWidth <= window.innerWidth,
      ),
    ).toBe(true);
    await page.screenshot({
      path: `/private/tmp/bds-${width}.png`,
      fullPage: true,
    });
    await start.click();
    await expect(
      page.getByText(
        "Voice demo unavailable — connect Retell credentials to enable calls.",
        { exact: false },
      ),
    ).toBeVisible();
    expect(sessions).toBe(0);
    await page.locator("#location").scrollIntoViewIfNeeded();
    await page
      .getByRole("button", { name: "Ask Best Driving School", exact: true })
      .click();
    const dialog = page.getByRole("dialog");
    await expect(dialog).toBeVisible();
    await expect(
      dialog.getByText("Voice demo unavailable", { exact: false }),
    ).toBeVisible();
    await page.keyboard.press("Escape");
    await expect(dialog).not.toBeVisible();
    expect(errors).toEqual([]);
  });
}
test("mobile navigation and keyboard dialog focus", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/");
  await page.getByRole("button", { name: "Open menu", exact: true }).click();
  await page
    .getByRole("navigation", { name: "Mobile navigation" })
    .getByRole("link", { name: "Pricing" })
    .click();
  await expect(
    page.getByRole("navigation", { name: "Mobile navigation" }),
  ).not.toBeVisible();
  await page.getByRole("button", { name: "Talk to AI", exact: true }).click();
  await expect(page.getByRole("dialog")).toBeVisible();
  for (let i = 0; i < 12; i++) {
    await page.keyboard.press("Tab");
    expect(
      await page.evaluate(() =>
        Boolean(document.activeElement?.closest("dialog")),
      ),
    ).toBe(true);
  }
  await page.keyboard.press("Escape");
  await expect(
    page.getByRole("button", { name: "Talk to AI", exact: true }),
  ).toBeFocused();
});
test("session proxy fails closed without a valid origin", async ({
  request,
}) => {
  const response = await request.post("/api/voice/session");
  expect(response.status()).toBe(403);
  expect(response.headers()["cache-control"]).toBe("no-store");
});

test("WCAG AA scan on homepage and voice dialog", async ({ page }) => {
  const { default: AxeBuilder } = await import("@axe-core/playwright");
  await page.goto("/");
  const home = await new AxeBuilder({ page })
    .withTags(["wcag2a", "wcag2aa", "wcag21aa"])
    .analyze();
  expect(home.violations).toEqual([]);
  await page.getByRole("button", { name: "Talk to AI", exact: true }).click();
  const dialog = await new AxeBuilder({ page })
    .withTags(["wcag2a", "wcag2aa", "wcag21aa"])
    .analyze();
  expect(dialog.violations).toEqual([]);
});
