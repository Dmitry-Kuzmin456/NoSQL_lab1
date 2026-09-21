import { FormEvent, useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { ApiError } from "../api/client";
import type { UserRole } from "../api/types";
import { useAuth } from "../auth/AuthContext";
import { homePath } from "../routing";

export function RegisterPage() {
  const { user, register } = useAuth();
  const navigate = useNavigate();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState<UserRole>("STUDENT");
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
      const next = await register(name, email, password, role);
      navigate(homePath(next.role), { replace: true });
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Не удалось зарегистрироваться");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="page page--auth">
      <form className="card auth-card" onSubmit={onSubmit}>
        <div className="brand">Витрина</div>
        <h1>Регистрация</h1>
        {error ? <p className="error">{error}</p> : null}
        <label className="field">
          <span>Имя</span>
          <input
            required
            minLength={2}
            value={name}
            onChange={(event) => setName(event.target.value)}
          />
        </label>
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
            autoComplete="new-password"
            required
            minLength={6}
            value={password}
            onChange={(event) => setPassword(event.target.value)}
          />
        </label>
        <label className="field">
          <span>Роль</span>
          <select value={role} onChange={(event) => setRole(event.target.value as UserRole)}>
            <option value="STUDENT">Ученик</option>
            <option value="TEACHER">Преподаватель</option>
            <option value="ADMIN">Админ</option>
          </select>
        </label>
        <button className="btn btn--primary btn--wide" type="submit" disabled={submitting}>
          {submitting ? "Создаём…" : "Создать аккаунт"}
        </button>
        <div className="auth-links">
          <Link to="/login">Уже есть вход</Link>
        </div>
      </form>
    </div>
  );
}
