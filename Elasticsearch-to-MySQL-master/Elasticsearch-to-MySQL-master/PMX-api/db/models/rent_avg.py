from sqlalchemy import DOUBLE, TEXT
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class rent_avg(Base):
    __tablename__ = "rent_county_avg"

    index: Mapped[int] = mapped_column(primary_key=True)
    county: Mapped[str] = mapped_column(TEXT)
    beds: Mapped[int] = mapped_column(DOUBLE)
    avg: Mapped[int] = mapped_column(DOUBLE)
