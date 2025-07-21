import React, { useState } from 'react';

function Agent({ tenantId, token }) {
  const [taskDescription, setTaskDescription] = useState('');
  const [result, setResult] = useState('');
  const [loading, setLoading] = useState(false);

  const handleExecute = async () => {
    if (!taskDescription.trim()) return;
    setLoading(true);
    try {
      const response = await fetch(`/ai/agent/execute?task_description=${encodeURIComponent(taskDescription)}`, {
        method: 'POST',
        headers: {
          'X-Tenant-ID': tenantId,
          'Authorization': `Bearer ${token}`
        }
      });
      const data = await response.json();
      setResult(data.result);
    } catch (error) {
      console.error("Error executing agent task:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h3>AI Agent</h3>
      <textarea
        value={taskDescription}
        onChange={(e) => setTaskDescription(e.target.value)}
        placeholder="Enter a task for the AI agent"
      />
      <button onClick={handleExecute} disabled={!taskDescription.trim() || loading}>Execute</button>
      {loading && <p>Loading...</p>}
      {result && (
        <div>
          <h5>Result</h5>
          <pre>{result}</pre>
        </div>
      )}
    </div>
  );
}

export default Agent;