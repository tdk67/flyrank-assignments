from sqlalchemy.orm import Session

from models import User
from repositories.user_repository_port import UserRepositoryPort


class UserRepository(UserRepositoryPort):
    def __init__(self, session: Session):
        self.session = session

    def create(self, user: User) -> User:
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user

    def get_by_id(self, user_id: str) -> User | None:
        return self.session.query(User).filter(User.id == user_id).first()

    def list_users(
        self,
        email: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
        telephone: str | None = None,
    ) -> list[User]:
        query = self.session.query(User)

        if email is not None:
            query = query.filter(User.email == email)
        if first_name is not None:
            query = query.filter(User.first_name == first_name)
        if last_name is not None:
            query = query.filter(User.last_name == last_name)
        if telephone is not None:
            query = query.filter(User.telephone == telephone)

        return query.all()

    def update(self, user: User) -> User:
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user

    def delete(self, user: User) -> None:
        self.session.delete(user)
        self.session.commit()
