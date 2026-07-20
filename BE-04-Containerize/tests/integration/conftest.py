import json
import pathlib
import uuid
from datetime import datetime

import pytest

from models import Task, User

FIXTURE_PATH = pathlib.Path(__file__).parent.parent / "fixtures" / "sample_data.json"


def load_sample_data() -> dict:
    return json.loads(FIXTURE_PATH.read_text())


def _parse_dt(value: str | None):
    return datetime.fromisoformat(value) if value else None


@pytest.fixture()
def sample_data() -> dict:
    return load_sample_data()


@pytest.fixture()
def seeded_db(db_session, sample_data) -> dict:
    """Insert the sample dataset (fixtures/sample_data.json) directly via the ORM session."""
    for user in sample_data["users"]:
        db_session.add(
            User(
                id=uuid.UUID(user["id"]),
                first_name=user["first_name"],
                last_name=user["last_name"],
                email=user["email"],
                telephone=user["telephone"],
            )
        )
    db_session.flush()

    for task in sample_data["tasks"]:
        db_session.add(
            Task(
                id=uuid.UUID(task["id"]),
                name=task["name"],
                description=task["description"],
                status=task["status"],
                assignee_user_id=uuid.UUID(task["assignee_user_id"]) if task["assignee_user_id"] else None,
                start_date=_parse_dt(task.get("start_date")),
                end_date=_parse_dt(task.get("end_date")),
            )
        )
    db_session.flush()

    return sample_data
