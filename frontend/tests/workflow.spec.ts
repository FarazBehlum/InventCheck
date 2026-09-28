import { test, expect } from "@playwright/test";

test.beforeEach(async ({ request }) => {
  const items = await (
    await request.get("http://127.0.0.1:8000/api/watchlist")
  ).json();
  for (const item of items)
    await request.delete(`http://127.0.0.1:8000/api/watchlist/${item.id}`);
});

test("demo search, filters, history, watchlist editing and deduplicated alerts", async ({
  page,
}) => {
  const errors: string[] = [];
  page.on("pageerror", (error) => errors.push(error.message));
  await page.goto("/");
  await expect(page.getByText("Demo workspace")).toBeVisible();
  await page
    .getByRole("textbox", { name: "What are you looking for?" })
    .fill("FW-D20");
  await page
    .getByRole("button", { name: "Compare prices", exact: true })
    .click();
  await expect(page.getByTestId("offer-row")).toHaveCount(10);
  await expect(
    page.getByRole("table").getByText("Lowest price", { exact: true }),
  ).toBeVisible();
  await page.getByLabel("In stock only").check();
  await expect(page.getByTestId("offer-row")).toHaveCount(4);
  await page.getByRole("button", { name: "Reset filters" }).click();
  await page.getByLabel("Max. price", { exact: true }).fill("80");
  await expect(page.getByTestId("offer-row")).toHaveCount(1);
  await page.getByRole("button", { name: "Reset filters" }).click();
  await page.getByLabel("Sort by").selectOption("distance");
  const distances = await page
    .getByTestId("offer-row")
    .locator("td:nth-child(2)")
    .allTextContents();
  expect(distances.map(parseFloat)).toEqual(
    distances.map(parseFloat).sort((a, b) => a - b),
  );
  await page.getByRole("button", { name: "Watch price", exact: true }).click();
  await page.getByRole("spinbutton", { name: "Target price ($)" }).fill("85");
  await page
    .getByRole("button", { name: "Save to watchlist", exact: true })
    .click();
  await expect(page.getByRole("status")).toContainText("Product saved");
  await page
    .getByRole("navigation")
    .getByRole("link", { name: "Watchlist", exact: true })
    .click();
  await expect(page.getByText("$85.00", { exact: true })).toBeVisible();
  await page
    .getByRole("button", { name: "Check watchlist", exact: true })
    .click();
  await expect(page.locator(".alert-row")).toHaveCount(3);
  await page
    .getByRole("button", { name: "Check watchlist", exact: true })
    .click();
  await expect(page.getByRole("status")).toContainText("0 new alerts");
  await expect(page.locator(".alert-row")).toHaveCount(3);
  await page.getByRole("button", { name: "Mark read" }).first().click();
  await expect(page.getByText("2 unread", { exact: true })).toBeVisible();
  await page.getByRole("button", { name: "Edit settings" }).click();
  await page.getByRole("spinbutton", { name: "Target price ($)" }).fill("70");
  await page.getByRole("button", { name: "Save changes", exact: true }).click();
  await expect(page.getByText("$70.00", { exact: true })).toBeVisible();
  await page.reload();
  await expect(page.getByText("$70.00", { exact: true })).toBeVisible();
  await page
    .getByRole("link", { name: "20V cordless drill kit", exact: true })
    .click();
  await expect(
    page.getByRole("heading", { name: "The price over time" }),
  ).toBeVisible();
  await expect(
    page.getByRole("img", { name: /Daily lowest demo price/ }),
  ).toBeVisible();
  await page.getByText("View chart data", { exact: true }).click();
  await expect(
    page.getByRole("columnheader", { name: "Lowest demo price" }),
  ).toBeVisible();
  await page
    .getByRole("navigation")
    .getByRole("link", { name: "Watchlist", exact: true })
    .click();
  await page
    .getByRole("button", { name: "Remove 20V cordless drill kit" })
    .click();
  await expect(
    page.getByRole("heading", { name: "A good price is worth remembering." }),
  ).toBeVisible();
  expect(errors).toEqual([]);
});

test("mobile layout, examples, empty states, and location validation", async ({
  page,
}) => {
  await page.setViewportSize({ width: 375, height: 812 });
  await page.goto("/");
  await expect(page.getByText("Demo workspace")).toBeVisible();
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= window.innerWidth,
    ),
  ).toBeTruthy();
  await page.screenshot({
    path: "test-results/mobile-home.png",
    fullPage: true,
  });
  await page.getByRole("button", { name: /Cordless drill kit/ }).click();
  await expect(page.getByTestId("offer-row")).toHaveCount(10);
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= window.innerWidth,
    ),
  ).toBeTruthy();
  await page
    .getByRole("textbox", { name: "What are you looking for?" })
    .fill("not a real product");
  await page
    .getByRole("button", { name: "Compare prices", exact: true })
    .click();
  await expect(
    page.getByRole("heading", { name: "No offers to compare." }),
  ).toBeVisible();
  await page
    .getByRole("textbox", { name: "ZIP code", exact: true })
    .fill("00000");
  await page
    .getByRole("button", { name: "Compare prices", exact: true })
    .click();
  await expect(page.getByRole("alert")).toContainText(
    "ZIP code is not supported",
  );
});

test("desktop homepage screenshot", async ({ page }) => {
  await page.setViewportSize({ width: 1440, height: 1000 });
  await page.goto("/");
  await expect(page.getByText("Demo workspace")).toBeVisible();
  await page.screenshot({
    path: "test-results/desktop-home.png",
    fullPage: true,
  });
});
