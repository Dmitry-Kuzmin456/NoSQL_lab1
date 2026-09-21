import type { OrderStatus, UserRole } from "../api/types";

export function formatPrice(price: string | number): string {
  const num = typeof price === "string" ? parseFloat(price) : price;
  if (isNaN(num)) {
    return `${price} ₽`;
  }
  return `${num.toLocaleString("ru-RU")} ₽`;
}

export const ORDER_STATUS_LABEL: Record<OrderStatus, string> = {
  CREATED: "Создана",
  APPROVED: "Одобрена",
  REJECTED: "Отклонена",
  CANCELLED: "Отменена",
};

export function roleLabel(role: UserRole): string {
  switch (role) {
    case "STUDENT":
      return "Студент";
    case "TEACHER":
      return "Преподаватель";
    case "ADMIN":
      return "Администратор";
    default:
      return role;
  }
}
