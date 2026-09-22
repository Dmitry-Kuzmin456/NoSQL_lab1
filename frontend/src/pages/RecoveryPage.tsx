import { FormEvent, useState } from "react";
import { Link } from "react-router-dom";
import { ApiError } from "../api/client";
import { requestRecovery } from "../api/recovery";

export function RecoveryPage() {
  const [email, setEmail] = useState("");
  const [token, setToken] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    setError("");
    setToken("");
    setSubmitting(true);
    try {
      const result = await requestRecovery(email);
      setToken(result.token);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Не удалось запросить ссылку");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="page page--auth">
      <form className="card auth-card" onSubmit={onSubmit}>
        <div className="brand">Лавка</div>
        <h1>Восстановление</h1>
        <p className="muted" style={{ marginBottom: 16 }}>
          Почты нет — токен сразу покажем на этой странице (TTL 15 минут).
        </p>
        {error ? <p className="error">{error}</p> : null}
        <label className="field">
          <span>Email</span>
          <input
            type="email"
            required
            value={email}
            onChange={(event) => setEmail(event.target.value)}
          />
        </label>
        <button className="btn btn--primary btn--wide" type="submit" disabled={submitting}>
          {submitting ? "Отправляем…" : "Получить ссылку"}
        </button>
        {token ? (
          <p className="ok" style={{ marginTop: 16, wordBreak: "break-all" }}>
            Токен: {token}
            <br />
            <Link to={`/reset-password?token=${encodeURIComponent(token)}`}>Сменить пароль</Link>
          </p>
        ) : null}
        <div className="auth-links">
          <Link to="/login">Ко входу</Link>
        </div>
      </form>
    </div>
  );
}
