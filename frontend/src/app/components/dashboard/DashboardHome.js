import React, { useState, useEffect } from 'react';
import { useKeycloak } from '@react-keycloak/web';

const cardStyle = {
  border: '1px solid #ccc',
  borderRadius: '8px',
  padding: '16px',
  margin: '16px',
  textAlign: 'center',
  width: '200px',
  boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
};

const cardContainerStyle = {
  display: 'flex',
  flexWrap: 'wrap',
  justifyContent: 'center',
};

const DashboardHome = () => {
  const { keycloak } = useKeycloak();
  const [username, setUsername] = useState('user');

  useEffect(() => {
    if (keycloak.authenticated && keycloak.tokenParsed) {
      setUsername(keycloak.tokenParsed.preferred_username);
    }
  }, [keycloak.authenticated, keycloak.tokenParsed]);

  return (
    <div>
      <h2>Welcome, {username}!</h2>
      <p>This is your dashboard. Here you can get a quick overview of your platform's status.</p>
      
      <div style={cardContainerStyle}>
        <div style={cardStyle}>
          <h3>Active Modules</h3>
          <p>5</p>
        </div>
        <div style={cardStyle}>
          <h3>Configured Providers</h3>
          <p>3</p>
        </div>
        <div style={cardStyle}>
          <h3>Users</h3>
          <p>12</p>
        </div>
        <div style={cardStyle}>
          <h3>Recent Activity</h3>
          <p>User 'admin' logged in.</p>
        </div>
      </div>
    </div>
  );
};

export default DashboardHome;