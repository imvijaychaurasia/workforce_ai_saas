import React, { useState, useEffect } from 'react';
import keycloak from '../../../keycloak';

const WorkflowManagement = () => {
  const [workflows, setWorkflows] = useState([]);
  const [workflowName, setWorkflowName] = useState('');

  const fetchWorkflows = async () => {
    try {
      const response = await fetch('/workflows', {
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${keycloak.token}`,
          'X-Tenant-ID': keycloak.realm,
        },
      });
      const data = await response.json();
      setWorkflows(data);
    } catch (error) {
      console.error('Error fetching workflows:', error);
    }
  };

  useEffect(() => {
    fetchWorkflows();
  }, []);

  const handleCreateWorkflow = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch('/workflows', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${keycloak.token}`,
          'X-Tenant-ID': keycloak.realm,
        },
        body: JSON.stringify({
          name: workflowName,
          definition: { "nodes": [], "connections": {} },
        }),
      });
      if (response.ok) {
        setWorkflowName('');
        fetchWorkflows();
      } else {
        console.error('Error creating workflow:', response.statusText);
      }
    } catch (error) {
      console.error('Error creating workflow:', error);
    }
  };

  const handleTriggerWorkflow = async (workflowId) => {
    try {
      const response = await fetch(`/workflows/${workflowId}/trigger`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${keycloak.token}`,
          'X-Tenant-ID': keycloak.realm,
        },
      });
      if (response.ok) {
        fetchWorkflows();
      } else {
        console.error('Error triggering workflow:', response.statusText);
      }
    } catch (error) {
      console.error('Error triggering workflow:', error);
    }
  };

  return (
    <div>
      <h2>Workflow Management</h2>
      <div>
        <h3>Existing Workflows</h3>
        <ul>
          {workflows.map((workflow) => (
            <li key={workflow.id}>
              {workflow.name}
              <button onClick={() => handleTriggerWorkflow(workflow.id)}>
                Trigger
              </button>
            </li>
          ))}
        </ul>
      </div>
      <div>
        <h3>Create New Workflow</h3>
        <form onSubmit={handleCreateWorkflow}>
          <div>
            <label>Workflow Name:</label>
            <input
              type="text"
              value={workflowName}
              onChange={(e) => setWorkflowName(e.target.value)}
              required
            />
          </div>
          <button type="submit">Create Workflow</button>
        </form>
      </div>
    </div>
  );
};

export default WorkflowManagement;