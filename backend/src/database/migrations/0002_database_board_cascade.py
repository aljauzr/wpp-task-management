from django.db import NotSupportedError, migrations


SQLITE_TRIGGER = "boards_delete_tasks"


def set_postgresql_delete_rule(schema_editor, rule):
    connection = schema_editor.connection
    with connection.cursor() as cursor:
        constraints = connection.introspection.get_constraints(cursor, "tasks")
    names = [
        name
        for name, details in constraints.items()
        if details["columns"] == ["board_id"]
        and details["foreign_key"] == ("boards", "id")
    ]
    if len(names) != 1:
        raise RuntimeError("Expected exactly one tasks.board_id foreign key.")

    name = schema_editor.quote_name(names[0])
    schema_editor.execute(f'ALTER TABLE "tasks" DROP CONSTRAINT {name}')
    schema_editor.execute(
        f'ALTER TABLE "tasks" ADD CONSTRAINT {name} '
        'FOREIGN KEY ("board_id") REFERENCES "boards" ("id") '
        f"ON DELETE {rule} DEFERRABLE INITIALLY DEFERRED"
    )


def enable_database_cascade(apps, schema_editor):
    vendor = schema_editor.connection.vendor
    if vendor == "sqlite":
        # SQLite cannot ALTER an existing FK. A database trigger avoids rebuilding
        # the table and preserves all existing rows, indexes, and constraints.
        schema_editor.execute(
            f'CREATE TRIGGER "{SQLITE_TRIGGER}" AFTER DELETE ON "boards" '
            'FOR EACH ROW BEGIN '
            'DELETE FROM "tasks" WHERE "board_id" = OLD."id"; '
            "END"
        )
    elif vendor == "postgresql":
        set_postgresql_delete_rule(schema_editor, "CASCADE")
    else:
        raise NotSupportedError("Board cascade supports SQLite and PostgreSQL only.")


def disable_database_cascade(apps, schema_editor):
    vendor = schema_editor.connection.vendor
    if vendor == "sqlite":
        schema_editor.execute(f'DROP TRIGGER "{SQLITE_TRIGGER}"')
    elif vendor == "postgresql":
        set_postgresql_delete_rule(schema_editor, "NO ACTION")
    else:
        raise NotSupportedError("Board cascade supports SQLite and PostgreSQL only.")


class Migration(migrations.Migration):
    dependencies = [
        ("src", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(enable_database_cascade, disable_database_cascade),
    ]
