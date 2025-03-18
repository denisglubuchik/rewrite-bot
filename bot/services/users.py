import logging

from sqlalchemy import select, delete

from bot.db.engine import async_session_maker
from bot.db.models.users import UserModel, UserThreadsModel
from bot.services.base import BaseService


class UsersService(BaseService[UserModel]):
    model = UserModel

    @classmethod
    async def get_user_goals(cls, user_id: int) -> str:
        async with async_session_maker() as session:
            stmt = select(cls.model.user_goals).filter_by(id=user_id)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()

    @classmethod
    async def get_tg_channel_id(cls, user_id):
        user = await cls.find_by_id(model_id=user_id)
        logging.info(user)
        if user and user.tg_channel_id is not None:
            return user.tg_channel_id
        return None


class UserThreadsService(BaseService[UserThreadsModel]):
    model = UserThreadsModel

    @classmethod
    async def get_user_thread(cls, user_id: int) -> model:
        async with async_session_maker() as session:
            stmt = select(cls.model).filter_by(user_id=user_id)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()


    @classmethod
    async def create_user_thread(cls, thread_id: str, user_id: int) -> model:
        async with async_session_maker() as session:
            await session.execute(
                delete(cls.model).where(cls.model.user_id == user_id)
            )
            thread = cls.model(thread_id=thread_id, user_id=user_id)
            session.add(thread)
            await session.commit()
            return thread