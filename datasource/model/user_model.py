from sqlalchemy import Column, String
from di.database import Base
import uuid
from werkzeug.security import generate_password_hash, check_password_hash

class UserModel(Base):
    __tablename__ = "users"

    uuid = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    login = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    def set_password(self, plain_password: str):
        self.hashed_password = generate_password_hash(plain_password)

    def check_password(self, plain_password: str) -> bool:
        return check_password_hash(self.hashed_password, plain_password)