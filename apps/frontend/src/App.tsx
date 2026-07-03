import { Routes, Route, Navigate } from "react-router-dom";
import { useAuthStore } from "@/lib/store/auth.store";

// Páginas auth
import LoginPage       from "@/pages/auth/LoginPage";
import SignupPage      from "@/pages/auth/SignupPage";
import CompleteProfilePage from "@/pages/auth/CompleteProfilePage";

// Páginas dashboard
import DashboardPage   from "@/pages/dashboard/DashboardPage";
import DocumentsPage   from "@/pages/dashboard/DocumentsPage";
import ProfilePage     from "@/pages/dashboard/ProfilePage";
import AiInsightsPage  from "@/pages/dashboard/AiInsightsPage";

// Portal médico (público)
import SharePage       from "@/pages/share/SharePage";

// Layout
import DashboardLayout from "@/components/layout/DashboardLayout";

function PrivateRoute({ children }: { children: React.ReactNode }) {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" replace />;
}

export default function App() {
  return (
    <Routes>
      {/* Rutas públicas */}
      <Route path="/login"  element={<LoginPage />} />
      <Route path="/signup" element={<SignupPage />} />
      <Route path="/complete-profile" element={<CompleteProfilePage />} />
      <Route path="/share/:token" element={<SharePage />} />

      {/* Rutas protegidas */}
      <Route
        path="/"
        element={
          <PrivateRoute>
            <DashboardLayout />
          </PrivateRoute>
        }
      >
        <Route index element={<DashboardPage />} />
        <Route path="documents"  element={<DocumentsPage />} />
        <Route path="profile"    element={<ProfilePage />} />
        <Route path="ai-insights" element={<AiInsightsPage />} />
      </Route>

      {/* Fallback */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
