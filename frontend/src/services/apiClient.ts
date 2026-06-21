export type AppErrorType = "validation" | "server" | "timeout" | "network";

export class AppError extends Error {
  type: AppErrorType;

  constructor(type: AppErrorType, message: string) {
    super(message);
    this.name = "AppError";
    this.type = type;
  }
}

interface RequestOptions extends RequestInit {
  retries?: number;
  timeoutMs?: number;
}

export async function requestJson<T>(
  input: string,
  options: RequestOptions = {},
): Promise<T> {
  const { retries = 3, timeoutMs = 8000, ...fetchOptions } = options;

  for (let attempt = 0; attempt < retries; attempt += 1) {
    const controller = new AbortController();
    const timeoutId = window.setTimeout(() => controller.abort(), timeoutMs);

    try {
      const response = await fetch(input, {
        ...fetchOptions,
        signal: controller.signal,
      });

      window.clearTimeout(timeoutId);

      let body: unknown = null;
      try {
        body = await response.json();
      } catch {
        body = null;
      }

      if (response.status >= 500) {
        if (attempt === retries - 1) {
          throw new AppError(
            "server",
            `Error del servidor (${response.status}). Intenta nuevamente en unos segundos.`,
          );
        }
        continue;
      }

      if (!response.ok) {
        const message =
          typeof body === "object" &&
          body !== null &&
          "error" in body &&
          typeof body.error === "string"
            ? body.error
            : "La solicitud no pudo completarse.";

        throw new AppError("validation", message);
      }

      return body as T;
    } catch (error) {
      window.clearTimeout(timeoutId);

      if (error instanceof AppError) {
        throw error;
      }

      if (error instanceof DOMException && error.name === "AbortError") {
        if (attempt === retries - 1) {
          throw new AppError(
            "timeout",
            "Timeout: el servidor tardó demasiado en responder.",
          );
        }
        continue;
      }

      if (attempt === retries - 1) {
        throw new AppError(
          "network",
          "Error de red: no se pudo conectar con el servidor tras varios intentos.",
        );
      }
    }
  }

  throw new AppError("network", "No se pudo completar la solicitud.");
}
