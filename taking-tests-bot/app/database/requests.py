from app.database.models import async_session
from app.database.models import User, Category,Test, Question, Option
from sqlalchemy import select, text
from typing import Optional
from sqlalchemy.orm import selectinload
from sqlalchemy.future import select

from sqlalchemy.orm import joinedload
import logging

async def set_user(tg_id: int, username: Optional[str] = None, first_name: Optional[str] = None, last_name: Optional[str] = None):
    async with async_session() as session:
        user = await session.execute(
            select(User).where(User.tg_id == tg_id)
        )
        user = user.scalars().first()

        if not user:
            new_user = User(
                tg_id=tg_id,
                username=username,
                first_name=first_name,
                last_name=last_name
            )
            session.add(new_user)
        else:
            user.username = username
            user.first_name = first_name
            user.last_name = last_name

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
            
            new_test = Test(title=test_name, category_id=category_id)
            session.add(new_test)

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
        result = await session.scalars(
            select(Test).options(joinedload(Test.category))  # Используем joinedload для загрузки категории
            .order_by(Test.id)
        )
        return result.all()
    

async def get_questions_by_test(test_id: int):
    async with async_session() as session:
        result = await session.execute(
            select(Question)
            .where(Question.test_id == test_id)
            .options(selectinload(Question.options))  # Используем selectinload для подгрузки связанных коллекций
        )
        questions = result.scalars().all()  # Получаем список вопросов
        return questions


async def create_question(question_text: str, options: list[str], correct_option: int, test_id: int):
    if correct_option < 1 or correct_option > len(options):
        raise ValueError("Номер правильного ответа выходит за пределы допустимого диапазона.")

    async with async_session() as session:
        test = await session.get(Test, test_id)
        if not test:
            raise ValueError(f"Тест с ID {test_id} не найден.")


        question = Question(question_text=question_text, correct_option=correct_option, test_id=test_id)
        session.add(question)
        await session.commit()
        await session.refresh(question)

        option_objects = [
            Option(option_text=option_text, question_id=question.id)
            for option_text in options
        ]
        session.add_all(option_objects)
        await session.commit()

        return question


async def get_questions_by_test(test_id: int):
    async with async_session() as session:
        result = await session.scalars(
            select(Question)
            .where(Question.test_id == test_id)
            .options(selectinload(Question.options))  # Используем selectinload вместо joinedload
        )
        return result.all()
    
async def get_tests_by_category(category_id: int):
    """
    Получает список тестов по ID категории.

    :param category_id: ID категории
    :return: Список объектов Test
    """
    async with async_session() as session:
        result = await session.execute(
            select(Test).where(Test.category_id == category_id)
        )
        return result.scalars().all()
    

async def delete_question(question_id: int):
    async with async_session() as session:
        # Получаем вопрос по ID
        question = await session.get(Question, question_id)
        
        if question:
            await session.delete(question)
            await session.commit()
        else:
            # Возвращаем ошибку, если вопрос не найден
            raise Exception(f"Вопрос с ID {question_id} не найден.")
        

async def get_question_by_id(question_id: int):
    async with async_session() as session:
        result = await session.execute(
            select(Question).where(Question.id == question_id)
        )
        question = result.scalars().first()  # Получаем первый результат (должен быть один вопрос или None)
        return question
    

async def get_test_by_id(test_id: int):
    async with async_session() as session:
        result = await session.execute(
            select(Test).where(Test.id == test_id)
        )
        test = result.scalars().first()  # Получаем первый результат (должен быть один тест или None)
        return test
    

async def delete_category(category_id: int):
    async with async_session() as session:

        # Включаем поддержку внешних ключей для SQLite
        await session.execute(text("PRAGMA foreign_keys = ON;"))
        
        category = await session.get(Category, category_id)
        if category:
            tests_to_delete = await session.scalars(select(Test).where(Test.category_id == category_id))
            for test in tests_to_delete:
                await session.delete(test)
            await session.commit()

            # Теперь удаляем саму категорию
            await session.delete(category)
            await session.commit()
        else:
            raise ValueError("Категория не найдена.")
        
async def delete_test(test_id: int):
    async with async_session() as session:
        # Включаем поддержку внешних ключей для SQLite
        await session.execute(text("PRAGMA foreign_keys = ON;"))

        # Получаем тест по ID
        test = await session.get(Test, test_id)
        
        if test:
            # Удаляем все вопросы, связанные с тестом
            questions_to_delete = await session.scalars(select(Question).where(Question.test_id == test_id))
            for question in questions_to_delete:
                await session.delete(question)
            await session.commit()

            # Удаляем сам тест
            await session.delete(test)
            await session.commit()
        else:
            raise ValueError(f"Тест с ID {test_id} не найден.")