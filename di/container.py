from datasource.repository.game_repository import SQLAlchemyGameRepository
from domain.service.game_service import GameServiceImpl
from datasource.repository.user_repository import SQLAlchemyUserRepository
from domain.service.user_service import UserService
from di.database import SessionLocal

class Container:
    def __init__(self):
        session = SessionLocal()

        # Репозиторий и сервис для игр
        self._repository = SQLAlchemyGameRepository(session=session)
        self._game_service = GameServiceImpl(repository=self._repository)

        # Репозиторий и сервис для пользователей
        self._user_repository = SQLAlchemyUserRepository(session=session)
        self._user_service = UserService(repository=self._user_repository)

    @property
    def game_service(self):
        return self._game_service

    @property
    def repository(self):
        return self._repository

    @property
    def user_service(self):
        return self._user_service

    @property
    def user_repository(self):
        return self._user_repository