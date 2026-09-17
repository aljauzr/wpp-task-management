import React from 'react';

export const Header: React.FC = () => {
  return (
    <header className="header">
      <div className="header-container">
        <div className="brand">
          <div className="brand-logo">MTM</div>
          <div>
            <h1 className="brand-title">Mini Task Management</h1>
          </div>
        </div>
      </div>
    </header>
  );
};
