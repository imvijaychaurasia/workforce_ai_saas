import React, { useState } from 'react';

function QnA({ tenantId, token, moduleId }) {
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');
  const [context, setContext] = useState('');
  const [loading, setLoading] = useState(false);

  const handleAsk = async () => {
    if (!question.trim() || !moduleId) return;
    setLoading(true);
    try {
      const response = await fetch(`/ai/ask?question=${encodeURIComponent(question)}&module_id=${moduleId}`, {
        method: 'POST',
        headers: {
          'X-Tenant-ID': tenantId,
          'Authorization': `Bearer ${token}`
        }
      });
      const data = await response.json();
      setAnswer(data.answer);
      setContext(data.context);
    } catch (error) {
      console.error("Error asking question:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h4>Q&A for Module: {moduleId}</h4>
      <input
        type="text"
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        placeholder="Ask a question"
      />
      <button onClick={handleAsk} disabled={!question.trim() || loading}>Ask</button>
      {loading && <p>Loading...</p>}
      {answer && (
        <div>
          <h5>Answer</h5>
          <p>{answer}</p>
          <h5>Context</h5>
          <pre>{context}</pre>
        </div>
      )}
    </div>
  );
}

export default QnA;