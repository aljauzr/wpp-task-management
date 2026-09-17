"""Verify the R4 migration on an existing database, including reversal."""

import pytest
from django.db import IntegrityError, connection, transaction
from django.db.migrations.executor import MigrationExecutor


pytestmark = pytest.mark.django_db(transaction=True)

BEFORE = [("src", "0001_initial")]
AFTER = [("src", "0002_database_board_cascade")]


def migrate_to(target):
    executor = MigrationExecutor(connection)
    executor.migrate(target)
    return executor.loader.project_state(target).apps


def assert_sql_delete_is_rejected(board_id):
    with pytest.raises(IntegrityError):
        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM boards WHERE id = %s", [board_id])


def indexes_and_checks():
    with connection.cursor() as cursor:
        constraints = connection.introspection.get_constraints(cursor, "tasks")
    return {
        name: details
        for name, details in constraints.items()
        if details["index"] or details["check"] or details["primary_key"]
    }


def assert_database_cascade_installed():
    with connection.cursor() as cursor:
        if connection.vendor == "sqlite":
            cursor.execute(
                "SELECT name FROM sqlite_master "
                "WHERE type = 'trigger' AND tbl_name = 'boards'"
            )
            assert ("boards_delete_tasks",) in cursor.fetchall()
        else:
            cursor.execute(
                "SELECT confdeltype, condeferrable, condeferred FROM pg_constraint "
                "WHERE conrelid = 'tasks'::regclass AND contype = 'f'"
            )
            assert cursor.fetchall() == [("c", True, True)]


def test_upgrade_reverse_and_reapply_preserve_existing_data_and_constraints():
    latest = MigrationExecutor(connection).loader.graph.leaf_nodes()
    try:
        apps = migrate_to(BEFORE)
        Board = apps.get_model("src", "Board")
        Task = apps.get_model("src", "Task")
        board = Board.objects.create(name="Existing board")
        task = Task.objects.create(
            board=board, title="Existing task", description="Keep\nformatting",
            status="IN_PROGRESS",
        )
        board_before = Board.objects.values().get(pk=board.id)
        task_before = Task.objects.values().get(pk=task.id)
        schema_before = indexes_and_checks()
        assert_sql_delete_is_rejected(board.id)

        for target in (AFTER, BEFORE, AFTER):
            migrate_to(target)
            assert Board.objects.values().get(pk=board.id) == board_before
            assert Task.objects.values().get(pk=task.id) == task_before
            assert indexes_and_checks() == schema_before
            connection.check_constraints()

            if target == BEFORE:
                assert_sql_delete_is_rejected(board.id)
            else:
                assert_database_cascade_installed()
                disposable = Board.objects.create(name="Disposable")
                child = Task.objects.create(board=disposable, title="Disposable task")
                with connection.cursor() as cursor:
                    cursor.execute("DELETE FROM boards WHERE id = %s", [disposable.id])
                assert not Board.objects.filter(pk=disposable.id).exists()
                assert not Task.objects.filter(pk=child.id).exists()
    finally:
        # Other tests must always see the latest schema, even after a failure.
        migrate_to(latest)
