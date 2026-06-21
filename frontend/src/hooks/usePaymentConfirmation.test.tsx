import { act, renderHook } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { usePaymentConfirmation } from "./usePaymentConfirmation";
import { subscriptionService } from "../services/subscriptionService";

describe("usePaymentConfirmation", () => {
  it("confirma el pago cuando el servicio responde CONFIRMED", async () => {
    vi.spyOn(subscriptionService, "getPaymentStatus").mockResolvedValue({
      message: "ok",
      payment_status: "CONFIRMED",
      attempts: 1,
    });

    const { result } = renderHook(() => usePaymentConfirmation());

    await act(async () => {
      const status = await result.current.waitForConfirmation("sub-1", 1, 0);
      expect(status).toBe("CONFIRMED");
    });

    expect(result.current.paymentStatus).toBe("CONFIRMED");
    expect(result.current.paymentMessage).toContain("Pago confirmado");
  });

  it("marca fallo cuando el servicio responde FAILED", async () => {
    vi.spyOn(subscriptionService, "getPaymentStatus").mockResolvedValue({
      message: "ok",
      payment_status: "FAILED",
      attempts: 3,
    });

    const { result } = renderHook(() => usePaymentConfirmation());

    await act(async () => {
      const status = await result.current.waitForConfirmation("sub-2", 1, 0);
      expect(status).toBe("FAILED");
    });

    expect(result.current.paymentStatus).toBe("FAILED");
    expect(result.current.paymentMessage).toContain("falló");
  });

  it("mantiene el estado pendiente si no llega confirmación", async () => {
    vi.spyOn(subscriptionService, "getPaymentStatus").mockResolvedValue({
      message: "ok",
      payment_status: "PENDING",
      attempts: 1,
    });

    const { result } = renderHook(() => usePaymentConfirmation());

    await act(async () => {
      const status = await result.current.waitForConfirmation("sub-3", 2, 0);
      expect(status).toBe("PENDING");
    });

    expect(result.current.paymentStatus).toBe("PENDING");
    expect(result.current.paymentMessage).toContain("sigue pendiente");
  });
});
