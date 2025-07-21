import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import { ReactKeycloakProvider } from '@react-keycloak/web';
import keycloak from './keycloak';
import LandingPage from './pages/LandingPage';
import TenantApp from './app/TenantApp';

function App() {
  return (
    <ReactKeycloakProvider authClient={keycloak}>
      <Router>
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/app/*" element={<TenantApp />} />
        </Routes>
      </Router>
    </ReactKeycloakProvider>
  );
}

export default App;