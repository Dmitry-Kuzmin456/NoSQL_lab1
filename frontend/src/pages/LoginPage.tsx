import { FormEvent, useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { ApiError } from "../api/client";
import { useAuth } from "../auth/AuthContext";
import { homePath } from "../routing";

export function LoginPage() {
  const { user, login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (user) navigate(homePath(user.role), { replace: true });
  }, [user, navigate]);

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      const next = await login(email, password);
      navigate(homePath(next.role), { replace: true });
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Не удалось войти");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="page page--auth">
      <form className="card auth-card" onSubmit={onSubmit}>
        <div className="brand">Лавка</div>
        <h1>Вход</h1>
        {error ? <p className="error">{error}</p> : null}
        <label className="field">
          <span>Email</span>
          <input
            type="email"
            autoComplete="email"
            required
            value={email}
            onChange={(event) => setEmail(event.target.value)}
          />
        </label>
        <label className="field">
          <span>Пароль</span>
          <input
            type="password"
            autoComplete="current-password"
            required
            minLength={1}
            value={password}
            onChange={(event) => setPassword(event.target.value)}
          />
        </label>
        <button className="btn btn--primary btn--wide" type="submit" disabled={submitting}>
          {submitting ? "Входим…" : "Войти"}
        </button>
        <div className="auth-links">
          <Link to="/register">Регистрация</Link>
          <Link to="/recovery">Забыли пароль</Link>
        </div>
      </form>
    </div>
  );
}
