import { FormEvent, useEffect, useState } from "react";
import { ApiError } from "../api/client";
import {
  createProduct,
  deleteProduct,
  listProducts,
  reserveStock,
  restoreStock,
  updateProduct,
} from "../api/products";
import type { Product } from "../api/types";
import { formatPrice } from "../lib/format";

export function AdminProductsPage() {
  const [items, setItems] = useState<Product[]>([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [price, setPrice] = useState("");
  const [quantity, setQuantity] = useState("0");

  async function load() {
    setLoading(true);
    try {
      const result = await listProducts({ limit: 50, sort_by: "name_asc" });
      setItems(result.items);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Не удалось загрузить товары");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void load();
  }, []);

  async function onCreate(event: FormEvent) {
    event.preventDefault();
    setError("");
    try {
      await createProduct({
        name,
        description,
        price,
        quantity: Number(quantity) || 0,
      });
      setName("");
      setDescription("");
      setPrice("");
      setQuantity("0");
      await load();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Не удалось создать товар");
    }
  }

  async function onSave(product: Product) {
    try {
      await updateProduct(product.id, {
        name: product.name,
        description: product.description,
        price: product.price,
        quantity: product.quantity,
      });
      await load();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Не удалось сохранить");
    }
  }

  async function onDelete(productId: string) {
    try {
      await deleteProduct(productId);
      await load();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Не удалось удалить");
    }
  }

  function patch(id: string, patchValue: Partial<Product>) {
    setItems((current) =>
      current.map((item) => (item.id === id ? { ...item, ...patchValue } : item)),
    );
  }

  return (
    <>
      <h1>Товары</h1>
      {error ? <p className="error">{error}</p> : null}
      <form className="card profile" onSubmit={onCreate} style={{ width: "100%", marginBottom: 20 }}>
        <h2>Новый товар</h2>
        <label className="field" style={{ marginTop: 12 }}>
          <span>Название</span>
          <input required value={name} onChange={(event) => setName(event.target.value)} />
        </label>
        <label className="field">
          <span>Описание</span>
          <input value={description} onChange={(event) => setDescription(event.target.value)} />
        </label>
        <label className="field">
          <span>Цена</span>
          <input required value={price} onChange={(event) => setPrice(event.target.value)} />
        </label>
        <label className="field">
          <span>Остаток</span>
          <input
            type="number"
            min={0}
            value={quantity}
            onChange={(event) => setQuantity(event.target.value)}
          />
        </label>
        <button className="btn btn--primary" type="submit">
          Создать
        </button>
      </form>
      {loading ? <div className="skeleton" /> : null}
      <div className="list">
        {items.map((product) => (
          <article key={product.id} className="card" style={{ padding: 16 }}>
            <div className="row" style={{ padding: 0 }}>
              <div className="row__main">
                <input
                  value={product.name}
                  onChange={(event) => patch(product.id, { name: event.target.value })}
                />
                <span className="muted">{formatPrice(product.price)} · {product.id}</span>
              </div>
              <div className="row__actions">
                <button type="button" className="btn btn--ghost" onClick={() => void onSave(product)}>
                  Сохранить
                </button>
                <button type="button" className="btn btn--danger" onClick={() => void onDelete(product.id)}>
                  Удалить
                </button>
              </div>
            </div>
            <div className="row" style={{ padding: "12px 0 0" }}>
              <input
                value={product.description}
                onChange={(event) => patch(product.id, { description: event.target.value })}
              />
              <div className="row__actions">
                <input
                  className="qty"
                  value={product.price}
                  onChange={(event) => patch(product.id, { price: event.target.value })}
                />
                <span className="muted">ост. {product.quantity}</span>
                <button
                  type="button"
                  className="btn btn--ghost"
                  onClick={() => void reserveStock(product.id, 1).then(load)}
                >
                  −1
                </button>
                <button
                  type="button"
                  className="btn btn--ghost"
                  onClick={() => void restoreStock(product.id, 1).then(load)}
                >
                  +1
                </button>
              </div>
            </div>
          </article>
        ))}
      </div>
    </>
  );
}
