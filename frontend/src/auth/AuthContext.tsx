import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import { getMe, login as loginRequest, logout as logoutRequest, register as registerRequest } from "../api/auth";
import { ApiError } from "../api/client";
import { getCart, getFavourites } from "../api/shop";
import type { Cart, Favourites, User, UserRole } from "../api/types";

type AuthContextValue = {
  user: User | null;
  loading: boolean;
  cart: Cart | null;
  favourites: Favourites | null;
  favouriteIds: Set<string>;
  cartIds: Set<string>;
  login: (email: string, password: string) => Promise<User>;
  register: (name: string, email: string, password: string, role?: UserRole) => Promise<User>;
  logout: () => Promise<void>;
  refreshShop: () => Promise<void>;
  setUser: (user: User) => void;
};

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [cart, setCart] = useState<Cart | null>(null);
  const [favourites, setFavourites] = useState<Favourites | null>(null);

  const refreshShop = useCallback(async () => {
    const [nextCart, nextFavourites] = await Promise.all([getCart(), getFavourites()]);
    setCart(nextCart);
    setFavourites(nextFavourites);
  }, []);

  const syncSession = useCallback(async () => {
    try {
      const me = await getMe();
      setUser(me);
      try {
        await refreshShop();
      } catch (error) {
        console.error(error);
      }
      return me;
    } catch (error) {
      if (!(error instanceof ApiError && error.status === 401)) {
        console.error(error);
      }
      setUser(null);
      setCart(null);
      setFavourites(null);
      return null;
    }
  }, [refreshShop]);

  useEffect(() => {
    let alive = true;
    (async () => {
      try {
        await syncSession();
      } finally {
        if (alive) setLoading(false);
      }
    })();
    return () => {
      alive = false;
    };
  }, [syncSession]);

  useEffect(() => {
    function onFocus() {
      if (document.visibilityState === "visible") {
        void syncSession();
      }
    }
    window.addEventListener("focus", onFocus);
    document.addEventListener("visibilitychange", onFocus);
    return () => {
      window.removeEventListener("focus", onFocus);
      document.removeEventListener("visibilitychange", onFocus);
    };
  }, [syncSession]);

  const login = useCallback(
    async (email: string, password: string) => {
      const next = await loginRequest(email, password);
      setUser(next);
      await refreshShop();
      return next;
    },
    [refreshShop],
  );

  const register = useCallback(
    async (name: string, email: string, password: string, role: UserRole = "STUDENT") => {
      await registerRequest(name, email, password, role);
      return login(email, password);
    },
    [login],
  );

  const logout = useCallback(async () => {
    try {
      await logoutRequest();
    } finally {
      setUser(null);
      setCart(null);
      setFavourites(null);
    }
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      loading,
      cart,
      favourites,
      favouriteIds: new Set(favourites?.products.map((item) => item.product_id) ?? []),
      cartIds: new Set(cart?.items.map((item) => item.product_id) ?? []),
      login,
      register,
      logout,
      refreshShop,
      setUser,
    }),
    [user, loading, cart, favourites, login, register, logout, refreshShop],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
}
