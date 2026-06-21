import { expect, test } from "@playwright/test";

test.describe("Flujo de suscripción", () => {
  test("crea una suscripción, confirma el pago y permite cancelarla", async ({
    page,
  }) => {
    test.setTimeout(30_000);

    await page.goto("/");

    await expect(
      page.getByRole("heading", { name: "Portal de Suscripciones" }),
    ).toBeVisible();

    await page.getByLabel("Nombre completo").fill("Erick Prueba");
    await page.getByLabel("Correo electrónico").fill("erick.prueba@example.com");
    await page.getByLabel("Método de pago").selectOption("tarjeta");

    await page.getByRole("button", { name: "Procesar pago y suscribirme" }).click();

    await expect(
      page.getByRole("heading", { name: "Resumen de tu suscripción" }),
    ).toBeVisible();

    const dashboard = page.locator(".card").filter({
      has: page.getByRole("heading", { name: "Resumen de tu suscripción" }),
    });

    await expect(dashboard.getByText("Erick Prueba", { exact: true })).toBeVisible();
    await expect(
      dashboard.getByText("erick.prueba@example.com", { exact: true }),
    ).toBeVisible();
    await expect(
      dashboard.locator(".subscription-details").getByText("Tarjeta de crédito", {
        exact: true,
      }),
    ).toBeVisible();
    await expect(dashboard.getByText("Activa", { exact: true })).toBeVisible();

    await expect(
      dashboard.getByText(/Pago inicial confirmado|Pago inicial pendiente/),
    ).toBeVisible();

    await expect(dashboard.getByText("Pago inicial confirmado", { exact: true })).toBeVisible({
      timeout: 12_000,
    });

    await page.getByRole("button", { name: "Cancelar suscripción" }).click();

    await expect(dashboard.getByText("Cancelada", { exact: true })).toBeVisible();
    await expect(dashboard.getByText("Pago inicial confirmado", { exact: true })).toBeVisible();
  });
});
