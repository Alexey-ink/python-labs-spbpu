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

async def create_test(test_name: str, category_id: int):
    try:
        async with async_session() as session:  # Используем асинхронный контекст сессии
            # Проверяем, существует ли категория
            category = await session.get(Category, category_id)
            if not category:
                raise Exception(f"Категория с ID {category_id} не найдена")
            
            # Создаем новый тест
            new_test = Test(title=test_name, category_id=category_id)
            session.add(new_test)

            # Коммитим изменения в базе данных
            await session.commit()

            # Получаем обновленные данные о новом тесте
            await session.refresh(new_test)

            logging.info(f"Тест '{test_name}' с ID {new_test.id} успешно создан")
            return new_test

    except Exception as e:
        logging.error(f"Ошибка при создании теста: {e}")
        raise Exception(f"Не удалось создать тест: {e}")


async def get_user_category(tg_id: int):
    async with async_session() as session:
        # Получаем категорию пользователя, если она была выбрана
        user_category = await session.scalar(select(Category).where(Category.id == tg_id))
        if not user_category:
            raise ValueError("Категория не была выбрана.")
        return user_category.id


async def get_all_tests():
    async with async_session() as session:
        # Получаем все тесты с их категориями, используя joinedload для загрузки связанных категорий
        result = await session.scalars(
            select(Test).options(joinedload(Test.category))  # Используем joinedload для загрузки категории
            .order_by(Test.id)
        )
        return result.all()  # Возвращаем все тесты


async def create_question(question_text: str, options: list[str], correct_option: int, test_id: int):
    if correct_option < 1 or correct_option > len(options):
        raise ValueError("Номер правильного ответа выходит за пределы допустимого диапазона.")

    async with async_session() as session:
        test = await session.get(Test, test_id)
        if not test:
            raise ValueError(f"Тест с ID {test_id} не найден.")

        # Создаем вопрос
        question = Question(question_text=question_text, test_id=test_id)
        session.add(question)
        await session.commit()
        await session.refresh(question)

        # Создаем варианты ответов
        option_objects = [
            Option(text=option_text, question_id=question.id, is_correct=(index + 1 == correct_option))
            for index, option_text in enumerate(options)
        ]
        session.add_all(option_objects)
        await session.commit()

        return question

