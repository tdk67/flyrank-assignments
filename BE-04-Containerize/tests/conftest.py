"""Shared fixtures for the integration test suite.

Integration tests run against a dedicated `<POSTGRES_DB>_test` database on the
same Postgres server the dev stack already uses (see docker-compose.yml's `db`
service). The schema is created by replaying the actual Liquibase changeset
files from db/changelog/changesets/, not by SQLAlchemy's create_all() from
models.py -- that way the tests exercise the exact schema Liquibase produces
in every environment, and would catch drift between models.py and the
changesets (see the assigned_at/started_at/finished_at/failed_at columns that
were missing from changeset 002 until changeset 003 added them).
"""

import pathlib
from urllib.parse import quote_plus

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker

from config import settings
from database import get_db
from main import app

CHANGELOG_DIR = pathlib.Path(__file__).parent.parent / "db" / "changelog" / "changesets"
TEST_DB_NAME = f"{settings.postgres_db}_test"


def _dsn(database: str) -> str:
    user = quote_plus(settings.postgres_user)
    password = quote_plus(settings.postgres_password)
    return f"postgresql://{user}:{password}@{settings.postgres_host}:{settings.postgres_port}/{database}"


@pytest.fixture(scope="session")
def test_database_url() -> str:
    """Create a clean `<db>_test` database and replay the real changeset files into it."""
    admin_engine = create_engine(_dsn(settings.postgres_db), isolation_level="AUTOCOMMIT")
    with admin_engine.connect() as conn:
        conn.execute(text(f'DROP DATABASE IF EXISTS "{TEST_DB_NAME}" WITH (FORCE)'))
        conn.execute(text(f'CREATE DATABASE "{TEST_DB_NAME}"'))
    admin_engine.dispose()

    url = _dsn(TEST_DB_NAME)
    migration_engine = create_engine(url)
    with migration_engine.begin() as conn:
        for changeset in sorted(CHANGELOG_DIR.glob("*.sql")):
            conn.exec_driver_sql(changeset.read_text())
    migration_engine.dispose()

    return url


@pytest.fixture()
def db_session(test_database_url):
    """A session bound to a single DB transaction that is rolled back after each test.

    Repositories call `session.commit()` during normal operation. The
    after_transaction_end listener restarts a SAVEPOINT whenever one of those
    commits ends it, so those commits only ever release the savepoint --
    everything stays nested inside the outer transaction rolled back at
    teardown, giving each test a clean, isolated database.
    """
    engine = create_engine(test_database_url)
    connection = engine.connect()
    outer_transaction = connection.begin()

    session_factory = sessionmaker(bind=connection)
    session = session_factory()
    session.begin_nested()

    @event.listens_for(session, "after_transaction_end")
    def _restart_savepoint(sess, transaction):
        if transaction.nested and not transaction._parent.nested:
            sess.begin_nested()

    yield session

    session.close()
    outer_transaction.rollback()
    connection.close()
    engine.dispose()


@pytest.fixture()
def client(db_session):
    """A TestClient whose `get_db` dependency yields the per-test rolled-back session above."""

    def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
