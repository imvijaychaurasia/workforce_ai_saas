import React from 'react';

const BillingManagement = () => {
  // Placeholder data
  const currentPlan = 'Pro Plan';
  const invoices = [
    { id: 1, date: '2023-05-01', amount: '$99.99', status: 'Paid' },
    { id: 2, date: '2023-04-01', amount: '$99.99', status: 'Paid' },
    { id: 3, date: '2023-03-01', amount: '$99.99', status: 'Paid' },
  ];
  const paymentMethods = [
    { id: 1, type: 'Visa', last4: '4242', expiry: '12/25' },
    { id: 2, type: 'Mastercard', last4: '5555', expiry: '08/26' },
  ];

  return (
    <div style={{ padding: '20px' }}>
      <h2>Billing Management</h2>

      {/* Current Plan Section */}
      <div style={{ marginBottom: '30px' }}>
        <h3>Current Plan</h3>
        <p>{currentPlan}</p>
        <button>Upgrade Plan</button>
      </div>

      {/* Invoices Section */}
      <div style={{ marginBottom: '30px' }}>
        <h3>Invoices</h3>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr>
              <th style={{ border: '1px solid #ddd', padding: '8px', textAlign: 'left' }}>Date</th>
              <th style={{ border: '1px solid #ddd', padding: '8px', textAlign: 'left' }}>Amount</th>
              <th style={{ border: '1px solid #ddd', padding: '8px', textAlign: 'left' }}>Status</th>
              <th style={{ border: '1px solid #ddd', padding: '8px', textAlign: 'left' }}></th>
            </tr>
          </thead>
          <tbody>
            {invoices.map((invoice) => (
              <tr key={invoice.id}>
                <td style={{ border: '1px solid #ddd', padding: '8px' }}>{invoice.date}</td>
                <td style={{ border: '1px solid #ddd', padding: '8px' }}>{invoice.amount}</td>
                <td style={{ border: '1px solid #ddd', padding: '8px' }}>{invoice.status}</td>
                <td style={{ border: '1px solid #ddd', padding: '8px' }}><button>Download</button></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Payment Methods Section */}
      <div>
        <h3>Payment Methods</h3>
        {paymentMethods.map((method) => (
          <div key={method.id} style={{ border: '1px solid #ddd', padding: '10px', marginBottom: '10px' }}>
            <p>{method.type} ending in {method.last4}</p>
            <p>Expires: {method.expiry}</p>
          </div>
        ))}
        <button>Add New Payment Method</button>
      </div>
    </div>
  );
};

export default BillingManagement;