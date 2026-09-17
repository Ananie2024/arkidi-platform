import React, { lazy, Suspense } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider } from './core/auth/AuthContext';
import { ProtectedRoute } from './core/auth/ProtectedRoute';
import { AppLayout } from './components/layout/AppLayout';
import { LoadingSpinner } from './components/common/LoadingSpinner';

// ---------------------------------------------------------------------------
// Route-level code splitting.
// Each page module uses *named* exports, so we adapt the namespace to the
// `.default` shape that React.lazy requires. Vite emits one async chunk per
// dynamic import, which keeps the initial bundle small and removes the
// bundle-size warning from large chart/GIS/QR dependencies.
// ---------------------------------------------------------------------------
const HomePage = lazy(() =>
  import('./pages/HomePage').then((m) => ({ default: m.HomePage }))
);
const LoginPage = lazy(() =>
  import('./modules/auth/LoginPage').then((m) => ({ default: m.LoginPage }))
);
const ForgotPasswordPage = lazy(() =>
  import('./modules/auth/ForgotPasswordPage').then((m) => ({ default: m.ForgotPasswordPage }))
);
const ResetPasswordPage = lazy(() =>
  import('./modules/auth/ResetPasswordPage').then((m) => ({ default: m.ResetPasswordPage }))
);
const DashboardPage = lazy(() =>
  import('./modules/dashboard/DashboardPage').then((m) => ({ default: m.DashboardPage }))
);
const GeographyPage = lazy(() =>
  import('./modules/geography/GeographyPage').then((m) => ({ default: m.GeographyPage }))
);
const ParishListPage = lazy(() =>
  import('./modules/geography/ParishListPage').then((m) => ({ default: m.ParishListPage }))
);
const ParishDetailPage = lazy(() =>
  import('./modules/geography/ParishDetailPage').then((m) => ({ default: m.ParishDetailPage }))
);
const FaithfulListPage = lazy(() =>
  import('./modules/faithful/FaithfulListPage').then((m) => ({ default: m.FaithfulListPage }))
);
const FaithfulDetailPage = lazy(() =>
  import('./modules/faithful/FaithfulDetailPage').then((m) => ({ default: m.FaithfulDetailPage }))
);
const SacramentsOverviewPage = lazy(() =>
  import('./modules/sacraments/SacramentsOverviewPage').then((m) => ({ default: m.SacramentsOverviewPage }))
);
const BaptismRegisterPage = lazy(() =>
  import('./modules/sacraments/BaptismRegisterPage').then((m) => ({ default: m.BaptismRegisterPage }))
);
const ConfirmationRegisterPage = lazy(() =>
  import('./modules/sacraments/ConfirmationRegisterPage').then((m) => ({ default: m.ConfirmationRegisterPage }))
);
const MatrimonyRegisterPage = lazy(() =>
  import('./modules/sacraments/MatrimonyRegisterPage').then((m) => ({ default: m.MatrimonyRegisterPage }))
);
const ClergyListPage = lazy(() =>
  import('./modules/clergy/ClergyListPage').then((m) => ({ default: m.ClergyListPage }))
);
const ClergyDetailPage = lazy(() =>
  import('./modules/clergy/ClergyDetailPage').then((m) => ({ default: m.ClergyDetailPage }))
);
const LiturgyPage = lazy(() =>
  import('./modules/liturgy/LiturgyPage').then((m) => ({ default: m.LiturgyPage }))
);
const FinancePage = lazy(() =>
  import('./modules/finance/FinancePage').then((m) => ({ default: m.FinancePage }))
);
const MinistriesPage = lazy(() =>
  import('./modules/ministries/MinistriesPage').then((m) => ({ default: m.MinistriesPage }))
);
const LandAssetsPage = lazy(() =>
  import('./modules/land_assets/LandAssetsPage').then((m) => ({ default: m.LandAssetsPage }))
);
const ArchivePage = lazy(() =>
  import('./modules/archive/ArchivePage').then((m) => ({ default: m.ArchivePage }))
);
const StatisticsPage = lazy(() =>
  import('./modules/statistics/StatisticsPage').then((m) => ({ default: m.StatisticsPage }))
);
const UnauthorizedPage = lazy(() =>
  import('./pages/UnauthorizedPage').then((m) => ({ default: m.UnauthorizedPage }))
);
const NotFoundPage = lazy(() =>
  import('./pages/NotFoundPage').then((m) => ({ default: m.NotFoundPage }))
);

const queryClient = new QueryClient();

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <AuthProvider>
          <Suspense fallback={<LoadingSpinner className="min-h-screen" />}>
            <Routes>
              {/* Public routes */}
              <Route path="/" element={<HomePage />} />
              <Route path="/login" element={<LoginPage />} />
              <Route path="/forgot-password" element={<ForgotPasswordPage />} />
              <Route path="/reset-password" element={<ResetPasswordPage />} />

              {/* Protected routes */}
              <Route element={<ProtectedRoute />}>
                <Route element={<AppLayout />}>
                  <Route path="/dashboard" element={<DashboardPage />} />
                  <Route path="/geography" element={<GeographyPage />} />
                  <Route path="/geography/parishes" element={<ParishListPage />} />
                  <Route path="/geography/parishes/:parishId" element={<ParishDetailPage />} />
                  <Route path="/faithful" element={<FaithfulListPage />} />
                  <Route path="/faithful/:faithfulId" element={<FaithfulDetailPage />} />
                  <Route path="/sacraments" element={<SacramentsOverviewPage />} />
                  <Route path="/sacraments/baptism" element={<BaptismRegisterPage />} />
                  <Route path="/sacraments/confirmation" element={<ConfirmationRegisterPage />} />
                  <Route path="/sacraments/matrimony" element={<MatrimonyRegisterPage />} />
                  <Route path="/clergy" element={<ClergyListPage />} />
                  <Route path="/clergy/:clergyId" element={<ClergyDetailPage />} />
                  <Route path="/liturgy" element={<LiturgyPage />} />
                  <Route path="/finance" element={<FinancePage />} />
                  <Route path="/ministries" element={<MinistriesPage />} />
                  <Route path="/land-assets" element={<LandAssetsPage />} />
                  <Route path="/archive" element={<ArchivePage />} />
                  <Route path="/statistics" element={<StatisticsPage />} />
                </Route>
              </Route>

              {/* Error routes */}
              <Route path="/unauthorized" element={<UnauthorizedPage />} />
              <Route path="*" element={<NotFoundPage />} />
            </Routes>
          </Suspense>
        </AuthProvider>
      </BrowserRouter>
    </QueryClientProvider>
  );
}