import React, { useState, useEffect } from 'react';

function AuditLog({ tenantId, token }) {
  const [auditLog, setAuditLog] = useState([]);
  const [loading, setLoading] = useState(false);

  const fetchAuditLog = () => {
    if (!token) return;
    setLoading(true);
    fetch('/audit-log', {
      headers: {
        'X-Tenant-ID': tenantId,
        'Authorization': `Bearer ${token}`
      }
    })
      .then(res => res.json())
      .then(data => {
        setAuditLog(data);
        setLoading(false);
      })
      .catch(err => {
        console.error("Error fetching audit log:", err);
        setLoading(false);
      });
  };

  useEffect(() => {
    fetchAuditLog();
  }, [tenantId, token]);

  return (
    <div>
      <h2>Audit Log</h2>
      {loading && <p>Loading...</p>}
      <table>
        <thead>
          <tr>
            <th>Timestamp</th>
            <th>User ID</th>
            <th>Action</th>
            <th>Details</th>
          </tr>
        </thead>
        <tbody>
          {auditLog.map(log => (
            <tr key={log.id}>
              <td>{log.timestamp}</td>
              <td>{log.user_id}</td>
              <td>{log.action}</td>
              <td>{JSON.stringify(log.details)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default AuditLog;