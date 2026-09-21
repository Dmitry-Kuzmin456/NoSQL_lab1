import { useEffect, useState } from "react";
import { ApiError } from "../api/client";
import { approveOrder, listAllOrders, rejectOrder } from "../api/orders";
import type { Order, OrderStatus } from "../api/types";
import { formatPrice, ORDER_STATUS_LABEL } from "../lib/format";

export function AdminOrdersPage() {
  const [status, setStatus] = useState<OrderStatus | "">("");
  const [orders, setOrders] = useState<Order[]>([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  async function load(nextStatus: OrderStatus | "" = status) {
    setLoading(true);
    try {
      const result = await listAllOrders(nextStatus || undefined);
      setOrders(result.items);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Не удалось загрузить заявки");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void load();
  }, []);

  async function act(kind: "approve" | "reject", orderId: string) {
    try {
      if (kind === "approve") await approveOrder(orderId);
      if (kind === "reject") await rejectOrder(orderId);
      await load();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Не удалось обновить заявку");
    }
  }

  return (
    <>
      <div className="page-head">
        <h1>Все заявки</h1>
        <select
          value={status}
          onChange={(event) => {
            const value = event.target.value as OrderStatus | "";
            setStatus(value);
            void load(value);
          }}
        >
          <option value="">Все статусы</option>
          <option value="CREATED">Созданы</option>
          <option value="APPROVED">Одобрены</option>
          <option value="REJECTED">Отклонены</option>
          <option value="CANCELLED">Отменены</option>
        </select>
      </div>
      {error ? <p className="error">{error}</p> : null}
      {loading ? <div className="skeleton" /> : null}
      {!loading && orders.length === 0 ? <div className="card empty">Заявок нет</div> : null}
      <div className="list">
        {orders.map((order) => (
          <article key={order.id} className="card row">
            <div className="row__main">
              <strong>{order.product_snapshot.name}</strong>
              <span className="muted">
                {order.quantity} шт. · {formatPrice(order.total_amount)} · {order.user_id}
              </span>
            </div>
            <div className="row__actions">
              <span className={`status status--${order.status}`}>
                {ORDER_STATUS_LABEL[order.status]}
              </span>
              {order.status === "CREATED" ? (
                <>
                  <button type="button" className="btn btn--primary" onClick={() => void act("approve", order.id)}>
                    Ок
                  </button>
                  <button type="button" className="btn btn--ghost" onClick={() => void act("reject", order.id)}>
                    Отклонить
                  </button>
                </>
              ) : null}
            </div>
          </article>
        ))}
      </div>
    </>
  );
}
