import React, { useEffect, useState } from 'react';
import { useKeycloak } from '@react-keycloak/web';

const AccountManagement = () => {
  const { keycloak } = useKeycloak();
  const [userInfo, setUserInfo] = useState(null);

  useEffect(() => {
    if (keycloak.authenticated) {
      keycloak.loadUserInfo().then(setUserInfo);
    }
  }, [keycloak, keycloak.authenticated]);

  const redirectToAccountManagement = () => {
    const accountManagementUrl = `${keycloak.authServerUrl}/realms/${keycloak.realm}/account`;
    window.open(accountManagementUrl, '_blank');
  };

  return (
    <div>
      <h2>Account Management</h2>
      {userInfo ? (
        <div>
          <p><strong>Username:</strong> {userInfo.preferred_username}</p>
          <p><strong>Email:</strong> {userInfo.email}</p>
          <p><strong>First Name:</strong> {userInfo.given_name}</p>
          <p><strong>Last Name:</strong> {userInfo.family_name}</p>
          <button onClick={redirectToAccountManagement}>
            Manage Account
          </button>
        </div>
      ) : (
        <p>Loading user information...</p>
      )}
    </div>
  );
};

export default AccountManagement;