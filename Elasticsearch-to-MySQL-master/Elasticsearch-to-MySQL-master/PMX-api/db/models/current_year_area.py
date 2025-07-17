from sqlalchemy import DOUBLE, TEXT
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class CurrentYearArea(Base):
    __tablename__ = "area_avg"

    index: Mapped[int] = mapped_column(primary_key=True)
    county: Mapped[str] = mapped_column(TEXT)
    beds: Mapped[int] = mapped_column(DOUBLE)
    area: Mapped[str] = mapped_column(TEXT)
    region: Mapped[str] = mapped_column(TEXT)
    avg: Mapped[int] = mapped_column(DOUBLE)
