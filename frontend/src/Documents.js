import React, { useState, useEffect } from 'react';

function Documents({ tenantId, token, moduleId }) {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);

  const fetchDocuments = () => {
    if (!token || !moduleId) return;
    setLoading(true);
    fetch(`/documents?module_id=${moduleId}`, {
      headers: {
        'X-Tenant-ID': tenantId,
        'Authorization': `Bearer ${token}`
      }
    })
      .then(res => res.json())
      .then(data => {
        setDocuments(data);
        setLoading(false);
      })
      .catch(err => {
        console.error("Error fetching documents:", err);
        setLoading(false);
      });
  };

  useEffect(() => {
    fetchDocuments();
  }, [tenantId, token, moduleId]);

  const handleFileChange = (event) => {
    setSelectedFile(event.target.files[0]);
  };

  const handleUpload = async () => {
    if (!selectedFile || !moduleId) return;
    setLoading(true);
    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('module_id', moduleId);

    try {
      await fetch('/documents/upload', {
        method: 'POST',
        headers: {
          'X-Tenant-ID': tenantId,
          'Authorization': `Bearer ${token}`
        },
        body: formData
      });
      setSelectedFile(null);
      fetchDocuments();
    } catch (error) {
      console.error("Error uploading document:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h3>Documents for Module: {moduleId}</h3>
      <div>
        <input type="file" onChange={handleFileChange} />
        <button onClick={handleUpload} disabled={!selectedFile || loading}>Upload</button>
      </div>
      {loading && <p>Loading...</p>}
      <ul>
        {documents.map(doc => (
          <li key={doc.id}>
            {doc.name}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default Documents;