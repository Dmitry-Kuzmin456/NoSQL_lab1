import { useState } from "react";
import { Link } from "react-router-dom";
import { removeFavourite, setCartQuantity, clearFavourites } from "../api/shop";
import { ApiError } from "../api/client";
import { useAuth } from "../auth/AuthContext";
import { formatPrice } from "../lib/format";
import { usePaths } from "../routing";

export function FavouritesPage() {
  const { favourites, cartIds, refreshShop } = useAuth();
  const paths = usePaths();
  const [error, setError] = useState("");
  const products = favourites?.products ?? [];

  async function remove(productId: string) {
    try {
      await removeFavourite(productId);
      await refreshShop();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Не удалось удалить");
    }
  }

  async function toCart(productId: string) {
    try {
      if (!cartIds.has(productId)) {
        await setCartQuantity(productId, 1);
        await refreshShop();
      }
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Не удалось добавить в корзину");
    }
  }

  if (products.length === 0) {
    return (
      <div className="card empty">
        <p>В избранном пока пусто</p>
        <p>
          <Link to={paths.catalog}>В каталог</Link>
        </p>
      </div>
    );
  }

  return (
    <>
      <div className="page-head">
        <h1>Избранное</h1>
        <button
          type="button"
          className="btn btn--danger"
          onClick={() =>
            void clearFavourites()
              .then(refreshShop)
              .catch((err: unknown) =>
                setError(err instanceof ApiError ? err.message : "Не удалось очистить"),
              )
          }
        >
          Очистить всё
        </button>
      </div>
      {error ? <p className="error">{error}</p> : null}
      <div className="list" style={{ marginTop: 16 }}>
        {products.map((item) => (
          <article key={item.product_id} className="card row">
            <div className="row__main">
              {item.product ? (
                <Link to={paths.product(item.product_id)}>{item.product.name}</Link>
              ) : (
                <span>Товар недоступен</span>
              )}
              {item.product ? (
                <span className="price">{formatPrice(item.product.price)}</span>
              ) : null}
              {item.added_user_id !== favourites?.user_id ? (
                <span className="muted">добавил преподаватель</span>
              ) : null}
            </div>
            <div className="row__actions">
              <button
                type="button"
                className="btn btn--primary"
                disabled={!item.product?.is_in_stock}
                onClick={() => void toCart(item.product_id)}
              >
                {cartIds.has(item.product_id) ? "В корзине" : "В корзину"}
              </button>
              <button
                type="button"
                className="btn btn--danger"
                onClick={() => void remove(item.product_id)}
              >
                Убрать
              </button>
            </div>
          </article>
        ))}
      </div>
    </>
  );
}
