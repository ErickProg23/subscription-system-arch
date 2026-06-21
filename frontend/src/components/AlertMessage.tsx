import type { AppErrorType } from "../services/apiClient";

interface AlertMessageProps {
  message: string | null;
  type?: AppErrorType | "info" | "success" | "warning";
}

export function AlertMessage({ message, type = "info" }: AlertMessageProps) {
  if (!message) {
    return null;
  }

  const classNameMap: Record<string, string> = {
    validation: "alert alert--warning",
    server: "alert alert--danger",
    timeout: "alert alert--warning",
    network: "alert alert--danger",
    info: "alert alert--info",
    success: "alert alert--success",
    warning: "alert alert--warning",
  };

  return (
    <div className={classNameMap[type] ?? classNameMap.info} role="alert">
      {message}
    </div>
  );
}
