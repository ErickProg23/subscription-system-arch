import { useCallback, useState } from "react";
import { subscriptionService } from "../services/subscriptionService";
import type { PaymentStatus } from "../types/subscription";

export function usePaymentConfirmation() {
  const [paymentStatus, setPaymentStatus] = useState<PaymentStatus>("PENDING");
  const [paymentMessage, setPaymentMessage] = useState(
    "Pendiente de confirmación",
  );

  const waitForConfirmation = useCallback(
    async (subscriptionId: string, maxAttempts = 8, intervalMs = 1500) => {
      setPaymentStatus("PENDING");
      setPaymentMessage("Suscripción creada. Esperando confirmación del pago...");

      for (let attempt = 0; attempt < maxAttempts; attempt += 1) {
        const response = await subscriptionService.getPaymentStatus(subscriptionId);
        setPaymentStatus(response.payment_status);

        if (response.payment_status === "CONFIRMED") {
          setPaymentMessage("Pago confirmado correctamente por el backend.");
          return "CONFIRMED" as const;
        }

        if (response.payment_status === "FAILED") {
          setPaymentMessage("La confirmación del pago falló.");
          return "FAILED" as const;
        }

        setPaymentMessage(
          `Confirmando pago... intento ${attempt + 1} de ${maxAttempts}.`,
        );
        await new Promise((resolve) => window.setTimeout(resolve, intervalMs));
      }

      setPaymentMessage(
        "La confirmación sigue pendiente. Puedes volver a consultar en unos segundos.",
      );
      return "PENDING" as const;
    },
    [],
  );

  return {
    paymentStatus,
    paymentMessage,
    setPaymentStatus,
    setPaymentMessage,
    waitForConfirmation,
  };
}
