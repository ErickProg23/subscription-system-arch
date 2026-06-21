import type {
  PaymentStatus,
  Subscription,
  SubscriptionStatus,
} from "../types/subscription";

interface SubscriptionDashboardProps {
  subscription: Subscription;
  paymentStatus: PaymentStatus;
  paymentMessage: string;
  isActionLoading: boolean;
  onCancel: () => void;
  onExpire: () => void;
}

function statusClassName(status: SubscriptionStatus) {
  if (status === "Activa") {
    return "badge badge--success";
  }
  if (status === "Cancelada") {
    return "badge badge--danger";
  }
  return "badge badge--warning";
}

function paymentClassName(status: PaymentStatus) {
  if (status === "CONFIRMED") {
    return "badge badge--success";
  }
  if (status === "FAILED") {
    return "badge badge--danger";
  }
  return "badge badge--info";
}

function paymentLabel(status: PaymentStatus) {
  if (status === "CONFIRMED") {
    return "Pago inicial confirmado";
  }
  if (status === "FAILED") {
    return "Pago inicial no confirmado";
  }
  return "Pago inicial pendiente";
}

function formatPaymentMethod(paymentMethod: Subscription["payment_method"]) {
  let value =
    typeof paymentMethod === "string" ? paymentMethod : paymentMethod.type;

  if (typeof value === "string") {
    const trimmedValue = value.trim();

    if (trimmedValue.startsWith("{") && trimmedValue.includes("type")) {
      try {
        const normalizedJson = trimmedValue.replace(/'/g, '"');
        const parsedValue = JSON.parse(normalizedJson) as { type?: string };
        value = parsedValue.type ?? trimmedValue;
      } catch {
        value = trimmedValue;
      }
    }
  }

  if (value === "tarjeta") {
    return "Tarjeta de crédito";
  }
  if (value === "paypal") {
    return "PayPal";
  }
  if (value === "transferencia") {
    return "Transferencia bancaria";
  }

  return value || "No disponible";
}

export function SubscriptionDashboard({
  subscription,
  paymentStatus,
  paymentMessage,
  isActionLoading,
  onCancel,
  onExpire,
}: SubscriptionDashboardProps) {
  const allowActions = subscription.status === "Activa";

  return (
    <section className="card">
      <h2>Resumen de tu suscripción</h2>
      <div className="dashboard-grid">
        <div>
          <p className="dashboard-label">Estado actual</p>
          <span className={statusClassName(subscription.status)}>
            {subscription.status}
          </span>
        </div>
        <div>
          <p className="dashboard-label">Confirmación del pago inicial</p>
          <span className={paymentClassName(paymentStatus)}>
            {paymentLabel(paymentStatus)}
          </span>
        </div>
      </div>

      <div className="subscription-details">
        <div>
          <p className="dashboard-label">Nombre</p>
          <p className="dashboard-value">{subscription.user_name}</p>
        </div>
        <div>
          <p className="dashboard-label">Correo electrónico</p>
          <p className="dashboard-value">{subscription.email}</p>
        </div>
        <div>
          <p className="dashboard-label">Método de pago</p>
          <p className="dashboard-value">
            {formatPaymentMethod(subscription.payment_method)}
          </p>
        </div>
        <div>
          <p className="dashboard-label">ID de referencia</p>
          <p className="dashboard-value">{subscription.id}</p>
        </div>
      </div>

      <p className="dashboard-message">{paymentMessage}</p>

      <div className="actions">
        <button
          className="button button--danger"
          type="button"
          onClick={onCancel}
          disabled={!allowActions || isActionLoading}
        >
          {isActionLoading ? "Procesando..." : "Cancelar suscripción"}
        </button>
        <button
          className="button button--warning"
          type="button"
          onClick={onExpire}
          disabled={!allowActions || isActionLoading}
        >
          {isActionLoading ? "Procesando..." : "Marcar como expirada"}
        </button>
      </div>
    </section>
  );
}
