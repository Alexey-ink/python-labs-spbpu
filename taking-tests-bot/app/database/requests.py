from app.database.models import async_session
from app.database.models import User, Category
from sqlalchemy import select


async def set_user(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))

        if not user:
            session.add(User(tg_id=tg_id))
            await session.commit()

async def get_categories():
    async with async_session() as session:
        return await session.scalars(select(Category))
    

async def new_category(topic: str):
    async with async_session() as session:
        # Проверка, существует ли категория с таким названием
        result = await session.execute(select(Category).filter(Category.name == topic))
        existing_category = result.scalar_one_or_none()

        if not existing_category:
            new_cat = Category(name=topic)
            session.add(new_cat)
            await session.commit()
