from sqlalchemy import DOUBLE, TEXT
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class RentYoy(Base):
    __tablename__ = "rent_yoy"
    index: Mapped[int] = mapped_column(primary_key=True)
    avg_yoy: Mapped[int] = mapped_column(DOUBLE)
    county: Mapped[str] = mapped_column(TEXT)
    beds: Mapped[int] = mapped_column(DOUBLE)
