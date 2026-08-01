from typing import Optional
from sqlalchemy.orm import Session
from domain.repository.user_repository_interface import UserRepository
from datasource.model.user_model import UserModel


class SQLAlchemyUserRepository(UserRepository):
    def __init__(self, session: Session):
        self.session = session

    def save(self, user: UserModel) -> None:
        self.session.merge(user)
        self.session.commit()

    def get_by_uuid(self, uuid: str) -> Optional[UserModel]:
        return self.session.query(UserModel).filter_by(uuid=uuid).first()

    def get_by_login(self, login: str) -> Optional[UserModel]:
        return self.session.query(UserModel).filter_by(login=login).first()