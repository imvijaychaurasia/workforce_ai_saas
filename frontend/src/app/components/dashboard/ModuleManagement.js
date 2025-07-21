import React, { useState, useEffect, useCallback } from 'react';
import keycloak from '../../../keycloak';

const ModuleManagement = () => {
  const [modules, setModules] = useState([]);
  const [activeModules, setActiveModules] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const getTenantId = () => {
    return keycloak.tokenParsed?.tenant_id;
  };

  const fetchModules = useCallback(async () => {
    setLoading(true);
    try {
      const tenantId = getTenantId();
      if (!tenantId) {
        throw new Error("Tenant ID not found.");
      }

      const headers = {
        'Authorization': `Bearer ${keycloak.token}`,
        'X-Tenant-ID': tenantId,
      };

      const [allModulesResponse, activeModulesResponse] = await Promise.all([
        fetch('/api/modules', { headers }),
        fetch('/api/modules/active', { headers }),
      ]);

      if (!allModulesResponse.ok || !activeModulesResponse.ok) {
        throw new Error('Failed to fetch module data.');
      }

      const allModulesData = await allModulesResponse.json();
      const activeModulesData = await activeModulesResponse.json();

      setModules(allModulesData);
      setActiveModules(activeModulesData.map(m => m.name));
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchModules();
  }, [fetchModules]);

  const handleToggleModule = async (moduleName, isActive) => {
    try {
      const tenantId = getTenantId();
      const endpoint = isActive ? '/deactivate' : '/activate';
      const response = await fetch(`/api/modules${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${keycloak.token}`,
          'X-Tenant-ID': tenantId,
        },
        body: JSON.stringify({ module_name: moduleName }),
      });

      if (!response.ok) {
        throw new Error(`Failed to ${isActive ? 'deactivate' : 'activate'} module.`);
      }

      fetchModules(); // Refresh the module list
    } catch (err) {
      setError(err.message);
    }
  };

  if (loading) {
    return <div>Loading...</div>;
  }

  if (error) {
    return <div>Error: {error}</div>;
  }

  return (
    <div>
      <h2>Module Management</h2>
      <ul>
        {modules.map((module) => {
          const isActive = activeModules.includes(module.name);
          return (
            <li key={module.name}>
              <h3>{module.name}</h3>
              <p>{module.description}</p>
              <p>Status: {isActive ? 'Active' : 'Inactive'}</p>
              <button
                onClick={() => handleToggleModule(module.name, isActive)}
                disabled={loading}
              >
                {isActive ? 'Deactivate' : 'Activate'}
              </button>
            </li>
          );
        })}
      </ul>
    </div>
  );
};

export default ModuleManagement;