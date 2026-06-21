import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { NotificationToast } from "./NotificationToast";

describe("NotificationToast", () => {
  it("renderiza el mensaje del toast", () => {
    render(<NotificationToast message="Pago confirmado" visible={true} />);
    expect(screen.getByRole("status")).toHaveTextContent("Pago confirmado");
  });

  it("aplica la clase visual cuando está visible", () => {
    render(<NotificationToast message="Pago confirmado" visible={true} />);
    expect(screen.getByRole("status").className).toContain("toast--visible");
  });
});
