import React, { useState, useEffect } from 'react';

function Orchestrations({ tenantId, token }) {
  const [orchestrations, setOrchestrations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [newOrchestrationName, setNewOrchestrationName] = useState('');
  const [pipeline, setPipeline] = useState([{ module: '', config: '' }]);

  const fetchOrchestrations = () => {
    if (!token) return;
    setLoading(true);
    fetch('/orchestrations', {
      headers: {
        'X-Tenant-ID': tenantId,
        'Authorization': `Bearer ${token}`
      }
    })
      .then(res => res.json())
      .then(data => {
        setOrchestrations(data);
        setLoading(false);
      })
      .catch(err => {
        console.error("Error fetching orchestrations:", err);
        setLoading(false);
      });
  };

  useEffect(() => {
    fetchOrchestrations();
  }, [tenantId, token]);

  const handlePipelineChange = (index, field, value) => {
    const newPipeline = [...pipeline];
    newPipeline[index][field] = value;
    setPipeline(newPipeline);
  };

  const addPipelineStep = () => {
    setPipeline([...pipeline, { module: '', config: '' }]);
  };

  const removePipelineStep = (index) => {
    const newPipeline = [...pipeline];
    newPipeline.splice(index, 1);
    setPipeline(newPipeline);
  };

  const createOrchestration = async () => {
    if (!newOrchestrationName.trim() || !token) return;
    setLoading(true);
    const parsedPipeline = pipeline.map(step => ({
      ...step,
      config: JSON.parse(step.config || '{}')
    }));
    await fetch('/orchestrations', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Tenant-ID': tenantId,
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        name: newOrchestrationName,
        pipeline: parsedPipeline
      })
    });
    setNewOrchestrationName('');
    setPipeline([{ module: '', config: '' }]);
    fetchOrchestrations();
  };

  const triggerOrchestration = async (orchestrationId) => {
    if (!token) return;
    setLoading(true);
    await fetch(`/orchestrations/${orchestrationId}/trigger`, {
      method: 'POST',
      headers: {
        'X-Tenant-ID': tenantId,
        'Authorization': `Bearer ${token}`
      }
    });
    fetchOrchestrations();
  };

  return (
    <div>
      <h2>Orchestrations</h2>
      <div>
        <h3>Create New Orchestration</h3>
        <input
          type="text"
          value={newOrchestrationName}
          onChange={(e) => setNewOrchestrationName(e.target.value)}
          placeholder="New orchestration name"
        />
        <h4>Pipeline Steps</h4>
        {pipeline.map((step, index) => (
          <div key={index}>
            <input
              type="text"
              value={step.module}
              onChange={(e) => handlePipelineChange(index, 'module', e.target.value)}
              placeholder="Module Name"
            />
            <textarea
              value={step.config}
              onChange={(e) => handlePipelineChange(index, 'config', e.target.value)}
              placeholder='JSON Config (e.g., {"key": "value"})'
            />
            <button onClick={() => removePipelineStep(index)}>Remove</button>
          </div>
        ))}
        <button onClick={addPipelineStep}>Add Step</button>
        <button onClick={createOrchestration} disabled={loading}>Create Orchestration</button>
      </div>
      {loading && <p>Loading...</p>}
      <h3>Existing Orchestrations</h3>
      <ul>
        {orchestrations.map(orch => (
          <li key={orch.id}>
            {orch.name}
            <button onClick={() => triggerOrchestration(orch.id)} disabled={loading}>Trigger</button>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default Orchestrations;