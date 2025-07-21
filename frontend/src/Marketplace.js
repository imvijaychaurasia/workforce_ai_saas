import React, { useState, useEffect } from 'react';

function Marketplace({ tenantId, token }) {
  const [modules, setModules] = useState([]);
  const [providers, setProviders] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!token) return;
    setLoading(true);
    Promise.all([
      fetch('/modules', { headers: { 'X-Tenant-ID': tenantId, 'Authorization': `Bearer ${token}` } }),
      fetch('/providers', { headers: { 'X-Tenant-ID': tenantId, 'Authorization': `Bearer ${token}` } })
    ])
      .then(([modulesRes, providersRes]) => Promise.all([modulesRes.json(), providersRes.json()]))
      .then(([modulesData, providersData]) => {
        setModules(modulesData);
        setProviders(providersData);
        setLoading(false);
      })
      .catch(err => {
        console.error("Error fetching marketplace data:", err);
        setLoading(false);
      });
  }, [tenantId, token]);

  return (
    <div>
      <h2>Marketplace</h2>
      {loading && <p>Loading...</p>}
      <h3>Modules</h3>
      <div style={{ display: 'flex', flexWrap: 'wrap' }}>
        {modules.map(module => (
          <div key={module.name} style={{ border: '1px solid #ccc', padding: '10px', margin: '10px', width: '200px' }}>
            <h4>{module.name}</h4>
            <p>{module.description}</p>
            <button>Activate</button>
          </div>
        ))}
      </div>
      <h3>Providers</h3>
      <div style={{ display: 'flex', flexWrap: 'wrap' }}>
        {providers.map(provider => (
          <div key={provider.id} style={{ border: '1px solid #ccc', padding: '10px', margin: '10px', width: '200px' }}>
            <h4>{provider.name}</h4>
            <button>Connect</button>
          </div>
        ))}
      </div>
    </div>
  );
}

export default Marketplace;