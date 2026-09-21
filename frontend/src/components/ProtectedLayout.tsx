import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";
import { Header } from "./Header";

export function ProtectedLayout() {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="page page--auth">
        <p className="muted">Загрузка…</p>
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  return (
    <div className="page">
      <Header />
      <main className="content">
        <Outlet />
      </main>
    </div>
  );
}
