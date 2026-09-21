import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { ApiError } from "../api/client";
import { checkout, clearCart, removeCartItem, setCartQuantity } from "../api/shop";
import { useAuth } from "../auth/AuthContext";
import { formatPrice } from "../lib/format";
import { usePaths } from "../routing";

export function CartPage() {
  const navigate = useNavigate();
  const { cart, refreshShop } = useAuth();
  const paths = usePaths();
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);
  const items = cart?.items ?? [];

  async function changeQty(productId: string, quantity: number) {
    try {
      await setCartQuantity(productId, quantity);
      await refreshShop();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Не удалось обновить корзину");
    }
  }

  async function onCheckout() {
    setBusy(true);
    setError("");
    setMessage("");
    try {
      const result = await checkout();
      await refreshShop();
      setMessage(`Оформлено заявок: ${result.total_orders}`);
      navigate(paths.orders);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Не удалось оформить");
    } finally {
      setBusy(false);
    }
  }

  if (items.length === 0) {
    return (
      <div className="card empty">
        <p>Корзина пустая</p>
        <p>
          <Link to={paths.catalog}>В каталог</Link>
        </p>
      </div>
    );
  }

  return (
    <>
      <div className="page-head">
        <h1>Корзина</h1>
        <button
          type="button"
          className="btn btn--danger"
          onClick={() =>
            void clearCart()
              .then(refreshShop)
              .catch((err: unknown) =>
                setError(err instanceof ApiError ? err.message : "Не удалось очистить"),
              )
          }
        >
          Очистить
        </button>
      </div>
      {error ? <p className="error">{error}</p> : null}
      {message ? <p className="ok">{message}</p> : null}
      {cart?.has_unavailable_items ? (
        <p className="error">Часть позиций недоступна в нужном количестве</p>
      ) : null}
      <div className="list" style={{ marginTop: 16 }}>
        {items.map((item) => (
          <article key={item.product_id} className="card row">
            <div className="row__main">
              {item.product ? (
                <Link to={paths.product(item.product_id)}>{item.product.name}</Link>
              ) : (
                <span>Товар недоступен</span>
              )}
              <span className="muted">
                {item.is_available
                  ? `Сумма: ${formatPrice(item.subtotal)}`
                  : `Доступно: ${item.available_stock}`}
              </span>
            </div>
            <div className="row__actions">
              <input
                className="qty"
                type="number"
                min={1}
                value={item.quantity}
                onChange={(event) => {
                  const value = Number(event.target.value);
                  if (Number.isFinite(value) && value >= 1) {
                    void changeQty(item.product_id, value);
                  }
                }}
              />
              <button
                type="button"
                className="btn btn--danger"
                onClick={() => void removeCartItem(item.product_id).then(refreshShop)}
              >
                Удалить
              </button>
            </div>
          </article>
        ))}
      </div>
      <div className="card row" style={{ marginTop: 16 }}>
        <div className="price">Итого: {formatPrice(cart?.total_amount ?? "0")}</div>
        <button
          type="button"
          className="btn btn--primary"
          disabled={busy || Boolean(cart?.has_unavailable_items)}
          onClick={() => void onCheckout()}
        >
          {busy ? "Оформляем…" : "Оформить"}
        </button>
      </div>
    </>
  );
}
