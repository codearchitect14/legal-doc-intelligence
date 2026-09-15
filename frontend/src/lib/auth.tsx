import { createContext, useContext, useEffect, useState, type ReactNode } from "react";

import { authApi, type Schemas } from "./apiClient";

interface AuthContextValue {
  user: Schemas["UserOut"] | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  registerFirm: (payload: Schemas["FirmRegisterRequest"]) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<Schemas["UserOut"] | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      const restored = await authApi.restoreSession();
      if (restored) {
        try {
          setUser(await authApi.me());
        } catch {
          setUser(null);
        }
      }
      setLoading(false);
    })();
  }, []);

  async function login(email: string, password: string) {
    await authApi.login(email, password);
    setUser(await authApi.me());
  }

  async function registerFirm(payload: Schemas["FirmRegisterRequest"]) {
    await authApi.registerFirm(payload);
    await login(payload.admin_email, payload.admin_password);
  }

  function logout() {
    authApi.logout();
    setUser(null);
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, registerFirm, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within an AuthProvider");
  return ctx;
}
