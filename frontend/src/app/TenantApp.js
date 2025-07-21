import React from 'react';
import { Route, Routes, Navigate } from 'react-router-dom';
import { ReactKeycloakProvider } from '@react-keycloak/web';
import keycloak from '../keycloak';
import PrivateRoute from '../components/PrivateRoute';
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import DashboardHome from './components/dashboard/DashboardHome';
import AccountManagement from './components/dashboard/AccountManagement';
import BillingManagement from './components/dashboard/BillingManagement';
import UserManagement from './components/dashboard/UserManagement';
import ModuleManagement from './components/dashboard/ModuleManagement';
import ProviderManagement from './components/dashboard/ProviderManagement';
import WorkflowManagement from './components/dashboard/WorkflowManagement';
import Logs from './components/dashboard/Logs';
import Tasks from './components/dashboard/Tasks';

function TenantApp() {
  return (
    <ReactKeycloakProvider authClient={keycloak}>
      <Routes>
        <Route path="login" element={<LoginPage />} />
        <Route
          path="dashboard/*"
          element={
            <PrivateRoute>
              <DashboardPage />
            </PrivateRoute>
          }
        >
          <Route index element={<Navigate to="home" replace />} />
          <Route path="home" element={<DashboardHome />} />
          <Route path="account" element={<AccountManagement />} />
          <Route path="billing" element={<BillingManagement />} />
          <Route path="users" element={<UserManagement />} />
          <Route path="modules" element={<ModuleManagement />} />
          <Route path="providers" element={<ProviderManagement />} />
          <Route path="workflows" element={<WorkflowManagement />} />
          <Route path="logs" element={<Logs />} />
          <Route path="tasks" element={<Tasks />} />
        </Route>
        <Route path="*" element={<Navigate to="dashboard" />} />
      </Routes>
    </ReactKeycloakProvider>
  );
}

export default TenantApp;