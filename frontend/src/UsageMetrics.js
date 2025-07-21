import React, { useState, useEffect } from 'react';

function UsageMetrics({ tenantId, token }) {
  const [metrics, setMetrics] = useState([]);
  const [loading, setLoading] = useState(false);

  const fetchMetrics = () => {
    if (!token) return;
    setLoading(true);
    fetch('/usage-metrics', {
      headers: {
        'X-Tenant-ID': tenantId,
        'Authorization': `Bearer ${token}`
      }
    })
      .then(res => res.json())
      .then(data => {
        setMetrics(data);
        setLoading(false);
      })
      .catch(err => {
        console.error("Error fetching usage metrics:", err);
        setLoading(false);
      });
  };

  useEffect(() => {
    fetchMetrics();
  }, [tenantId, token]);

  return (
    <div>
      <h2>Usage Metrics</h2>
      {loading && <p>Loading...</p>}
      <table>
        <thead>
          <tr>
            <th>Timestamp</th>
            <th>Metric Name</th>
            <th>Value</th>
          </tr>
        </thead>
        <tbody>
          {metrics.map(metric => (
            <tr key={metric.id}>
              <td>{metric.timestamp}</td>
              <td>{metric.metric_name}</td>
              <td>{JSON.stringify(metric.value)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default UsageMetrics;