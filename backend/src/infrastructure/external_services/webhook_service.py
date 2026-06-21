import time
from turtle import delay


class WebhookNotificationService:
    """ Este sservicio simulara la conexion a un sistema externo..
    Implementa el patron de reintetos (Retry Pattern)"""

    def __init__(self):
        self.simulate_500_error = False

    def notify_payment_success(self, subscription_id: str) -> bool:
        max_retries = 3
        delay = 1  # segundos

        for attempt in range(1, max_retries + 1):
            try: 
                print(f"\n[Webhook] Intentando notificar suscripción {subscription_id} (Intento {attempt}/{max_retries})...")

                if self.simulate_500_error:
                    raise RuntimeError("500 Internal Server Error - El servicio externo no responde")
                
            # Si no hay error, simulamos que tardó medio segundo en responder y fue un éxito
                time.sleep(0.5)
                print(f"[Webhook] ✅ Éxito: Servidor externo confirmó recepción de la suscripción {subscription_id}")
                return True
            
            except RuntimeError as error:
                print(f"[Webhook] Fallo: {str(error)}")

                if attempt == max_retries:
                    print(f"[Webhook] Se agotaron los intentos. No se pudo notificar al servidor externo.")
                    return False
                
                print(f"[Webhook] Reintentando en {delay} segundos...")
                time.sleep(delay)
                delay *= 2  # Incrementa el tiempo de espera para el próximo intento (exponencial)

        return False