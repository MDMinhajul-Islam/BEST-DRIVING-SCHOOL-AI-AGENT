import { test, expect } from "@playwright/test";
test.skip(
  !process.env.TEST_LIVE_PATH,
  "Run against a local test server with NEXT_PUBLIC_VOICE_DEMO_MODE=false; HTTP responses are mocked.",
);
const buttonName = "Start Voice Conversation";
test("permission denied without requesting a token", async ({ page }) => {
  let requests = 0;
  page.on("request", (r) => {
    if (r.url().includes("/api/voice/session")) requests++;
  });
  await page.addInitScript(() => {
    navigator.mediaDevices.getUserMedia = async () => {
      throw new DOMException("Denied", "NotAllowedError");
    };
  });
  await page.goto("/");
  await page.getByRole("button", { name: buttonName, exact: true }).click();
  await expect(
    page.getByText("We couldn’t access your microphone.", { exact: false }),
  ).toBeVisible();
  expect(requests).toBe(0);
});
test("unsupported microphone browser", async ({ page }) => {
  await page.addInitScript(() => {
    Object.defineProperty(navigator, "mediaDevices", { value: undefined });
  });
  await page.goto("/");
  await page.getByRole("button", { name: buttonName, exact: true }).click();
  await expect(
    page.getByText("Voice calling needs a browser", { exact: false }),
  ).toBeVisible();
});
for (const mode of ["network", "service"])
  test(`${mode} unavailable safely ends microphone tracks`, async ({
    page,
  }) => {
    await page.addInitScript(() => {
      const track = {
        stop() {
          (window as unknown as { stopped: boolean }).stopped = true;
        },
      };
      navigator.mediaDevices.getUserMedia = async () =>
        ({ getTracks: () => [track] }) as unknown as MediaStream;
    });
    await page.route("**/api/voice/session", (r) =>
      mode === "network"
        ? r.abort()
        : r.fulfill({ status: 503, json: { error: "private server detail" } }),
    );
    await page.goto("/");
    await page.getByRole("button", { name: buttonName, exact: true }).click();
    await expect(
      page.getByText(
        mode === "network"
          ? "We couldn’t reach the voice service."
          : "Our voice assistant is temporarily unavailable.",
        { exact: false },
      ),
    ).toBeVisible();
    expect(
      await page.evaluate(
        () => (window as unknown as { stopped: boolean }).stopped,
      ),
    ).toBe(true);
    await expect(page.getByText("private server detail")).toHaveCount(0);
  });
test("cancelled permission request cleans late tracks and never creates a session", async ({
  page,
}) => {
  await page.addInitScript(() => {
    navigator.mediaDevices.getUserMedia = () =>
      new Promise((resolve) => {
        (window as unknown as { release: () => void }).release = () =>
          resolve({
            getTracks: () => [
              {
                stop() {
                  (window as unknown as { stopped: boolean }).stopped = true;
                },
              },
            ],
          } as unknown as MediaStream);
      });
  });
  let requests = 0;
  page.on("request", (r) => {
    if (r.url().includes("/api/voice/session")) requests++;
  });
  await page.goto("/");
  await page.getByRole("button", { name: buttonName, exact: true }).click();
  await expect(page.getByText("Allow microphone access…")).toBeVisible();
  await page.getByRole("button", { name: "Cancel", exact: true }).click();
  await page.evaluate(() =>
    (window as unknown as { release: () => void }).release(),
  );
  await expect(
    page.getByText("Conversation ended.", { exact: false }),
  ).toBeVisible();
  expect(
    await page.evaluate(
      () => (window as unknown as { stopped: boolean }).stopped,
    ),
  ).toBe(true);
  expect(requests).toBe(0);
});
test("connection timeout is recoverable", async ({ page }) => {
  await page.clock.install();
  await page.addInitScript(() => {
    navigator.mediaDevices.getUserMedia = () => new Promise(() => {});
  });
  await page.goto("/");
  await page.getByRole("button", { name: buttonName, exact: true }).click();
  await page.clock.fastForward(31000);
  await expect(
    page.getByText("Connecting took too long.", { exact: false }),
  ).toBeVisible();
});
