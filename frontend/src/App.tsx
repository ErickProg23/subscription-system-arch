import { useEffect, useMemo, useState } from "react";
import { AlertMessage } from "./components/AlertMessage";
import { NotificationToast } from "./components/NotificationToast";
import { SubscriptionDashboard } from "./components/SubscriptionDashboard";
import { SubscriptionForm } from "./components/SubscriptionForm";
import { usePaymentConfirmation } from "./hooks/usePaymentConfirmation";
import { AppError } from "./services/apiClient";
import { subscriptionService } from "./services/subscriptionService";
import type {
  FieldErrors,
  Subscription,
  SubscriptionPayload,
} from "./types/subscription";
import { validateSubscriptionPayload } from "./utils/validation";

const initialFormState: SubscriptionPayload = {
  user_name: "",
  email: "",
  payment_method: {
    type: "",
  },
};

export default function App() {
  const [formData, setFormData] = useState<SubscriptionPayload>(initialFormState);
  const [fieldErrors, setFieldErrors] = useState<FieldErrors>({});
  const [subscription, setSubscription] = useState<Subscription | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isActionLoading, setIsActionLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [errorType, setErrorType] = useState<
    "validation" | "server" | "timeout" | "network" | "info" | "success" | "warning"
  >("info");
  const [toastMessage, setToastMessage] = useState("");
  const [toastVisible, setToastVisible] = useState(false);

  const {
    paymentStatus,
    paymentMessage,
    setPaymentMessage,
    waitForConfirmation,
  } = usePaymentConfirmation();

  useEffect(() => {
    if (!toastVisible) {
      return undefined;
    }

    const timeoutId = window.setTimeout(() => {
      setToastVisible(false);
    }, 4000);

    return () => window.clearTimeout(timeoutId);
  }, [toastVisible]);

  const headerDescription = useMemo(
    () =>
      "Gestiona el flujo de suscripción, visualiza su estado real y confirma el pago con feedback en tiempo real.",
    [],
  );

  function showToast(message: string) {
    setToastMessage(message);
    setToastVisible(true);
  }

  function clearMessages() {
    setErrorMessage(null);
    setFieldErrors({});
  }

  function handleFormChange(
    field: "user_name" | "email" | "payment_method",
    value: string,
  ) {
    setFormData((current) => {
      if (field === "payment_method") {
        return {
          ...current,
          payment_method: {
            type: value,
          },
        };
      }

      return {
        ...current,
        [field]: value,
      };
    });
  }

  async function refreshSubscription(subscriptionId: string) {
    const response = await subscriptionService.getSubscription(subscriptionId);
    setSubscription(response.data);
  }

  async function handleSubmit() {
    clearMessages();
    const validation = validateSubscriptionPayload(formData);

    if (!validation.isValid) {
      setFieldErrors(validation.fieldErrors);
      setErrorType("validation");
      setErrorMessage("Corrige los campos marcados antes de continuar.");
      return;
    }

    setIsSubmitting(true);

    try {
      const response = await subscriptionService.createSubscription(formData);
      setSubscription(response.data);
      setPaymentMessage("Suscripción creada. Esperando confirmación del pago...");

      const confirmedStatus = await waitForConfirmation(response.data.id);
      await refreshSubscription(response.data.id);

      if (confirmedStatus === "CONFIRMED") {
        showToast("¡Pago exitoso! Suscripción activada.");
      }

      if (confirmedStatus === "FAILED") {
        setErrorType("server");
        setErrorMessage("El pago no pudo confirmarse correctamente.");
      }
    } catch (error) {
      if (error instanceof AppError) {
        setErrorType(error.type);
        setErrorMessage(error.message);
      } else {
        setErrorType("network");
        setErrorMessage("Ocurrió un error inesperado.");
      }
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleCancel() {
    if (!subscription) {
      return;
    }

    setIsActionLoading(true);
    clearMessages();

    try {
      await subscriptionService.cancelSubscription(subscription.id);
      await refreshSubscription(subscription.id);
      setErrorType("warning");
      setErrorMessage("La suscripción fue cancelada.");
      showToast("Suscripción cancelada exitosamente.");
    } catch (error) {
      if (error instanceof AppError) {
        setErrorType(error.type);
        setErrorMessage(error.message);
      }
    } finally {
      setIsActionLoading(false);
    }
  }

  async function handleExpire() {
    if (!subscription) {
      return;
    }

    setIsActionLoading(true);
    clearMessages();

    try {
      await subscriptionService.expireSubscription(subscription.id);
      await refreshSubscription(subscription.id);
      setErrorType("warning");
      setErrorMessage("La suscripción fue marcada como expirada.");
      showToast("Suscripción marcada como expirada.");
    } catch (error) {
      if (error instanceof AppError) {
        setErrorType(error.type);
        setErrorMessage(error.message);
      }
    } finally {
      setIsActionLoading(false);
    }
  }

  return (
    <main className="app-shell">
      <NotificationToast message={toastMessage} visible={toastVisible} />

      <section className="hero">
        <p className="eyebrow">Frontend React + TypeScript</p>
        <h1>Portal de Suscripciones</h1>
        <p className="hero-copy">{headerDescription}</p>
      </section>

      <AlertMessage message={errorMessage} type={errorType} />

      <div className="layout">
        <SubscriptionForm
          formData={formData}
          fieldErrors={fieldErrors}
          isSubmitting={isSubmitting}
          onChange={handleFormChange}
          onSubmit={handleSubmit}
        />

        {subscription ? (
          <SubscriptionDashboard
            subscription={subscription}
            paymentStatus={paymentStatus}
            paymentMessage={paymentMessage}
            isActionLoading={isActionLoading}
            onCancel={handleCancel}
            onExpire={handleExpire}
          />
        ) : (
          <section className="card card--empty">
            <h2>Dashboard de suscripción</h2>
            <p>
              Aquí verás el estado actual de la suscripción y la confirmación del
              pago cuando completes el formulario.
            </p>
          </section>
        )}
      </div>
    </main>
  );
}
