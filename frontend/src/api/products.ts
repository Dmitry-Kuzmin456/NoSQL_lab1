import { api } from "./client";
import type { Product, ProductList, ProductSortBy } from "./types";

export const PAGE_SIZE = 12;

export type ProductQuery = {
  query?: string;
  min_price?: string;
  max_price?: string;
  in_stock_only?: boolean;
  sort_by?: ProductSortBy;
  offset?: number;
  limit?: number;
};

export function listProducts(params: ProductQuery): Promise<ProductList> {
  const search = new URLSearchParams();
  if (params.query) search.set("query", params.query);
  if (params.min_price) search.set("min_price", params.min_price);
  if (params.max_price) search.set("max_price", params.max_price);
  if (params.in_stock_only) search.set("in_stock_only", "true");
  search.set("sort_by", params.sort_by ?? "popularity");
  search.set("offset", String(params.offset ?? 0));
  search.set("limit", String(params.limit ?? PAGE_SIZE));
  return api<ProductList>(`/api/products?${search.toString()}`);
}

export function getProduct(productId: string): Promise<Product> {
  return api<Product>(`/api/products/${productId}`);
}

export function createProduct(payload: {
  name: string;
  description: string;
  price: string;
  quantity: number;
}): Promise<Product> {
  return api<Product>("/api/products", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function updateProduct(
  productId: string,
  payload: {
    name?: string;
    description?: string;
    price?: string;
    quantity?: number;
  },
): Promise<Product> {
  return api<Product>(`/api/products/${productId}`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export function deleteProduct(productId: string): Promise<void> {
  return api<void>(`/api/products/${productId}`, { method: "DELETE" });
}

export function reserveStock(productId: string, amount: number): Promise<Product> {
  return api<Product>(`/api/products/${productId}/reserve`, {
    method: "POST",
    body: JSON.stringify({ amount }),
  });
}

export function restoreStock(productId: string, amount: number): Promise<Product> {
  return api<Product>(`/api/products/${productId}/restore`, {
    method: "POST",
    body: JSON.stringify({ amount }),
  });
}
