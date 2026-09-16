import React from 'react';
import { HealthState } from '../hooks/useHealthCheck';

interface HealthCardProps {
  health: HealthState & { refetch: () => void };
}

export const HealthCard: React.FC<HealthCardProps> = ({ health }) => {
  const { isLoading, isConnected, statusText, errorMessage, lastCheckedAt, baseUrl, refetch } = health;

  return (
    <div className="card status-card">
      <div className="status-card-header">
        <h2 className="card-title">Backend Service Status</h2>
        <button
          onClick={refetch}
          disabled={isLoading}
          className="button button-outline button-sm"
          title="Refresh connection status"
        >
          {isLoading ? 'Checking...' : 'Check Connection'}
        </button>
      </div>

      <div className="status-body">
        {isLoading && (
          <div className="status-row">
            <span className="status-indicator status-loading" />
            <div>
              <p className="status-label">Contacting Backend Service...</p>
              <p className="status-detail">Probing {baseUrl}/health</p>
            </div>
          </div>
        )}

        {!isLoading && isConnected && (
          <div className="status-row">
            <span className="status-indicator status-online" />
            <div>
              <p className="status-label">Backend: <strong className="text-success">Connected</strong></p>
              <p className="status-detail">
                Endpoint: <code>{baseUrl}/health</code> • Response: <code>{JSON.stringify({ status: statusText })}</code>
              </p>
            </div>
          </div>
        )}

        {!isLoading && isConnected === false && (
          <div className="status-row">
            <span className="status-indicator status-offline" />
            <div>
              <p className="status-label">Backend: <strong className="text-danger">Disconnected</strong></p>
              <p className="status-detail text-danger">{errorMessage}</p>
              <div className="troubleshoot-box">
                <p className="troubleshoot-title">To start the backend service:</p>
                <code>cd backend && python manage.py runserver 8000</code>
              </div>
            </div>
          </div>
        )}

        {lastCheckedAt && (
          <div className="status-footer">
            <span>Last checked: {lastCheckedAt.toLocaleTimeString()}</span>
            <span>Configured URL: <code>{baseUrl}</code></span>
          </div>
        )}
      </div>
    </div>
  );
};
