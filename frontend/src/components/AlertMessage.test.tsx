import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AlertMessage } from "./AlertMessage";

describe("AlertMessage", () => {
  it("no renderiza nada si no hay mensaje", () => {
    const { container } = render(<AlertMessage message={null} />);
    expect(container).toBeEmptyDOMElement();
  });

  it("renderiza el mensaje con la clase correspondiente", () => {
    render(<AlertMessage message="Error del servidor" type="server" />);

    const alert = screen.getByRole("alert");
    expect(alert).toHaveTextContent("Error del servidor");
    expect(alert.className).toContain("alert--danger");
  });
});
