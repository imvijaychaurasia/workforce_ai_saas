import React, { useState, useEffect } from 'react';
import keycloak from '../../../keycloak';

const ProviderManagement = () => {
  const [providers, setProviders] = useState([]);
  const [providerName, setProviderName] = useState('');
  const [providerConfig, setProviderConfig] = useState('');

  const fetchProviders = async () => {
    try {
      const response = await fetch('/providers', {
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${keycloak.token}`,
          'X-Tenant-ID': keycloak.realm,
        },
      });
      const data = await response.json();
      setProviders(data);
    } catch (error) {
      console.error('Error fetching providers:', error);
    }
  };

  useEffect(() => {
    fetchProviders();
  }, []);

  const handleAddProvider = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch('/providers', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${keycloak.token}`,
          'X-Tenant-ID': keycloak.realm,
        },
        body: JSON.stringify({
          name: providerName,
          config: JSON.parse(providerConfig),
        }),
      });
      if (response.ok) {
        setProviderName('');
        setProviderConfig('');
        fetchProviders();
      } else {
        console.error('Error adding provider:', response.statusText);
      }
    } catch (error) {
      console.error('Error adding provider:', error);
    }
  };

  return (
    <div>
      <h2>Provider Management</h2>
      <div>
        <h3>Configured Providers</h3>
        <ul>
          {providers.map((provider) => (
            <li key={provider.id}>{provider.name}</li>
          ))}
        </ul>
      </div>
      <div>
        <h3>Add New Provider</h3>
        <form onSubmit={handleAddProvider}>
          <div>
            <label>Provider Name:</label>
            <input
              type="text"
              value={providerName}
              onChange={(e) => setProviderName(e.target.value)}
              required
            />
          </div>
          <div>
            <label>Configuration (JSON):</label>
            <textarea
              value={providerConfig}
              onChange={(e) => setProviderConfig(e.target.value)}
              required
            />
          </div>
          <button type="submit">Add Provider</button>
        </form>
      </div>
    </div>
  );
};

export default ProviderManagement;