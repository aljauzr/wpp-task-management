import React from 'react';

export const Header: React.FC = () => {
  return (
    <header className="header">
      <div className="header-container">
        <div className="brand">
          <div className="brand-logo">TM</div>
          <div>
            <h1 className="brand-title">Task Manager</h1>
            <p className="brand-subtitle">WPP Media Full Stack Take-Home Study Case</p>
          </div>
        </div>
        <div className="header-badge">Initial Scaffolding</div>
      </div>
    </header>
  );
};
