from sqlalchemy import VARCHAR, Column, ForeignKey, Integer
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Token(Base):
    __tablename__ = "tokens"
    id = Column(Integer, primary_key=True)
    token = Column(VARCHAR(64))
    user_id = Column(Integer, ForeignKey("users.id"))
    salt = Column(VARCHAR(16))
