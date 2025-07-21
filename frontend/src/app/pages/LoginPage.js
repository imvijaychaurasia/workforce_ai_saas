import React from 'react';
import { useKeycloak } from '@react-keycloak/web';

const LoginPage = () => {
  const { keycloak } = useKeycloak();

  return (
    <div>
      <h2>Tenant Login</h2>
      <button onClick={() => keycloak.login()}>Login with Keycloak</button>
    </div>
  );
};

export default LoginPage;