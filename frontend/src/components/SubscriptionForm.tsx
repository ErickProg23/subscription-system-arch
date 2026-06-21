import type { FieldErrors, SubscriptionPayload } from "../types/subscription";

interface SubscriptionFormProps {
  formData: SubscriptionPayload;
  fieldErrors: FieldErrors;
  isSubmitting: boolean;
  onChange: (field: "user_name" | "email" | "payment_method", value: string) => void;
  onSubmit: () => void;
}

export function SubscriptionForm({
  formData,
  fieldErrors,
  isSubmitting,
  onChange,
  onSubmit,
}: SubscriptionFormProps) {
  return (
    <form
      className="card"
      onSubmit={(event) => {
        event.preventDefault();
        onSubmit();
      }}
    >
      <div className="form-group">
        <label htmlFor="name">Nombre completo</label>
        <input
          id="name"
          type="text"
          value={formData.user_name}
          onChange={(event) => onChange("user_name", event.target.value)}
          aria-invalid={Boolean(fieldErrors.name)}
          aria-describedby="name-error"
          placeholder="Ej. Juan Perez"
        />
        {fieldErrors.name ? (
          <p id="name-error" className="field-error">
            {fieldErrors.name}
          </p>
        ) : null}
      </div>

      <div className="form-group">
        <label htmlFor="email">Correo electrónico</label>
        <input
          id="email"
          type="email"
          value={formData.email}
          onChange={(event) => onChange("email", event.target.value)}
          aria-invalid={Boolean(fieldErrors.email)}
          aria-describedby="email-error"
          placeholder="correo@ejemplo.com"
        />
        {fieldErrors.email ? (
          <p id="email-error" className="field-error">
            {fieldErrors.email}
          </p>
        ) : null}
      </div>

      <div className="form-group">
        <label htmlFor="payment-method">Método de pago</label>
        <select
          id="payment-method"
          value={formData.payment_method.type}
          onChange={(event) => onChange("payment_method", event.target.value)}
          aria-invalid={Boolean(fieldErrors.paymentMethod)}
          aria-describedby="payment-method-error"
        >
          <option value="">Selecciona una opción</option>
          <option value="tarjeta">Tarjeta de crédito</option>
          <option value="paypal">PayPal</option>
          <option value="transferencia">Transferencia bancaria</option>
        </select>
        {fieldErrors.paymentMethod ? (
          <p id="payment-method-error" className="field-error">
            {fieldErrors.paymentMethod}
          </p>
        ) : null}
      </div>

      <button className="button button--primary" type="submit" disabled={isSubmitting}>
        {isSubmitting ? "Procesando pago..." : "Procesar pago y suscribirme"}
      </button>
    </form>
  );
}
