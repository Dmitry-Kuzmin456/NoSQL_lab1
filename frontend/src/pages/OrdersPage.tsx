import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { ApiError } from "../api/client";
import { cancelOrder, listMyOrders } from "../api/orders";
import type { Order } from "../api/types";
import { formatPrice, ORDER_STATUS_LABEL } from "../lib/format";
import { usePaths } from "../routing";

export function OrdersPage() {
  const paths = usePaths();
  const [orders, setOrders] = useState<Order[]>([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  async function load() {
    setLoading(true);
    try {
      const result = await listMyOrders();
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

  async function onCancel(orderId: string) {
    try {
      await cancelOrder(orderId);
      await load();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Не удалось отменить заявку");
    }
  }

  if (loading) {
    return <div className="skeleton" />;
  }

  if (orders.length === 0) {
    return (
      <div className="card empty">
        <p>Заявок пока нет</p>
        <p>
          <Link to={paths.catalog}>В каталог</Link>
        </p>
      </div>
    );
  }

  return (
    <>
      <h1>Заявки</h1>
      {error ? <p className="error">{error}</p> : null}
      <div className="list" style={{ marginTop: 16 }}>
        {orders.map((order) => (
          <article key={order.id} className="card row">
            <div className="row__main">
              <strong>{order.product_snapshot.name}</strong>
              <span className="muted">
                {order.quantity} шт. · {formatPrice(order.total_amount)}
              </span>
            </div>
            <div className="row__actions">
              <span className={`status status--${order.status}`}>
                {ORDER_STATUS_LABEL[order.status]}
              </span>
              {order.status === "CREATED" ? (
                <button
                  type="button"
                  className="btn btn--danger"
                  onClick={() => void onCancel(order.id)}
                >
                  Отменить
                </button>
              ) : null}
            </div>
          </article>
        ))}
      </div>
    </>
  );
}
