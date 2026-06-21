import type { FieldErrors, SubscriptionPayload } from "../types/subscription";

export interface ValidationResult {
  isValid: boolean;
  fieldErrors: FieldErrors;
}

const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export function validateSubscriptionPayload(
  payload: SubscriptionPayload,
): ValidationResult {
  const fieldErrors: FieldErrors = {};

  if (!payload.user_name.trim()) {
    fieldErrors.name = "El nombre es obligatorio.";
  } else if (payload.user_name.trim().length < 3) {
    fieldErrors.name = "El nombre debe tener al menos 3 caracteres.";
  }

  if (!payload.email.trim()) {
    fieldErrors.email = "El correo es obligatorio.";
  } else if (!emailPattern.test(payload.email.trim())) {
    fieldErrors.email = "Ingresa un correo electrónico válido.";
  }

  if (!payload.payment_method.type.trim()) {
    fieldErrors.paymentMethod = "Selecciona un método de pago.";
  }

  return {
    isValid: Object.keys(fieldErrors).length === 0,
    fieldErrors,
  };
}
