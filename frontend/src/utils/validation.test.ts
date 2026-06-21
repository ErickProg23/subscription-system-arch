import { describe, expect, it } from "vitest";
import { validateSubscriptionPayload } from "./validation";

describe("validateSubscriptionPayload", () => {
  it("retorna errores cuando faltan campos requeridos", () => {
    const result = validateSubscriptionPayload({
      user_name: "",
      email: "",
      payment_method: { type: "" },
    });

    expect(result.isValid).toBe(false);
    expect(result.fieldErrors.name).toBe("El nombre es obligatorio.");
    expect(result.fieldErrors.email).toBe("El correo es obligatorio.");
    expect(result.fieldErrors.paymentMethod).toBe(
      "Selecciona un método de pago.",
    );
  });

  it("acepta payloads válidos", () => {
    const result = validateSubscriptionPayload({
      user_name: "Erick Perez",
      email: "erick@example.com",
      payment_method: { type: "tarjeta" },
    });

    expect(result.isValid).toBe(true);
    expect(result.fieldErrors).toEqual({});
  });
});
