import datetime

from sqlalchemy import DATETIME, DOUBLE, TEXT
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class addressData(Base):
    __tablename__ = "address_data"
    index: Mapped[int] = mapped_column(primary_key=True)
    county: Mapped[str] = mapped_column(TEXT)
    region: Mapped[str] = mapped_column(TEXT)
    area: Mapped[str] = mapped_column(TEXT)
    price: Mapped[int] = mapped_column(DOUBLE)
    beds: Mapped[int] = mapped_column(DOUBLE)
    rawAddress: Mapped[str] = mapped_column(TEXT)
    sqrMetres: Mapped[int] = mapped_column(DOUBLE)
    pricePerSqrMetres: Mapped[int] = mapped_column(DOUBLE)
    saleDate: Mapped[datetime.datetime] = mapped_column(DATETIME)
    location: Mapped[str] = mapped_column(TEXT)
