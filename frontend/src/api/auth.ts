import { api } from "./client";
import type { User, UserRole } from "./types";

export function getMe(): Promise<User> {
  return api<User>("/api/users/me");
}

export function getUser(userId: string): Promise<User> {
  return api<User>(`/api/users/${userId}`);
}

export function getUserByEmail(email: string): Promise<User> {
  const search = new URLSearchParams({ email: email.trim() });
  return api<User>(`/api/users/by-email?${search.toString()}`);
}

export function login(email: string, password: string): Promise<User> {
  return api<User>("/api/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
    skipAuthRetry: true,
  });
}

export function register(
  name: string,
  email: string,
  password: string,
  role: UserRole = "STUDENT",
): Promise<User> {
  return api<User>("/api/users/register", {
    method: "POST",
    body: JSON.stringify({ name, email, password, role }),
    skipAuthRetry: true,
  });
}

export function logout(): Promise<void> {
  return api<void>("/api/auth/logout", { method: "POST", skipAuthRetry: true });
}

export function logoutAll(): Promise<void> {
  return api<void>("/api/auth/logout-all/me", { method: "POST" });
}

export function updateProfile(name: string, email: string): Promise<User> {
  return api<User>("/api/users/me", {
    method: "PATCH",
    body: JSON.stringify({ name, email }),
  });
}

export function changePassword(oldPassword: string, newPassword: string): Promise<void> {
  return api<void>("/api/users/me/change-password", {
    method: "POST",
    body: JSON.stringify({
      old_password: oldPassword,
      new_password: newPassword,
    }),
  });
}

export function deleteAccount(): Promise<void> {
  return api<void>("/api/users/me", { method: "DELETE" });
}
