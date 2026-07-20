import uuid

import pytest

from dtos.user_dto import UserCreateDTO, UserUpdateDTO
from services.user_service import UserService
from tests.unit.fakes import FakeUserRepository


@pytest.fixture()
def service() -> UserService:
    return UserService(FakeUserRepository())


def test_create_user_assigns_id_and_stores_fields(service):
    created = service.create_user(UserCreateDTO(first_name="Jane", last_name="Doe", email="jane@example.com", telephone=None))

    assert created.id is not None
    assert created.first_name == "Jane"
    assert created.last_name == "Doe"
    assert created.email == "jane@example.com"
    assert created.telephone is None


def test_get_user_by_id_returns_none_when_missing(service):
    assert service.get_user_by_id(uuid.uuid4()) is None


def test_get_user_by_id_returns_created_user(service):
    created = service.create_user(UserCreateDTO(first_name="Jane", last_name="Doe", email=None, telephone=None))

    found = service.get_user_by_id(created.id)

    assert found is not None
    assert found.id == created.id


def test_list_users_filters_by_email(service):
    service.create_user(UserCreateDTO(first_name="Jane", last_name="Doe", email="jane@example.com", telephone=None))
    service.create_user(UserCreateDTO(first_name="John", last_name="Smith", email="john@example.com", telephone=None))

    results = service.list_users(email="jane@example.com")

    assert len(results) == 1
    assert results[0].first_name == "Jane"


def test_update_user_changes_only_provided_fields(service):
    created = service.create_user(UserCreateDTO(first_name="Jane", last_name="Doe", email=None, telephone=None))

    updated = service.update_user(created.id, UserUpdateDTO(email="new@example.com"))

    assert updated is not None
    assert updated.email == "new@example.com"
    assert updated.first_name == "Jane"
    assert updated.last_name == "Doe"


def test_update_user_missing_returns_none(service):
    assert service.update_user(uuid.uuid4(), UserUpdateDTO(email="x@example.com")) is None


def test_delete_user_removes_record(service):
    created = service.create_user(UserCreateDTO(first_name="Jane", last_name="Doe", email=None, telephone=None))

    assert service.delete_user(created.id) is True
    assert service.get_user_by_id(created.id) is None


def test_delete_user_missing_returns_false(service):
    assert service.delete_user(uuid.uuid4()) is False
