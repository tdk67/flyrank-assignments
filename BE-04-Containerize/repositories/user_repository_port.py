from abc import ABC, abstractmethod

from models import User


class UserRepositoryPort(ABC):
    @abstractmethod
    def create(self, user: User) -> User:
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, user_id: str) -> User | None:
        raise NotImplementedError

    @abstractmethod
    def list_users(
        self,
        email: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
        telephone: str | None = None,
    ) -> list[User]:
        raise NotImplementedError

    @abstractmethod
    def update(self, user: User) -> User:
        raise NotImplementedError

    @abstractmethod
    def delete(self, user: User) -> None:
        raise NotImplementedError
