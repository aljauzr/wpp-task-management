export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ||
  process.env.VITE_API_BASE_URL ||
  'http://localhost:8000';

export type TaskStatus = 'TODO' | 'IN_PROGRESS' | 'DONE';

export interface HealthResponse {
  status: string;
}

export interface ApiErrorPayload {
  error: string;
  message: string;
  field: string | null;
}

export interface Board {
  id: number;
  name: string;
  created_at: string;
  updated_at: string;
  tasks: Task[];
}

export interface Task {
  id: number;
  board: number;
  title: string;
  description: string;
  status: TaskStatus;
  created_at: string;
  updated_at: string;
}

export interface CreateBoardInput {
  name: string;
}

export interface CreateTaskInput {
  title: string;
  description?: string;
  status?: TaskStatus;
}

export class ApiError extends Error {
  constructor(
    public statusCode: number,
    public code: string,
    message: string,
    public field: string | null = null
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

const REQUEST_TIMEOUT_MS = 5000;
const NORMALIZED_BASE_URL = API_BASE_URL.replace(/\/$/, '');

async function requestJson<T>(path: string, init?: RequestInit): Promise<T> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);
  const url = `${NORMALIZED_BASE_URL}${path}`;

  try {
    const response = await fetch(url, {
      ...init,
      headers: {
        Accept: 'application/json',
        ...(init?.body ? { 'Content-Type': 'application/json' } : {}),
        ...init?.headers,
      },
      signal: controller.signal,
    });

    if (response.status === 204) {
      return undefined as T;
    }

    const data = (await response.json().catch(() => null)) as T | ApiErrorPayload | null;

    if (!response.ok) {
      const payload = data as ApiErrorPayload | null;
      throw new ApiError(
        response.status,
        payload?.error || 'HTTP_ERROR',
        payload?.message || `Request failed with HTTP ${response.status}.`,
        payload?.field ?? null
      );
    }

    return data as T;
  } catch (error: unknown) {
    if (error instanceof ApiError) {
      throw error;
    }

    if (error instanceof Error && error.name === 'AbortError') {
      throw new ApiError(
        0,
        'NETWORK_ERROR',
        `Request timed out while contacting ${NORMALIZED_BASE_URL}.`
      );
    }

    throw new ApiError(
      0,
      'NETWORK_ERROR',
      error instanceof Error
        ? error.message
        : `Unable to reach backend at ${NORMALIZED_BASE_URL}.`
    );
  } finally {
    clearTimeout(timeoutId);
  }
}

export async function checkBackendHealth(): Promise<HealthResponse> {
  return requestJson<HealthResponse>('/health');
}

export async function listBoards(): Promise<Board[]> {
  return requestJson<Board[]>('/api/boards/');
}

export async function createBoard(payload: CreateBoardInput): Promise<Board> {
  return requestJson<Board>('/api/boards/', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export async function listBoardTasks(
  boardId: number,
  status?: TaskStatus
): Promise<Task[]> {
  const query = status ? `?status=${encodeURIComponent(status)}` : '';
  return requestJson<Task[]>(`/api/boards/${boardId}/tasks/${query}`);
}

export async function createTask(
  boardId: number,
  payload: CreateTaskInput
): Promise<Task> {
  return requestJson<Task>(`/api/boards/${boardId}/tasks/`, {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export async function updateTaskStatus(
  taskId: number,
  status: TaskStatus
): Promise<Task> {
  return requestJson<Task>(`/api/tasks/${taskId}/`, {
    method: 'PATCH',
    body: JSON.stringify({ status }),
  });
}

export async function deleteTask(taskId: number): Promise<void> {
  return requestJson<void>(`/api/tasks/${taskId}/`, {
    method: 'DELETE',
  });
}

export async function deleteBoard(boardId: number): Promise<void> {
  return requestJson<void>(`/api/boards/${boardId}/`, {
    method: 'DELETE',
  });
}
