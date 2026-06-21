export type SubscriptionStatus = "Activa" | "Cancelada" | "Expirada";
export type PaymentStatus = "PENDING" | "CONFIRMED" | "FAILED";

export interface PaymentMethod {
  type: string;
}

export interface Subscription {
  id: string;
  user_name: string;
  email: string;
  payment_method: PaymentMethod | string;
  status: SubscriptionStatus;
  created_at: string;
}

export interface SubscriptionPayload {
  user_name: string;
  email: string;
  payment_method: PaymentMethod;
}

export interface ApiResponse<T> {
  message: string;
  data: T;
}

export interface PaymentStatusResponse {
  message: string;
  payment_status: PaymentStatus;
  attempts?: number;
}

export interface FieldErrors {
  name?: string;
  email?: string;
  paymentMethod?: string;
}
