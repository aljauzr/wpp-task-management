import { FormEvent, useMemo, useState } from 'react';
import styles from './TaskManager.module.css';
import { Board, Task, TaskStatus } from '../../services/api';
import { SubmissionError, TaskFilter } from '../../hooks/useTaskManager';

const STATUS_OPTIONS: Array<{ value: TaskStatus; label: string }> = [
  { value: 'TODO', label: 'To Do' },
  { value: 'IN_PROGRESS', label: 'In Progress' },
  { value: 'DONE', label: 'Done' },
];

const FILTER_OPTIONS: Array<{ value: TaskFilter; label: string }> = [
  { value: 'ALL', label: 'All statuses' },
  { value: 'TODO', label: 'To Do' },
  { value: 'IN_PROGRESS', label: 'In Progress' },
  { value: 'DONE', label: 'Done' },
];

interface TaskWorkspaceProps {
  selectedBoard: Board | null;
  tasks: Task[];
  taskFilter: TaskFilter;
  isBoardsLoading: boolean;
  isTasksLoading: boolean;
  isSubmittingTask: boolean;
  boardError: string | null;
  taskError: string | null;
  taskFormError: SubmissionError | null;
  onRetry: () => Promise<void>;
  onSetTaskFilter: (filter: TaskFilter) => Promise<void>;
  onCreateTask: (payload: {
    title: string;
    description: string;
    status: TaskStatus;
  }) => Promise<{ ok: boolean }>;
  onChangeTaskStatus: (taskId: number, status: TaskStatus) => Promise<void>;
  onDeleteTask: (taskId: number) => Promise<void>;
  onDeleteBoard: (boardId: number) => Promise<void>;
}

function statusLabel(status: TaskStatus): string {
  return STATUS_OPTIONS.find((option) => option.value === status)?.label ?? status;
}

function statusClass(status: TaskStatus): string {
  switch (status) {
    case 'IN_PROGRESS':
      return styles.statusInProgress;
    case 'DONE':
      return styles.statusDone;
    default:
      return styles.statusTodo;
  }
}

function formatDate(value: string): string {
  return new Intl.DateTimeFormat('en-GB', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(value));
}

