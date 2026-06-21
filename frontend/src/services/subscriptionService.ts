import { requestJson } from "./apiClient";
import type {
  ApiResponse,
  PaymentStatusResponse,
  Subscription,
  SubscriptionPayload,
} from "../types/subscription";

export const subscriptionService = {
  createSubscription(payload: SubscriptionPayload) {
    return requestJson<ApiResponse<Subscription>>("/api/subscribirse", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
      retries: 3,
      timeoutMs: 8000,
    });
  },

  getSubscription(subscriptionId: string) {
    return requestJson<ApiResponse<Subscription>>(`/api/subscribirse/${subscriptionId}`, {
      method: "GET",
      retries: 2,
      timeoutMs: 5000,
    });
  },

  getPaymentStatus(subscriptionId: string) {
    return requestJson<PaymentStatusResponse>(
      `/api/subscribirse/${subscriptionId}/payment-status`,
      {
        method: "GET",
        retries: 2,
        timeoutMs: 5000,
      },
    );
  },

  cancelSubscription(subscriptionId: string) {
    return requestJson<{ message: string; status: string }>(
      `/api/subscribirse/${subscriptionId}/cancelar`,
      {
        method: "POST",
        retries: 2,
        timeoutMs: 5000,
      },
    );
  },

  expireSubscription(subscriptionId: string) {
    return requestJson<{ message: string; status: string }>(
      `/api/subscribirse/${subscriptionId}/expirar`,
      {
        method: "POST",
        retries: 2,
        timeoutMs: 5000,
      },
    );
  },
};
