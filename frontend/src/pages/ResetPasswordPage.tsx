import { FormEvent, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { ApiError } from "../api/client";
import { resetPassword } from "../api/recovery";

export function ResetPasswordPage() {
  const [params] = useSearchParams();
  const [token, setToken] = useState(params.get("token") ?? "");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [submitting, setSubmitting] = useState(false);

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    setError("");
    setMessage("");
    setSubmitting(true);
    try {
      const result = await resetPassword(token, password);
      setMessage(result.message);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Не удалось сменить пароль");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="page page--auth">
      <form className="card auth-card" onSubmit={onSubmit}>
        <div className="brand">Витрина</div>
        <h1>Новый пароль</h1>
        {error ? <p className="error">{error}</p> : null}
        {message ? <p className="ok">{message}</p> : null}
        <label className="field">
          <span>Токен</span>
          <input required value={token} onChange={(event) => setToken(event.target.value)} />
        </label>
        <label className="field">
          <span>Новый пароль</span>
          <input
            type="password"
            required
            minLength={6}
            value={password}
            onChange={(event) => setPassword(event.target.value)}
          />
        </label>
        <button className="btn btn--primary btn--wide" type="submit" disabled={submitting}>
          {submitting ? "Сохраняем…" : "Сменить пароль"}
        </button>
        <div className="auth-links">
          <Link to="/login">Ко входу</Link>
        </div>
      </form>
    </div>
  );
}
