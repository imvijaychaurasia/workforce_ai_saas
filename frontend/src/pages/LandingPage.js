import React from 'react';
import Header from '../components/Header';
import './LandingPage.css';

const LandingPage = () => {
  return (
    <div className="landing-page">
      <Header />
      <main className="main-content">
        <h2>Our Services</h2>
        <p>Discover the amazing services we offer to help your business grow.</p>
        <h2>Our Products</h2>
        <p>Explore our innovative products designed to solve your problems.</p>
        <h2>Features</h2>
        <p>Our platform is packed with features to streamline your workflow.</p>
      </main>
    </div>
  );
};

export default LandingPage;