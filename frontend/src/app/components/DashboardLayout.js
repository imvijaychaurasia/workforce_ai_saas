import React from 'react';
import { Link, Outlet } from 'react-router-dom';

const DashboardLayout = () => {
  return (
    <div style={{ display: 'flex' }}>
      <nav style={{ width: '200px', borderRight: '1px solid #ccc', padding: '1rem' }}>
        <h3>Dashboard</h3>
        <ul>
          <li><Link to="home">Home</Link></li>
          <li><Link to="account">Account</Link></li>
          <li><Link to="billing">Billing</Link></li>
          <li><Link to="users">Users</Link></li>
          <li><Link to="modules">Modules</Link></li>
          <li><Link to="providers">Providers</Link></li>
          <li><Link to="workflows">Workflows</Link></li>
          <li><Link to="logs">Logs</Link></li>
          <li><Link to="tasks">Tasks</Link></li>
        </ul>
      </nav>
      <main style={{ flex: 1, padding: '1rem' }}>
        <Outlet />
      </main>
    </div>
  );
};

export default DashboardLayout;