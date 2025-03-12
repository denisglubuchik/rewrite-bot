from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from bot.db.models.base import Base, big_int_pk


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[big_int_pk]
    username: Mapped[str] = mapped_column(String(64), nullable=False, default='')
    user_goals: Mapped[str] = mapped_column(String(256), nullable=True, default='')
    tg_channel_id: Mapped[int] = mapped_column(nullable=True, default=None)

    thread: Mapped["UserThreadsModel"] = relationship("UserThreadsModel", back_populates="user", uselist=False)


class UserThreadsModel(Base):
    __tablename__ = "user_threads"

    user_id: Mapped[big_int_pk] = mapped_column(ForeignKey("users.id"))
    thread_id: Mapped[str] = mapped_column(String(64), nullable=False)

    user: Mapped["UserModel"] = relationship("UserModel", back_populates="thread", uselist=False)
