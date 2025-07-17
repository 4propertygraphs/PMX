from sqlalchemy import Column, DateTime, Integer, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Users(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    domain = Column(Text)
    created = Column(DateTime)
