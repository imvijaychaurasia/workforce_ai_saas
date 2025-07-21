import React from 'react';
import './Tasks.css';

const tasksData = [
  {
    id: 'TSK-001',
    description: 'Resolve payment gateway issue',
    status: 'In Progress',
    createdAt: '2023-10-27T10:00:00Z',
  },
  {
    id: 'TSK-002',
    description: 'Deploy new feature to production',
    status: 'Completed',
    createdAt: '2023-10-26T15:30:00Z',
  },
  {
    id: 'TSK-003',
    description: 'Update user documentation',
    status: 'Pending',
    createdAt: '2023-10-25T09:00:00Z',
  },
];

const Tasks = () => {
  return (
    <div className="tasks-container">
      <h2>Tasks</h2>
      <table className="tasks-table">
        <thead>
          <tr>
            <th>Task ID</th>
            <th>Description</th>
            <th>Status</th>
            <th>Created At</th>
          </tr>
        </thead>
        <tbody>
          {tasksData.map((task) => (
            <tr key={task.id}>
              <td>{task.id}</td>
              <td>{task.description}</td>
              <td>{task.status}</td>
              <td>{new Date(task.createdAt).toLocaleString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default Tasks;