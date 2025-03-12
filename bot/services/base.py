from typing import Optional, TypeVar, Generic, Type

from sqlalchemy import select

from bot.db.engine import async_session_maker


T = TypeVar('T')


class BaseService(Generic[T]):
    model: Type[T] = None

    @classmethod
    async def find_by_id(cls, model_id: int) -> Optional[T]:
        async with async_session_maker() as session:
            result = await session.get(cls.model, model_id)
            return result

    @classmethod
    async def find_one_or_none(cls, **filter_by) -> Optional[T]:
        async with async_session_maker() as session:
            stmt = select(cls.model).filter_by(**filter_by)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()

    @classmethod
    async def find_all(cls, **filter_by) -> list[T]:
        async with async_session_maker() as session:
            stmt = select(cls.model).filter_by(**filter_by)
            result = await session.execute(stmt)
            return result.scalars().all()

    @classmethod
    async def insert(cls, **data) -> T:
        async with async_session_maker() as session:
            obj = cls.model(**data)
            session.add(obj)
            await session.commit()
            return obj

    @classmethod
    async def update(cls, model_id: int, **data) -> Optional[T]:
        async with async_session_maker() as session:
            obj = await session.get(cls.model, model_id)
            if obj is None:
                return None
            for key, value in data.items():
                setattr(obj, key, value)
            await session.commit()
            return obj

    @classmethod
    async def delete(cls, model_id: int) -> bool:
        async with async_session_maker() as session:
            obj = await session.get(cls.model, model_id)
            if obj is None:
                return False
            await session.delete(obj)
            await session.commit()
            return True
