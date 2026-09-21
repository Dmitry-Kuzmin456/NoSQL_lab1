import { Navigate, Outlet } from "react-router-dom";
import type { UserRole } from "../api/types";
import { useAuth } from "../auth/AuthContext";
import { homePath } from "../routing";

export function RoleLayout({ role }: { role: UserRole }) {
  const { user } = useAuth();
  if (!user) {
    return <Navigate to="/login" replace />;
  }
  if (user.role !== role) {
    return <Navigate to={homePath(user.role)} replace />;
  }
  return <Outlet />;
}
