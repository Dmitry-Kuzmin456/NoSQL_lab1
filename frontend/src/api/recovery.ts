import { api } from "./client";
import type { RecoveryToken } from "./types";

export function requestRecovery(email: string): Promise<RecoveryToken> {
  return api<RecoveryToken>("/api/recovery", {
    method: "POST",
    body: JSON.stringify({ email }),
    skipAuthRetry: true,
  });
}

export function resetPassword(token: string, newPassword: string): Promise<{ message: string }> {
  return api<{ message: string }>("/api/recovery/reset-password", {
    method: "POST",
    body: JSON.stringify({ token, new_password: newPassword }),
    skipAuthRetry: true,
  });
}
