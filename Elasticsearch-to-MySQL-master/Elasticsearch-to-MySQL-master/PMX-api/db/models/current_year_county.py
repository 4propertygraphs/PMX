from sqlalchemy import DOUBLE, TEXT
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class CurrentYearCounty(Base):
    __tablename__ = "county_avg"

    index: Mapped[int] = mapped_column(primary_key=True)
    county: Mapped[str] = mapped_column(TEXT)
    beds: Mapped[int] = mapped_column(DOUBLE)
    avg: Mapped[int] = mapped_column(DOUBLE)
