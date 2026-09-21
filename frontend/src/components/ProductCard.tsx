import { Link } from "react-router-dom";
import type { Product } from "../api/types";
import { formatPrice } from "../lib/format";
import { usePaths } from "../routing";

type Props = {
  product: Product;
  inFavourites: boolean;
  inCart: boolean;
  busy?: boolean;
  onFavourite: () => void;
  onCart: () => void;
};

export function ProductCard({
  product,
  inFavourites,
  inCart,
  busy,
  onFavourite,
  onCart,
}: Props) {
  const paths = usePaths();
  const href = paths.product(product.id);
  return (
    <article className="card product-card">
      <div className="product-card__body">
        <h2>
          <Link to={href}>{product.name}</Link>
        </h2>
        <div className="price">{formatPrice(product.price)}</div>
        <div className={product.is_in_stock ? "stock" : "stock stock--out"}>
          {product.is_in_stock ? `В наличии: ${product.quantity}` : "Нет в наличии"}
        </div>
        <div className="product-card__actions">
          <button
            type="button"
            className={inFavourites ? "btn btn--ghost" : "btn btn--ghost"}
            disabled={busy}
            onClick={onFavourite}
          >
            {inFavourites ? "В избранном" : "В избранное"}
          </button>
          <button
            type="button"
            className="btn btn--primary"
            disabled={busy || !product.is_in_stock}
            onClick={onCart}
          >
            {inCart ? "В корзине" : "В корзину"}
          </button>
        </div>
      </div>
    </article>
  );
}
