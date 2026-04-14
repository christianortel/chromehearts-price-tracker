from pathlib import Path


def test_initial_migration_exists() -> None:
    migration = (
        Path(__file__).resolve().parents[2]
        / "alembic"
        / "versions"
        / "20260413_0001_initial_schema.py"
    )
    assert migration.exists()
