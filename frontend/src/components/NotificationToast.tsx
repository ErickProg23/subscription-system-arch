interface NotificationToastProps {
  message: string;
  visible: boolean;
}

export function NotificationToast({
  message,
  visible,
}: NotificationToastProps) {
  return (
    <div
      className={`toast ${visible ? "toast--visible" : ""}`}
      aria-live="polite"
      role="status"
    >
      {message}
    </div>
  );
}
