"""
Data migration: transfer API keys from the old Flask `auth` table to
Django User + DRF Token records, then drop the old table.

Each old key becomes a service-account User (unusable password, can't log in)
with a matching Token.
"""

from django.db import migrations


def forwards(apps, schema_editor):
    connection = schema_editor.connection
    with connection.cursor() as cursor:
        # Check if the old auth table exists (it won't on fresh installs)
        cursor.execute(
            "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'auth' AND table_schema = 'public')"
        )
        if not cursor.fetchone()[0]:
            return

        # Check it's actually the old Flask table (has 'key' and 'name' columns, not Django's)
        cursor.execute(
            "SELECT column_name FROM information_schema.columns WHERE table_name = 'auth' AND table_schema = 'public'"
        )
        columns = {row[0] for row in cursor.fetchall()}
        if columns != {"key", "name"}:
            return

        cursor.execute("SELECT key, name FROM auth")
        old_keys = cursor.fetchall()

    if not old_keys:
        return

    User = apps.get_model("auth", "User")
    Token = apps.get_model("authtoken", "Token")

    for key, name in old_keys:
        username = f"svc-{name}"
        user, _ = User.objects.get_or_create(
            username=username,
            defaults={"is_active": True, "password": "!"},  # unusable password marker
        )
        Token.objects.get_or_create(user=user, defaults={"key": key})

    # Drop the old table
    with connection.cursor() as cursor:
        cursor.execute("DROP TABLE auth")


def backwards(apps, schema_editor):
    # No reverse — the old table is gone
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("pnogo", "0001_initial"),
        ("auth", "0012_alter_user_first_name_max_length"),
        ("authtoken", "0004_alter_tokenproxy_options"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards, elidable=True),
    ]
