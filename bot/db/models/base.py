from datetime import datetime
from typing import Annotated

from sqlalchemy import DateTime, func, BigInteger, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

int_pk = Annotated[int, mapped_column(primary_key=True, unique=True, autoincrement=False)]
big_int_pk = Annotated[int, mapped_column(primary_key=True, unique=True, autoincrement=False, type_=BigInteger)]
created_at = Annotated[datetime, mapped_column(server_default=text("TIMEZONE('utc', now())"))]


class Base(DeclarativeBase):
    created: Mapped[created_at] = mapped_column(DateTime(timezone=True), default=func.now(), server_default=func.now())

    repr_cols_num: int = 3  # print first columns
    repr_cols: tuple = ()  # extra printed columns

    def __repr__(self) -> str:
        cols = [
            f"{col}={getattr(self, col)}"
            for idx, col in enumerate(self.__table__.columns.keys())
            if col in self.repr_cols or idx < self.repr_cols_num
        ]
        return f"<{self.__class__.__name__} {', '.join(cols)}>"
