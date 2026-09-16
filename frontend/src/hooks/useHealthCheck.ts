import { useState, useEffect, useCallback } from 'react';
import { checkBackendHealth, API_BASE_URL } from '../services/api';

export interface HealthState {
  isLoading: boolean;
  isConnected: boolean | null;
  statusText: string | null;
  errorMessage: string | null;
  lastCheckedAt: Date | null;
  baseUrl: string;
}

export function useHealthCheck() {
  const [state, setState] = useState<HealthState>({
    isLoading: true,
    isConnected: null,
    statusText: null,
    errorMessage: null,
    lastCheckedAt: null,
    baseUrl: API_BASE_URL,
  });

  const verifyHealth = useCallback(async () => {
    setState((prev) => ({ ...prev, isLoading: true, errorMessage: null }));

    try {
      const data = await checkBackendHealth();
      setState({
        isLoading: false,
        isConnected: true,
        statusText: data.status,
        errorMessage: null,
        lastCheckedAt: new Date(),
        baseUrl: API_BASE_URL,
      });
    } catch (err: any) {
      setState({
        isLoading: false,
        isConnected: false,
        statusText: null,
        errorMessage: err.message || 'Connection refused or timed out',
        lastCheckedAt: new Date(),
        baseUrl: API_BASE_URL,
      });
    }
  }, []);

  useEffect(() => {
    verifyHealth();
  }, [verifyHealth]);

  return {
    ...state,
    refetch: verifyHealth,
  };
}
