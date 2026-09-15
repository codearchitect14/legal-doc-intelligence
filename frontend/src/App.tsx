import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";

import { AppLayout } from "./components/AppLayout";
import { ProtectedRoute } from "./components/ProtectedRoute";
import { PublicLayout } from "./components/PublicLayout";
import { AuthProvider } from "./lib/auth";
import { Login } from "./pages/auth/Login";
import { Register } from "./pages/auth/Register";
import { CaseDetail } from "./pages/app/CaseDetail";
import { Dashboard } from "./pages/app/Dashboard";
import { Settings } from "./pages/app/Settings";
import { Demo } from "./pages/marketing/Demo";
import { Home } from "./pages/marketing/Home";
import { Pricing } from "./pages/marketing/Pricing";
import { Product } from "./pages/marketing/Product";
import { Security } from "./pages/marketing/Security";
import { Solutions } from "./pages/marketing/Solutions";

export function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route element={<PublicLayout />}>
            <Route path="/" element={<Home />} />
            <Route path="/product" element={<Product />} />
            <Route path="/solutions" element={<Solutions />} />
            <Route path="/security" element={<Security />} />
            <Route path="/pricing" element={<Pricing />} />
            <Route path="/demo" element={<Demo />} />
          </Route>

          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />

          <Route element={<ProtectedRoute />}>
            <Route element={<AppLayout />}>
              <Route path="/app" element={<Dashboard />} />
              <Route path="/app/cases/:caseId" element={<CaseDetail />} />
              <Route path="/app/settings" element={<Settings />} />
            </Route>
          </Route>

          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}
