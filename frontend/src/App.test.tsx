import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import App from "./App";

describe("App", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("muestra errores de validación si el formulario está vacío", async () => {
    render(<App />);

    fireEvent.click(
      screen.getByRole("button", { name: /procesar pago y suscribirme/i }),
    );

    expect(
      await screen.findByText(/corrige los campos marcados antes de continuar/i),
    ).toBeInTheDocument();
  });

  it("renderiza el dashboard tras crear una suscripción", async () => {
    const fetchMock = vi
      .spyOn(window, "fetch")
      .mockResolvedValueOnce({
        ok: true,
        status: 201,
        json: async () => ({
          message: "Suscripción creada exitosamente",
          data: {
            id: "sub-1",
            user_name: "Erick",
            email: "erick@example.com",
            payment_method: { type: "tarjeta" },
            status: "Activa",
            created_at: "2026-01-01T00:00:00",
          },
        }),
      } as Response)
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({
          message: "Estado consultado",
          payment_status: "CONFIRMED",
          attempts: 1,
        }),
      } as Response)
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({
          message: "Suscripción consultada exitosamente",
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

    render(<App />);

    fireEvent.change(screen.getByLabelText(/nombre completo/i), {
      target: { value: "Erick Perez" },
    });
    fireEvent.change(screen.getByLabelText(/correo electrónico/i), {
      target: { value: "erick@example.com" },
    });
    fireEvent.change(screen.getByLabelText(/método de pago/i), {
      target: { value: "tarjeta" },
    });

    fireEvent.click(
      screen.getByRole("button", { name: /procesar pago y suscribirme/i }),
    );

    await waitFor(() =>
      expect(
        screen.getByRole("heading", { name: /resumen de tu suscripción/i }),
      ).toBeInTheDocument(),
    );

    expect(fetchMock).toHaveBeenCalledTimes(3);
    expect(screen.getByText(/sub-1/i)).toBeInTheDocument();
  });
});
