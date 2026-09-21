import { api } from "./client";
import type { Cart, CheckoutResult, Favourites } from "./types";

export function getFavourites(): Promise<Favourites> {
  return api<Favourites>("/api/users/me/favourites");
}

export function addFavourite(productId: string): Promise<Favourites> {
  return api<Favourites>("/api/users/me/favourites", {
    method: "POST",
    body: JSON.stringify({ product_id: productId }),
  });
}

export function removeFavourite(productId: string): Promise<Favourites> {
  return api<Favourites>(`/api/users/me/favourites/${productId}`, {
    method: "DELETE",
  });
}

export function getCart(): Promise<Cart> {
  return api<Cart>("/api/users/me/cart");
}

export function setCartQuantity(productId: string, quantity: number): Promise<Cart> {
  return api<Cart>(`/api/users/me/cart/items/${productId}`, {
    method: "PATCH",
    body: JSON.stringify({ quantity }),
  });
}

export function removeCartItem(productId: string): Promise<Cart> {
  return api<Cart>(`/api/users/me/cart/items/${productId}`, {
    method: "DELETE",
  });
}

export function clearFavourites(): Promise<Favourites> {
  return api<Favourites>("/api/users/me/favourites", { method: "DELETE" });
}

export function clearCart(): Promise<Cart> {
  return api<Cart>("/api/users/me/cart", { method: "DELETE" });
}

export function checkout(): Promise<CheckoutResult> {
  return api<CheckoutResult>("/api/users/me/checkout", { method: "POST" });
}
