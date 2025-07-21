import React, { useState, useEffect } from 'react';

function Providers({ tenantId, token }) {
  const [providers, setProviders] = useState([]);
  const [loading, setLoading] = useState(false);
  const [newProviderName, setNewProviderName] = useState('');
  const [newProviderConfig, setNewProviderConfig] = useState('');

  const fetchProviders = () => {
    if (!token) return;
    setLoading(true);
    fetch('/providers', {
      headers: {
        'X-Tenant-ID': tenantId,
        'Authorization': `Bearer ${token}`
      }
    })
      .then(res => res.json())
      .then(data => {
        setProviders(data);
        setLoading(false);
      })
      .catch(err => {
        console.error("Error fetching providers:", err);
        setLoading(false);
      });
  };

  useEffect(() => {
    fetchProviders();
  }, [tenantId, token]);

  const createProvider = async () => {
    if (!newProviderName.trim() || !token) return;
    setLoading(true);
    try {
      const config = JSON.parse(newProviderConfig || '{}');
      await fetch('/providers', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Tenant-ID': tenantId,
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          name: newProviderName,
          config: config
        })
      });
      setNewProviderName('');
      setNewProviderConfig('');
      fetchProviders();
    } catch (error) {
      console.error("Error creating provider:", error);
      alert("Invalid JSON config");
      setLoading(false);
    }
  };

  return (
    <div>
      <h2>Providers</h2>
      <div>
        <h3>Create New Provider</h3>
        <input
          type="text"
          value={newProviderName}
          onChange={(e) => setNewProviderName(e.target.value)}
          placeholder="New provider name"
        />
        <textarea
          value={newProviderConfig}
          onChange={(e) => setNewProviderConfig(e.target.value)}
          placeholder='JSON Config (e.g., {"apiKey": "secret"})'
        />
        <button onClick={createProvider} disabled={loading}>Create Provider</button>
      </div>
      {loading && <p>Loading...</p>}
      <h3>Existing Providers</h3>
      <ul>
        {providers.map(p => (
          <li key={p.id}>
            {p.name}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default Providers;