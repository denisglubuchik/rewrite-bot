from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from bot.core.config import settings

DB_URL = "sqlite+aiosqlite:///" + settings.DB_PATH
engine = create_async_engine(DB_URL)
async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
