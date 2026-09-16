/**
 * Centralized API service.
 * Base URL is read from environment variables to satisfy R26 (no hardcoding).
 */

export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ||
  process.env.VITE_API_BASE_URL ||
  'http://localhost:8000';

export interface HealthResponse {
  status: string;
}

export class ApiError extends Error {
  constructor(public statusCode: number, message: string) {
    super(message);
    this.name = 'ApiError';
  }
}

/**
 * Checks backend service availability via GET /health.
 */
export async function checkBackendHealth(): Promise<HealthResponse> {
  const url = `${API_BASE_URL.replace(/\/$/, '')}/health`;

  try {
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
      },
      // Short timeout prevention via AbortController if supported
      signal: AbortSignal.timeout(5000),
    });

    if (!response.ok) {
      throw new ApiError(response.status, `Backend responded with HTTP ${response.status}`);
    }

    const data = await response.json();
    return data as HealthResponse;
  } catch (error: any) {
    if (error instanceof ApiError) {
      throw error;
    }
    throw new Error(
      error.message || `Unable to reach backend at ${API_BASE_URL}. Ensure Django server is running.`
    );
  }
}
