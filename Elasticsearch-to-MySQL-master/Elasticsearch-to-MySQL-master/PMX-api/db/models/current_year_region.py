from sqlalchemy import DOUBLE, TEXT
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class CurrentYearRegion(Base):
    __tablename__ = "region_avg"
    index: Mapped[int] = mapped_column(primary_key=True)
    county: Mapped[str] = mapped_column(TEXT)
    beds: Mapped[int] = mapped_column(DOUBLE)
    region: Mapped[str] = mapped_column(TEXT)
    avg: Mapped[int] = mapped_column(DOUBLE)
