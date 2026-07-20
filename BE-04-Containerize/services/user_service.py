import uuid

from dtos.user_dto import UserCreateDTO, UserReadDTO, UserUpdateDTO
from models import User
from repositories.user_repository_port import UserRepositoryPort


class UserService:
    def __init__(self, user_repository: UserRepositoryPort):
        self.user_repository = user_repository

    def create_user(self, payload: UserCreateDTO) -> UserReadDTO:
        db_user = User(
            first_name=payload.first_name,
            last_name=payload.last_name,
            email=payload.email,
            telephone=payload.telephone,
        )
        created = self.user_repository.create(db_user)
        return self._to_read_dto(created)

    def get_user_by_id(self, user_id: uuid.UUID) -> UserReadDTO | None:
        db_user = self.user_repository.get_by_id(str(user_id))
        if db_user is None:
            return None
        return self._to_read_dto(db_user)

    def list_users(
        self,
        email: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
        telephone: str | None = None,
    ) -> list[UserReadDTO]:
        users = self.user_repository.list_users(
            email=email,
            first_name=first_name,
            last_name=last_name,
            telephone=telephone,
        )
        return [self._to_read_dto(user) for user in users]

    def update_user(self, user_id: uuid.UUID, payload: UserUpdateDTO) -> UserReadDTO | None:
        existing = self.user_repository.get_by_id(str(user_id))
        if existing is None:
            return None

        if payload.first_name is not None:
            existing.first_name = payload.first_name
        if payload.last_name is not None:
            existing.last_name = payload.last_name
        if payload.email is not None:
            existing.email = payload.email
        if payload.telephone is not None:
            existing.telephone = payload.telephone

        updated = self.user_repository.update(existing)
        return self._to_read_dto(updated)

    def delete_user(self, user_id: uuid.UUID) -> bool:
        existing = self.user_repository.get_by_id(str(user_id))
        if existing is None:
            return False
        self.user_repository.delete(existing)
        return True

    @staticmethod
    def _to_read_dto(user: User) -> UserReadDTO:
        return UserReadDTO(
            id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            telephone=user.telephone,
        )
