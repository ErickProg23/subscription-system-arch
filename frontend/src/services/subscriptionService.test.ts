import { beforeEach, describe, expect, it, vi } from "vitest";
import { AppError } from "./apiClient";
import { subscriptionService } from "./subscriptionService";

describe("subscriptionService", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("crea una suscripción usando el endpoint correcto", async () => {
    const fetchMock = vi.spyOn(window, "fetch").mockResolvedValue({
      ok: true,
      status: 201,
      json: async () => ({
        message: "ok",
        data: {
          id: "sub-1",
          user_name: "Erick",
          email: "erick@example.com",
          payment_method: { type: "tarjeta" },
          status: "Activa",
          created_at: "2026-01-01T00:00:00",
        },
      }),
    } as Response);

    const response = await subscriptionService.createSubscription({
      user_name: "Erick",
      email: "erick@example.com",
      payment_method: { type: "tarjeta" },
    });

    expect(fetchMock).toHaveBeenCalledWith(
      "/api/subscribirse",
      expect.objectContaining({
        method: "POST",
      }),
    );
    expect(response.data.id).toBe("sub-1");
  });

  it("lanza AppError de validación para respuestas 400", async () => {
    vi.spyOn(window, "fetch").mockResolvedValue({
      ok: false,
      status: 400,
      json: async () => ({
        error: "Faltan datos requeridos",
      }),
    } as Response);

    await expect(
      subscriptionService.createSubscription({
        user_name: "",
        email: "",
        payment_method: { type: "" },
      }),
    ).rejects.toEqual(expect.any(AppError));
  });
});
