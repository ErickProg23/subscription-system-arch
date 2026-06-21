import { afterEach, describe, expect, it, vi } from "vitest";
import { AppError, requestJson } from "./apiClient";

describe("requestJson", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("retorna el body si la respuesta es exitosa", async () => {
    vi.spyOn(window, "fetch").mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({ message: "ok" }),
    } as Response);

    const response = await requestJson<{ message: string }>("/api/test");
    expect(response.message).toBe("ok");
  });

  it("lanza error de validación en respuestas 400", async () => {
    vi.spyOn(window, "fetch").mockResolvedValue({
      ok: false,
      status: 400,
      json: async () => ({ error: "Payload inválido" }),
    } as Response);

    await expect(requestJson("/api/test")).rejects.toEqual(
      expect.objectContaining<AppError>({
        type: "validation",
        message: "Payload inválido",
      }),
    );
  });

  it("reintenta errores 500 y luego responde correctamente", async () => {
    const fetchMock = vi
      .spyOn(window, "fetch")
      .mockResolvedValueOnce({
        ok: false,
        status: 500,
        json: async () => ({ error: "server error" }),
      } as Response)
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({ message: "ok" }),
      } as Response);

    const response = await requestJson<{ message: string }>("/api/test", {
      retries: 2,
    });

    expect(fetchMock).toHaveBeenCalledTimes(2);
    expect(response.message).toBe("ok");
  });

  it("lanza timeout cuando la solicitud aborta en el último intento", async () => {
    vi.spyOn(window, "fetch").mockRejectedValue(
      new DOMException("Abortado", "AbortError"),
    );

    await expect(requestJson("/api/test", { retries: 1 })).rejects.toEqual(
      expect.objectContaining<AppError>({
        type: "timeout",
      }),
    );
  });

  it("lanza error de red si fetch falla en el último intento", async () => {
    vi.spyOn(window, "fetch").mockRejectedValue(new Error("network down"));

    await expect(requestJson("/api/test", { retries: 1 })).rejects.toEqual(
      expect.objectContaining<AppError>({
        type: "network",
      }),
    );
  });
});
