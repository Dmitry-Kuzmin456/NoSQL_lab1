import { api } from "./client";
import type { Order, OrderList, OrderStatus } from "./types";

export function listMyOrders(status?: OrderStatus): Promise<OrderList> {
  const search = new URLSearchParams({ limit: "50" });
  if (status) search.set("status", status);
  return api<OrderList>(`/api/users/me/orders?${search.toString()}`);
}

export function cancelOrder(orderId: string): Promise<Order> {
  return api<Order>(`/api/users/me/orders/${orderId}/cancel`, {
    method: "POST",
  });
}

export function listAllOrders(status?: OrderStatus): Promise<OrderList> {
  const search = new URLSearchParams({ limit: "50" });
  if (status) search.set("status", status);
  return api<OrderList>(`/api/orders?${search.toString()}`);
}

export function approveOrder(orderId: string): Promise<Order> {
  return api<Order>(`/api/orders/${orderId}/approve`, { method: "POST" });
}

export function rejectOrder(orderId: string): Promise<Order> {
  return api<Order>(`/api/orders/${orderId}/reject`, { method: "POST" });
}