export function TaskWorkspace({
  selectedBoard,
  tasks,
  taskFilter,
  isBoardsLoading,
  isTasksLoading,
  isSubmittingTask,
  boardError,
  taskError,
  taskFormError,
  onRetry,
  onSetTaskFilter,
  onCreateTask,
  onChangeTaskStatus,
  onDeleteTask,
  onDeleteBoard,
}: TaskWorkspaceProps) {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [status, setStatus] = useState<TaskStatus>('TODO');
  const [clientError, setClientError] = useState<string | null>(null);
  const [busyTaskId, setBusyTaskId] = useState<number | null>(null);

  const hasBackendIssue = Boolean(boardError || taskError);
  const visibleTaskCount = tasks.length;
  const boardTaskCount = selectedBoard?.tasks.length ?? 0;

  const emptyMessage = useMemo(() => {
    if (!selectedBoard) {
      return 'Create a board to start managing tasks.';
    }

    if (taskFilter !== 'ALL') {
      return `No tasks match the "${FILTER_OPTIONS.find((item) => item.value === taskFilter)?.label}" filter yet.`;
    }

    return 'This board has no tasks yet. Add one from the form below.';
  }, [selectedBoard, taskFilter]);

  async function handleTaskSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const trimmedTitle = title.trim();

    if (!trimmedTitle) {
      setClientError('Task title is required.');
      return;
    }

    setClientError(null);
    const result = await onCreateTask({
      title: trimmedTitle,
      description,
      status,
    });

    if (result.ok) {
      setTitle('');
      setDescription('');
      setStatus('TODO');
    }
  }

  async function handleStatusChange(taskId: number, nextStatus: TaskStatus) {
    setBusyTaskId(taskId);
    await onChangeTaskStatus(taskId, nextStatus);
    setBusyTaskId((current) => (current === taskId ? null : current));
  }

  async function handleDeleteTask(taskId: number) {
    setBusyTaskId(taskId);
    await onDeleteTask(taskId);
    setBusyTaskId((current) => (current === taskId ? null : current));
  }

  async function handleDeleteBoard() {
    if (!selectedBoard) {
      return;
    }

    const shouldDelete = window.confirm(
      `Delete "${selectedBoard.name}" and all of its tasks?`
    );

    if (!shouldDelete) {
      return;
    }

    await onDeleteBoard(selectedBoard.id);
  }

  return (
    <section className={styles.stack}>
      <div
        className={`${styles.statusBanner} ${
          hasBackendIssue ? styles.statusBannerOffline : styles.statusBannerOnline
        }`}
      >
        <div>
          <p className={styles.statusTitle}>
            {hasBackendIssue ? 'Backend connection issue' : 'Backend connected'}
          </p>
          <p className={styles.statusText}>
            {hasBackendIssue
              ? boardError || taskError
              : 'Boards and tasks are loaded over HTTP from the Django API.'}
          </p>
        </div>
        <button
          type="button"
          className="button button-outline"
          onClick={() => void onRetry()}
        >
          Retry
        </button>
      </div>

      <div className={styles.panel}>
        <div className={styles.panelHeader}>
          <div>
            <h2 className={styles.panelTitle}>
              {selectedBoard ? selectedBoard.name : 'Task workspace'}
            </h2>
            <p className={styles.panelSubtitle}>
              {selectedBoard
                ? `${boardTaskCount} total task${boardTaskCount === 1 ? '' : 's'}`
                : 'Select a board to view and manage its tasks.'}
            </p>
          </div>

          {selectedBoard && (
            <button
              type="button"
              className={`button button-outline ${styles.dangerButton}`}
              onClick={() => void handleDeleteBoard()}
            >
              Delete board
            </button>
          )}
        </div>

        <div className={`${styles.panelBody} ${styles.stack}`}>
          <div className={styles.toolbar}>
            <div className={styles.toolbarGroup}>
              <label className={styles.fieldLabel} htmlFor="task-filter">
                Filter tasks
              </label>
              <select
                id="task-filter"
                className={styles.select}
                value={taskFilter}
                onChange={(event) =>
                  void onSetTaskFilter(event.target.value as TaskFilter)
                }
                disabled={!selectedBoard || isBoardsLoading || isTasksLoading}
              >
                {FILTER_OPTIONS.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>

            <p className={styles.panelSubtitle}>
              {isTasksLoading ? 'Refreshing tasks...' : `${visibleTaskCount} visible`}
            </p>
          </div>

          {selectedBoard && (
            <form className={styles.form} onSubmit={handleTaskSubmit}>
              <div className={styles.field}>
                <label className={styles.fieldLabel} htmlFor="task-title">
                  Create task
                </label>
                <input
                  id="task-title"
                  className={styles.input}
                  value={title}
                  onChange={(event) => setTitle(event.target.value)}
                  placeholder="Prepare campaign brief"
                  disabled={isSubmittingTask}
                />
              </div>

              <div className={styles.field}>
                <label className={styles.fieldLabel} htmlFor="task-description">
                  Description
                </label>
                <textarea
                  id="task-description"
                  className={styles.textarea}
                  value={description}
                  onChange={(event) => setDescription(event.target.value)}
                  placeholder="Optional details for the task."
                  disabled={isSubmittingTask}
                />
              </div>

              <div className={styles.field}>
                <label className={styles.fieldLabel} htmlFor="task-status">
                  Initial status
                </label>
                <select
                  id="task-status"
                  className={styles.select}
                  value={status}
                  onChange={(event) => setStatus(event.target.value as TaskStatus)}
                  disabled={isSubmittingTask}
                >
                  {STATUS_OPTIONS.map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </div>

              {(clientError || taskFormError) && (
                <p className={styles.formError}>
                  {clientError || taskFormError?.message}
                </p>
              )}

              <div className={styles.actionsRow}>
                <button className="button button-primary" disabled={isSubmittingTask}>
                  {isSubmittingTask ? 'Creating task...' : 'Create task'}
                </button>
                <span className={styles.fieldHint}>
                  The browser validates empty titles before the request is sent.
                </span>
              </div>
            </form>
          )}

          {!selectedBoard && !isBoardsLoading ? (
            <div className={styles.emptyState}>
              <strong>No board selected.</strong>
              <p>{emptyMessage}</p>
            </div>
          ) : isTasksLoading ? (
            <p className={styles.loadingText}>Loading tasks...</p>
          ) : tasks.length === 0 ? (
            <div className={styles.emptyState}>
              <strong>No tasks to show.</strong>
              <p>{emptyMessage}</p>
            </div>
          ) : (
            <div className={styles.list}>
              {tasks.map((task) => {
                const isBusy = busyTaskId === task.id;

                return (
                  <article key={task.id} className={styles.taskCard}>
                    <div className={styles.taskHeader}>
                      <div>
                        <h3 className={styles.taskTitle}>{task.title}</h3>
                        <p className={styles.taskDescription}>
                          {task.description || 'No description provided.'}
                        </p>
                      </div>

                      <span className={`${styles.statusTag} ${statusClass(task.status)}`}>
                        {statusLabel(task.status)}
                      </span>
                    </div>

                    <div className={styles.taskMeta}>
                      <span>Created {formatDate(task.created_at)}</span>
                      <span>Updated {formatDate(task.updated_at)}</span>
                    </div>

                    <div className={styles.taskActions}>
                      <label className={styles.fieldLabel} htmlFor={`task-${task.id}-status`}>
                        Status
                      </label>
                      <select
                        id={`task-${task.id}-status`}
                        className={styles.select}
                        value={task.status}
                        onChange={(event) =>
                          void handleStatusChange(
                            task.id,
                            event.target.value as TaskStatus
                          )
                        }
                        disabled={isBusy}
                      >
                        {STATUS_OPTIONS.map((option) => (
                          <option key={option.value} value={option.value}>
                            {option.label}
                          </option>
                        ))}
                      </select>

                      <button
                        type="button"
                        className={`button button-outline ${styles.dangerButton}`}
                        onClick={() => void handleDeleteTask(task.id)}
                        disabled={isBusy}
                      >
                        {isBusy ? 'Working...' : 'Delete'}
                      </button>
                    </div>
                  </article>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </section>
  );
}
