import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { SubscriptionDashboard } from "./SubscriptionDashboard";

describe("SubscriptionDashboard", () => {
  it("muestra los datos completos de la suscripción", () => {
    render(
      <SubscriptionDashboard
        subscription={{
          id: "sub-1",
          user_name: "Erick Perez",
          email: "erick@example.com",
          payment_method: { type: "tarjeta" },
          status: "Activa",
          created_at: "2026-01-01T00:00:00",
        }}
        paymentStatus="CONFIRMED"
        paymentMessage="Pago confirmado correctamente por el backend."
        isActionLoading={false}
        onCancel={vi.fn()}
        onExpire={vi.fn()}
      />,
    );

    expect(screen.getByText("Erick Perez")).toBeInTheDocument();
    expect(screen.getByText("erick@example.com")).toBeInTheDocument();
    expect(screen.getByText("Tarjeta de crédito")).toBeInTheDocument();
    expect(screen.getByText("sub-1")).toBeInTheDocument();
    expect(
      screen.getByText("Confirmación del pago inicial"),
    ).toBeInTheDocument();
    expect(screen.getByText("Pago inicial confirmado")).toBeInTheDocument();
  });

  it("interpreta el método de pago serializado como string", () => {
    render(
      <SubscriptionDashboard
        subscription={{
          id: "sub-2",
          user_name: "Erick Perez",
          email: "erick@example.com",
          payment_method: "{'type': 'paypal'}",
          status: "Cancelada",
          created_at: "2026-01-01T00:00:00",
        }}
        paymentStatus="FAILED"
        paymentMessage="La confirmación del pago falló."
        isActionLoading={false}
        onCancel={vi.fn()}
        onExpire={vi.fn()}
      />,
    );

    expect(screen.getByText("PayPal")).toBeInTheDocument();
    expect(screen.getByText("Pago inicial no confirmado")).toBeInTheDocument();
  });

  it("ejecuta las acciones cuando la suscripción está activa", () => {
    const onCancel = vi.fn();
    const onExpire = vi.fn();

    render(
      <SubscriptionDashboard
        subscription={{
          id: "sub-3",
          user_name: "Erick Perez",
          email: "erick@example.com",
          payment_method: { type: "transferencia" },
          status: "Activa",
          created_at: "2026-01-01T00:00:00",
        }}
        paymentStatus="PENDING"
        paymentMessage="Pendiente de confirmación"
        isActionLoading={false}
        onCancel={onCancel}
        onExpire={onExpire}
      />,
    );

    fireEvent.click(screen.getByRole("button", { name: /cancelar/i }));
    fireEvent.click(screen.getByRole("button", { name: /marcar como expirada/i }));

    expect(onCancel).toHaveBeenCalledTimes(1);
    expect(onExpire).toHaveBeenCalledTimes(1);
  });

  it("deshabilita acciones cuando la suscripción no está activa", () => {
    render(
      <SubscriptionDashboard
        subscription={{
          id: "sub-4",
          user_name: "Erick Perez",
          email: "erick@example.com",
          payment_method: { type: "tarjeta" },
          status: "Expirada",
          created_at: "2026-01-01T00:00:00",
        }}
        paymentStatus="PENDING"
        paymentMessage="Pendiente de confirmación"
        isActionLoading={false}
        onCancel={vi.fn()}
        onExpire={vi.fn()}
      />,
    );

    expect(screen.getByRole("button", { name: /cancelar/i })).toBeDisabled();
    expect(
      screen.getByRole("button", { name: /marcar como expirada/i }),
    ).toBeDisabled();
  });
});
