import React from 'react';
import { Link } from 'react-router-dom';

const Header = () => {
  return (
    <header className="header">
      <h1>Employee.AI SaaS Platform</h1>
      <Link to="/app/login">
        <button>Tenant Sign In</button>
      </Link>
    </header>
  );
};

export default Header;