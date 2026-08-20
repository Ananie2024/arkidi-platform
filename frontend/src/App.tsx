import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider } from './core/auth/AuthContext';
import { ProtectedRoute } from './core/auth/ProtectedRoute';
import { AppLayout } from './components/layout/AppLayout';
import { DashboardPage } from './modules/dashboard/DashboardPage';
import { GeographyPage } from './modules/geography/GeographyPage';
import { ParishListPage } from './modules/geography/ParishListPage';
import { ParishDetailPage } from './modules/geography/ParishDetailPage';
import { FaithfulListPage } from './modules/faithful/FaithfulListPage';
import { FaithfulDetailPage } from './modules/faithful/FaithfulDetailPage';
import { SacramentsOverviewPage } from './modules/sacraments/SacramentsOverviewPage';
import { BaptismRegisterPage } from './modules/sacraments/BaptismRegisterPage';
import { ConfirmationRegisterPage } from './modules/sacraments/ConfirmationRegisterPage';
import { MatrimonyRegisterPage } from './modules/sacraments/MatrimonyRegisterPage';
import { ClergyListPage } from './modules/clergy/ClergyListPage';
import { ClergyDetailPage } from './modules/clergy/ClergyDetailPage';
import { LiturgyPage } from './modules/liturgy/LiturgyPage';
import { FinancePage } from './modules/finance/FinancePage';
import { MinistriesPage } from './modules/ministries/MinistriesPage';
import { LandAssetsPage } from './modules/land_assets/LandAssetsPage';
import { ArchivePage } from './modules/archive/ArchivePage';
import { StatisticsPage } from './modules/statistics/StatisticsPage';
import { LoginPage } from './modules/auth/LoginPage';
import { ForgotPasswordPage } from './modules/auth/ForgotPasswordPage';
import { UnauthorizedPage } from './pages/UnauthorizedPage';
import { NotFoundPage } from './pages/NotFoundPage';

const queryClient = new QueryClient();

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <AuthProvider>
          <Routes>
            {/* Public routes */}
            <Route path="/login" element={<LoginPage />} />
            <Route path="/forgot-password" element={<ForgotPasswordPage />} />

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
        </AuthProvider>
      </BrowserRouter>
    </QueryClientProvider>
  );
};