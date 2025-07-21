import React, { useState, useEffect } from 'react';

function Workflows({ tenantId, token }) {
  const [workflows, setWorkflows] = useState([]);
  const [loading, setLoading] = useState(false);
  const [newWorkflowName, setNewWorkflowName] = useState('');

  const fetchWorkflows = () => {
    if (!token) return;
    setLoading(true);
    fetch('/workflows', {
      headers: {
        'X-Tenant-ID': tenantId,
        'Authorization': `Bearer ${token}`
      }
    })
      .then(res => res.json())
      .then(data => {
        setWorkflows(data);
        setLoading(false);
      })
      .catch(err => {
        console.error("Error fetching workflows:", err);
        setLoading(false);
      });
  };

  useEffect(() => {
    fetchWorkflows();
  }, [tenantId, token]);

  const createWorkflow = async () => {
    if (!newWorkflowName.trim() || !token) return;
    setLoading(true);
    await fetch('/workflows', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Tenant-ID': tenantId,
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        name: newWorkflowName,
        definition: { nodes: [], connections: {} }
      })
    });
    setNewWorkflowName('');
    fetchWorkflows();
  };

  const triggerWorkflow = async (workflowId) => {
    if (!token) return;
    setLoading(true);
    await fetch(`/workflows/${workflowId}/trigger`, {
      method: 'POST',
      headers: {
        'X-Tenant-ID': tenantId,
        'Authorization': `Bearer ${token}`
      }
    });
    fetchWorkflows();
  };

  return (
    <div>
      <h2>Workflows</h2>
      <div>
        <input
          type="text"
          value={newWorkflowName}
          onChange={(e) => setNewWorkflowName(e.target.value)}
          placeholder="New workflow name"
        />
        <button onClick={createWorkflow} disabled={loading}>Create Workflow</button>
      </div>
      {loading && <p>Loading...</p>}
      <ul>
        {workflows.map(wf => (
          <li key={wf.id}>
            {wf.name}
            <button onClick={() => triggerWorkflow(wf.id)} disabled={loading}>Trigger</button>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default Workflows;