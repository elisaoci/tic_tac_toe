from abc import ABC, abstractmethod
from typing import Optional
from datasource.model.user_model import UserModel


class UserRepository(ABC):

    @abstractmethod
    def save(self, user: UserModel) -> None:
        pass

    @abstractmethod
    def get_by_uuid(self, uuid: str) -> Optional[UserModel]:
        pass

    @abstractmethod
    def get_by_login(self, login: str) -> Optional[UserModel]:
        pass