import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import {
  ApiError,
  Board,
  CreateTaskInput,
  Task,
  TaskStatus,
  createBoard,
  createTask,
  deleteBoard,
  deleteTask,
  listBoardTasks,
  listBoards,
  updateTaskStatus,
} from '../services/api';

export type TaskFilter = 'ALL' | TaskStatus;

export interface SubmissionError {
  message: string;
  field: string | null;
}

export interface TaskManagerState {
  boards: Board[];
  selectedBoardId: number | null;
  tasks: Task[];
  taskFilter: TaskFilter;
  isBoardsLoading: boolean;
  isTasksLoading: boolean;
  isSubmittingBoard: boolean;
  isSubmittingTask: boolean;
  boardError: string | null;
  taskError: string | null;
  boardFormError: SubmissionError | null;
  taskFormError: SubmissionError | null;
}

function toSubmissionError(error: unknown, fallback: string): SubmissionError {
  if (error instanceof ApiError) {
    return {
      message: error.message,
      field: error.field,
    };
  }

  return {
    message: fallback,
    field: null,
  };
}

export function useTaskManager() {
  const selectedBoardIdRef = useRef<number | null>(null);
  const taskFilterRef = useRef<TaskFilter>('ALL');
  const [state, setState] = useState<TaskManagerState>({
    boards: [],
    selectedBoardId: null,
    tasks: [],
    taskFilter: 'ALL',
    isBoardsLoading: true,
    isTasksLoading: false,
    isSubmittingBoard: false,
    isSubmittingTask: false,
    boardError: null,
    taskError: null,
    boardFormError: null,
    taskFormError: null,
  });

  const selectedBoard = useMemo(
    () => state.boards.find((board) => board.id === state.selectedBoardId) ?? null,
    [state.boards, state.selectedBoardId]
  );

  useEffect(() => {
    selectedBoardIdRef.current = state.selectedBoardId;
    taskFilterRef.current = state.taskFilter;
  }, [state.selectedBoardId, state.taskFilter]);

  const loadTasks = useCallback(
    async (boardId: number, filter: TaskFilter) => {
      setState((current) => ({
        ...current,
        isTasksLoading: true,
        taskError: null,
      }));

      try {
        const tasks = await listBoardTasks(
          boardId,
          filter === 'ALL' ? undefined : filter
        );

        setState((current) => ({
          ...current,
          tasks,
          isTasksLoading: false,
          taskError: null,
        }));
      } catch (error) {
        const taskError = toSubmissionError(
          error,
          'Unable to load tasks for the selected board.'
        );
        setState((current) => ({
          ...current,
          tasks: [],
          isTasksLoading: false,
          taskError: taskError.message,
        }));
      }
    },
    []
  );

  const loadBoards = useCallback(
    async (preferredBoardId?: number | null, preferredFilter?: TaskFilter) => {
      setState((current) => ({
        ...current,
        isBoardsLoading: true,
        boardError: null,
      }));

      try {
        const boards = await listBoards();
        const nextBoardId =
          preferredBoardId && boards.some((board) => board.id === preferredBoardId)
            ? preferredBoardId
            : boards[0]?.id ?? null;
        const nextFilter = preferredFilter ?? taskFilterRef.current;

        setState((current) => ({
          ...current,
          boards,
          selectedBoardId: nextBoardId,
          isBoardsLoading: false,
          boardError: null,
          taskFilter: nextFilter,
          tasks: nextBoardId === null ? [] : current.tasks,
        }));

        if (nextBoardId !== null) {
          await loadTasks(nextBoardId, nextFilter);
        } else {
          setState((current) => ({
            ...current,
            tasks: [],
            isTasksLoading: false,
          }));
        }
      } catch (error) {
        const boardError = toSubmissionError(
          error,
          'Unable to load boards from the backend service.'
        );
        setState((current) => ({
          ...current,
          boards: [],
          selectedBoardId: null,
          tasks: [],
          isBoardsLoading: false,
          isTasksLoading: false,
          boardError: boardError.message,
          taskError: boardError.message,
        }));
      }
    },
    [loadTasks]
  );

  useEffect(() => {
    void loadBoards();
  }, [loadBoards]);

  const selectBoard = useCallback(
    async (boardId: number) => {
      setState((current) => ({
        ...current,
        selectedBoardId: boardId,
      }));
      await loadTasks(boardId, taskFilterRef.current);
    },
    [loadTasks]
  );

  const setTaskFilter = useCallback(
    async (filter: TaskFilter) => {
      setState((current) => ({
        ...current,
        taskFilter: filter,
      }));

      if (selectedBoardIdRef.current !== null) {
        await loadTasks(selectedBoardIdRef.current, filter);
      }
    },
    [loadTasks]
  );

  const submitBoard = useCallback(
    async (name: string) => {
      setState((current) => ({
        ...current,
        isSubmittingBoard: true,
        boardFormError: null,
      }));

      try {
        const board = await createBoard({ name });
        await loadBoards(board.id, 'ALL');
        setState((current) => ({
          ...current,
          isSubmittingBoard: false,
          boardFormError: null,
        }));
        return { ok: true as const };
      } catch (error) {
        const boardFormError = toSubmissionError(
          error,
          'Unable to create the board.'
        );
        setState((current) => ({
          ...current,
          isSubmittingBoard: false,
          boardFormError,
        }));
        return { ok: false as const, error: boardFormError };
      }
    },
    [loadBoards]
  );

  const submitTask = useCallback(
    async (payload: CreateTaskInput) => {
      const currentBoardId = selectedBoardIdRef.current;

      if (currentBoardId === null) {
        const taskFormError = {
          message: 'Select a board before creating a task.',
          field: 'board',
        };
        setState((current) => ({
          ...current,
          taskFormError,
        }));
        return { ok: false as const, error: taskFormError };
      }

      setState((current) => ({
        ...current,
        isSubmittingTask: true,
        taskFormError: null,
      }));

      try {
        const task = await createTask(currentBoardId, payload);

        setState((current) => ({
          ...current,
          isSubmittingTask: false,
          taskFormError: null,
          tasks:
            current.taskFilter === 'ALL' || current.taskFilter === task.status
              ? [...current.tasks, task]
              : current.tasks,
          boards: current.boards.map((board) =>
            board.id === currentBoardId
              ? { ...board, tasks: [...board.tasks, task] }
              : board
          ),
        }));

        return { ok: true as const };
      } catch (error) {
        const taskFormError = toSubmissionError(
          error,
          'Unable to create the task.'
        );
        setState((current) => ({
          ...current,
          isSubmittingTask: false,
          taskFormError,
        }));
        return { ok: false as const, error: taskFormError };
      }
    },
    []
  );

  const changeTaskStatus = useCallback(
    async (taskId: number, status: TaskStatus) => {
      const previousTask = state.tasks.find((task) => task.id === taskId) ?? null;

      try {
        const updatedTask = await updateTaskStatus(taskId, status);
        setState((current) => ({
          ...current,
          taskError: null,
          tasks:
            current.taskFilter !== 'ALL' && current.taskFilter !== updatedTask.status
              ? current.tasks.filter((task) => task.id !== taskId)
              : current.tasks.map((task) =>
                  task.id === taskId ? updatedTask : task
                ),
          boards: current.boards.map((board) =>
            board.id === updatedTask.board
              ? {
                  ...board,
                  tasks: board.tasks.map((task) =>
                    task.id === taskId ? updatedTask : task
                  ),
                }
              : board
          ),
        }));
      } catch (error) {
        const taskError = toSubmissionError(
          error,
          previousTask
            ? `Unable to update "${previousTask.title}".`
            : 'Unable to update the task.'
        );
        setState((current) => ({
          ...current,
          taskError: taskError.message,
        }));
      }
    },
    [state.tasks]
  );

  const removeTask = useCallback(
    async (taskId: number) => {
      const existingTask = state.tasks.find((task) => task.id === taskId) ?? null;

      try {
        await deleteTask(taskId);
        setState((current) => ({
          ...current,
          taskError: null,
          tasks: current.tasks.filter((task) => task.id !== taskId),
          boards: current.boards.map((board) =>
            board.id === existingTask?.board
              ? {
                  ...board,
                  tasks: board.tasks.filter((task) => task.id !== taskId),
                }
              : board
          ),
        }));
      } catch (error) {
        const taskError = toSubmissionError(
          error,
          existingTask
            ? `Unable to delete "${existingTask.title}".`
            : 'Unable to delete the task.'
        );
        setState((current) => ({
          ...current,
          taskError: taskError.message,
        }));
      }
    },
    [state.tasks]
  );

  const removeBoard = useCallback(
    async (boardId: number) => {
      try {
        await deleteBoard(boardId);
        const remainingBoards = state.boards.filter((board) => board.id !== boardId);
        const nextBoardId = remainingBoards[0]?.id ?? null;
        setState((current) => ({
          ...current,
          boards: remainingBoards,
          selectedBoardId: nextBoardId,
          tasks: nextBoardId === null ? [] : current.tasks,
          boardError: null,
        }));

        if (nextBoardId !== null) {
          await loadTasks(nextBoardId, taskFilterRef.current);
        } else {
          setState((current) => ({
            ...current,
            tasks: [],
            taskError: null,
          }));
        }
      } catch (error) {
        const boardError = toSubmissionError(
          error,
          'Unable to delete the board.'
        );
        setState((current) => ({
          ...current,
          boardError: boardError.message,
        }));
      }
    },
    [loadTasks, state.boards]
  );

  const retry = useCallback(async () => {
    await loadBoards(selectedBoardIdRef.current, taskFilterRef.current);
  }, [loadBoards]);

  return {
    ...state,
    selectedBoard,
    retry,
    selectBoard,
    setTaskFilter,
    submitBoard,
    submitTask,
    changeTaskStatus,
    removeTask,
    removeBoard,
  };
}
