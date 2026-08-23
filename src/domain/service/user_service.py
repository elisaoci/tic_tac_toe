from typing import Optional
from domain.repository.user_repository_interface import UserRepository
from datasource.model.user_model import UserModel


class UserService:
    def __init__(self, repository: UserRepository):
        self.repo = repository

    def register(self, login: str, password: str) -> bool:
        existing_user = self.repo.get_by_login(login)
        if existing_user:
            return False

        new_user = UserModel()
        new_user.login = login
        new_user.set_password(password)

        self.repo.save(new_user)
        return True

    def authenticate(self, login: str, password: str) -> Optional[str]:
        user = self.repo.get_by_login(login)
        if not user:
            return None

        if user.check_password(password):
            return user.uuid
        else:
            return None

    def get_user_by_uuid(self, uuid: str) -> Optional[UserModel]:
        return self.repo.get_by_uuid(uuid)