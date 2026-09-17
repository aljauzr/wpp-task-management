import React from 'react';
import Head from 'next/head';
import { Layout } from '../components/Layout';
import { BoardSidebar } from '../components/task-manager/BoardSidebar';
import { TaskWorkspace } from '../components/task-manager/TaskWorkspace';
import { useTaskManager } from '../hooks/useTaskManager';

export default function Home() {
  const taskManager = useTaskManager();

  return (
    <>
      <Head>
        <title>Mini Task Management</title>
      </Head>
      <Layout>
        <section className="intro-section page-intro">
          <div>
            <h2>Mini Task Management</h2>
            <p className="intro-text">
              Create boards, add tasks, filter by status, and update progress inline.
            </p>
          </div>
        </section>

        <section className="section">
          <div className="task-manager-shell">
            <BoardSidebar
              boards={taskManager.boards}
              selectedBoardId={taskManager.selectedBoardId}
              isLoading={taskManager.isBoardsLoading}
              isSubmitting={taskManager.isSubmittingBoard}
              error={taskManager.boardError}
              formError={taskManager.boardFormError}
              onSelectBoard={(boardId) => void taskManager.selectBoard(boardId)}
              onCreateBoard={taskManager.submitBoard}
            />

            <TaskWorkspace
              selectedBoard={taskManager.selectedBoard}
              tasks={taskManager.tasks}
              taskFilter={taskManager.taskFilter}
              isBoardsLoading={taskManager.isBoardsLoading}
              isTasksLoading={taskManager.isTasksLoading}
              isSubmittingTask={taskManager.isSubmittingTask}
              boardError={taskManager.boardError}
              taskError={taskManager.taskError}
              taskFormError={taskManager.taskFormError}
              onRetry={taskManager.retry}
              onSetTaskFilter={taskManager.setTaskFilter}
              onCreateTask={taskManager.submitTask}
              onChangeTaskStatus={taskManager.changeTaskStatus}
              onDeleteTask={taskManager.removeTask}
              onDeleteBoard={taskManager.removeBoard}
            />
          </div>
        </section>
      </Layout>
    </>
  );
}
