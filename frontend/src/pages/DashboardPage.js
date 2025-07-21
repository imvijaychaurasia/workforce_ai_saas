import React from 'react';
import { useKeycloak } from '@react-keycloak/web';

const DashboardPage = () => {
  const { keycloak } = useKeycloak();

  return (
    <div>
      <header style={{ display: 'flex', justifyContent: 'space-between', padding: '1rem', borderBottom: '1px solid #ccc' }}>
        <h1>SaaS AI Platform</h1>
        <button onClick={() => keycloak.logout()}>
          Logout ({keycloak.tokenParsed.preferred_username})
        </button>
      </header>
      <main style={{ padding: '1rem' }}>
        <h2>Dashboard</h2>
        <p>Welcome to your dashboard. More features coming soon!</p>
      </main>
    </div>
  );
};

export default DashboardPage;