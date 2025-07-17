from sqlalchemy import DOUBLE, TEXT
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class PMXYoYRegion(Base):
    __tablename__ = "region_yoy"
    index: Mapped[int] = mapped_column(primary_key=True)
    yoy: Mapped[int] = mapped_column(DOUBLE)
    region: Mapped[str] = mapped_column(TEXT)
    beds: Mapped[int] = mapped_column(DOUBLE)
    county: Mapped[str] = mapped_column(TEXT)
