from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from database.models import Base
from config import DATABASE_URL

engine = create_async_engine(DATABASE_URL, echo=False)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def init_db():
    """Create all tables on startup."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_or_create_user(session: AsyncSession, user_id: int, username: str | None, first_name: str | None):
    from sqlalchemy import select
    from database.models import User

    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        user = User(id=user_id, username=username, first_name=first_name)
        session.add(user)
        await session.commit()

    return user


async def update_user_numerology(session: AsyncSession, user_id: int, birth_date: str,
                                  belova_number: int, psychomatrix: str):
    from sqlalchemy import select
    from database.models import User

    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user:
        user.birth_date = birth_date
        user.belova_number = belova_number
        user.psychomatrix = psychomatrix
        await session.commit()

    return user


async def create_booking(session: AsyncSession, user_id: int, preferred_time: str, contact_info: str):
    from database.models import Booking

    booking = Booking(user_id=user_id, preferred_time=preferred_time, contact_info=contact_info)
    session.add(booking)
    await session.commit()
    return booking


async def get_user(session: AsyncSession, user_id: int):
    from sqlalchemy import select
    from database.models import User

    result = await session.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()
