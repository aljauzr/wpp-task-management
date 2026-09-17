import { FormEvent, useMemo, useState } from 'react';
import styles from './TaskManager.module.css';
import { Board } from '../../services/api';
import { SubmissionError } from '../../hooks/useTaskManager';

interface BoardSidebarProps {
  boards: Board[];
  selectedBoardId: number | null;
  isLoading: boolean;
  isSubmitting: boolean;
  error: string | null;
  formError: SubmissionError | null;
  onSelectBoard: (boardId: number) => void;
  onCreateBoard: (name: string) => Promise<{ ok: boolean }>;
}

function formatBoardMeta(board: Board): string {
  return new Intl.DateTimeFormat('en-GB', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  }).format(new Date(board.created_at));
}

export function BoardSidebar({
  boards,
  selectedBoardId,
  isLoading,
  isSubmitting,
  error,
  formError,
  onSelectBoard,
  onCreateBoard,
}: BoardSidebarProps) {
  const [name, setName] = useState('');
  const [clientError, setClientError] = useState<string | null>(null);

  const totalTasks = useMemo(
    () => boards.reduce((count, board) => count + board.tasks.length, 0),
    [boards]
  );

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const trimmedName = name.trim();
    if (!trimmedName) {
      setClientError('Board name is required.');
      return;
    }

    setClientError(null);
    const result = await onCreateBoard(trimmedName);
    if (result.ok) {
      setName('');
    }
  }

  return (
    <aside className={styles.panel}>
      <div className={styles.panelHeader}>
        <div>
          <h2 className={styles.panelTitle}>Boards</h2>
          <p className={styles.panelSubtitle}>
            {boards.length} board{boards.length === 1 ? '' : 's'} and {totalTasks} task
            {totalTasks === 1 ? '' : 's'}
          </p>
        </div>
      </div>

      <div className={`${styles.panelBody} ${styles.stack}`}>
        <form className={styles.form} onSubmit={handleSubmit}>
          <div className={styles.field}>
            <label className={styles.fieldLabel} htmlFor="board-name">
              Create board
            </label>
            <input
              id="board-name"
              className={styles.input}
              value={name}
              onChange={(event) => setName(event.target.value)}
              placeholder="Q3 Website Refresh"
              disabled={isSubmitting}
            />
            <p className={styles.fieldHint}>
              Add a named container to group related tasks.
            </p>
            {(clientError || formError?.field === 'name') && (
              <p className={styles.formError}>{clientError || formError?.message}</p>
            )}
          </div>

          <button className="button button-primary" disabled={isSubmitting}>
            {isSubmitting ? 'Creating board...' : 'Create board'}
          </button>
        </form>

        {error && <p className={styles.inlineError}>{error}</p>}

        {isLoading ? (
          <p className={styles.loadingText}>Loading boards...</p>
        ) : boards.length === 0 ? (
          <div className={styles.emptyState}>
            <strong>No boards yet.</strong>
            <p>Create your first board to start organizing tasks.</p>
          </div>
        ) : (
          <div className={styles.list}>
            {boards.map((board) => (
              <button
                key={board.id}
                type="button"
                className={`${styles.boardItem} ${
                  selectedBoardId === board.id ? styles.boardItemActive : ''
                }`}
                onClick={() => onSelectBoard(board.id)}
              >
                <span className={styles.boardRow}>
                  <span className={styles.boardText}>
                    <span className={styles.boardName}>{board.name}</span>
                    <span className={styles.boardMeta}>
                      Created {formatBoardMeta(board)}
                    </span>
                  </span>
                  <span className={styles.pill}>{board.tasks.length}</span>
                </span>
              </button>
            ))}
          </div>
        )}
      </div>
    </aside>
  );
}
