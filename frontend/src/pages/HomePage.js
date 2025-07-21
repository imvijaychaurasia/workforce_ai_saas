import React from 'react';
import { useKeycloak } from '@react-keycloak/web';

const HomePage = () => {
  const { keycloak } = useKeycloak();

  return (
    <div>
      <header style={{ display: 'flex', justifyContent: 'space-between', padding: '1rem', borderBottom: '1px solid #ccc' }}>
        <h1>SaaS AI Platform</h1>
        {!keycloak.authenticated && (
          <button onClick={() => keycloak.login()}>
            Tenant Sign In
          </button>
        )}
        {keycloak.authenticated && (
          <button onClick={() => keycloak.logout()}>
            Logout ({keycloak.tokenParsed.preferred_username})
          </button>
        )}
      </header>
      <main style={{ padding: '1rem' }}>
        <h2>Automate Your Business with the Power of AI</h2>
        <p>
          Our platform provides a suite of AI-powered tools and services to help you streamline operations,
          gain insights from your data, and drive growth.
        </p>
        <h3>Our Services</h3>
        <ul>
          <li>Automated Security Scanning with Nmap and Semgrep</li>
          <li>Workflow Automation with n8n</li>
          <li>Document Analysis and Q&A with local and cloud-based AI</li>
          <li>And much more...</li>
        </ul>
      </main>
    </div>
  );
};

export default HomePage;