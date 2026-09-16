import React, { ReactNode } from 'react';
import { Header } from './Header';

interface LayoutProps {
  children: ReactNode;
}

export const Layout: React.FC<LayoutProps> = ({ children }) => {
  return (
    <div className="layout-root">
      <Header />
      <main className="main-content">
        <div className="content-container">
          {children}
        </div>
      </main>
      <footer className="footer">
        <div className="footer-container">
          <p>WPP Media Full Stack Study Case • Clean Architecture Scaffolding</p>
        </div>
      </footer>
    </div>
  );
};
