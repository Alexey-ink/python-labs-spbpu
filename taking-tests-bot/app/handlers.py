from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command

import app.database.requests as rq
import app.keybords as kb

from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command

from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

import app.database.requests as rq
import app.keybords as kb


class Form(StatesGroup):
    waiting_for_category_name = State()  # Ожидание ввода названия категории
    waiting_for_test_name = State()  # Ожидание ввода названия теста
    waiting_for_question_text = State()  # Ожидание ввода текста вопроса
    waiting_for_question_options = State()  # Ожидание ввода вариантов для вопроса
    waiting_for_correct_option = State()  # Ожидание выбора правильного ответа для вопроса
    
router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    await rq.set_user(message.from_user.id)
    await message.answer(f"Вас приветствует бот для прохождения тестов!\nВыберите пункт меню: ", reply_markup=kb.main)


@router.callback_query(F.data =='new-test')
async def new_test(callback: CallbackQuery):
    await callback.answer('')
    await callback.message.edit_text(
        text="Выберите тематику или создайте новую:",
        reply_markup= await kb.choose_category()
    )


@router.callback_query(F.data == 'create_new_category')
async def create_new_category(callback: CallbackQuery):
    await callback.answer('')
    await callback.message.edit_text(
        text="Введите название новой тематики:",
    )

@router.message(F.text)
async def process_new_category(message: Message):
    topic_name = message.text.strip()

    if not topic_name:
        await message.answer("Название категории не может быть пустым. Попробуйте снова.")
        return

    try:
        await rq.new_category(topic_name)
        await message.answer(f"Категория '{topic_name}' успешно создана!", reply_markup=await kb.choose_category())
    except Exception as e:
        await message.answer(f"Произошла ошибка при создании категории: {e}")


@router.callback_query(F.data =='show-tests')
async def show_tests(callback: CallbackQuery):
    await callback.answer('')
    await callback.message.answer('Тут будет список категорий тестов...')


@router.callback_query(F.data =='take-test')
async def take_test(callback: CallbackQuery):
    await callback.answer('')
    await callback.message.answer('Выберите категорию товара', reply_markup= await kb.categories())



@router.callback_query(F.data == 'to_main')
async def to_main(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        text="Выберите пункт меню:",
        reply_markup=kb.main
    )

@router.message(Form.waiting_for_test_name)
async def process_new_test(message: Message, state: FSMContext):
    test_name = message.text.strip()

    if not test_name:
        await message.answer("Название теста не может быть пустым. Попробуйте снова.")
        return

    try:
        data = await state.get_data()
        category_id = data.get('category_id')

        # Создаем тест и проверяем результат
        new_test = await rq.create_test(test_name, category_id)
        if not new_test:
            raise Exception("Не удалось создать тест. Возможно, произошла ошибка в базе данных.")

        # Отправляем клавиатуру с кнопкой для создания вопроса
        await message.answer(
            f"Тест '{test_name}' успешно создан!",
            reply_markup=await kb.test_created_keyboard(new_test.id)  # Используем ID нового теста
        )
        await state.clear()  # Сброс состояния
    except Exception as e:
        await message.answer(f"Произошла ошибка при создании теста: {e}")


@router.callback_query(F.data == 'take-test')
async def take_test(callback: CallbackQuery, state: FSMContext):
    categories = await rq.get_categories()
    
    if not categories:
        await callback.answer("Нет доступных категорий для тестов.")
        return
    
    # Отправляем список категорий для выбора
    keyboard = await kb.categories()
    await callback.message.edit_text(
        text="Выберите категорию для прохождения теста:",
        reply_markup=keyboard
    )
    
    # Устанавливаем состояние для выбора категории
    await state.set_state(Form.waiting_for_category_name)


@router.callback_query(F.data == 'show-tests')
async def show_tests(callback: CallbackQuery):
    await callback.answer('')

    # Получаем все тесты с их категориями
    try:
        tests = await rq.get_all_tests()  # Получаем список всех тестов с категориями

        # Формируем текстовый список тестов
        if tests:
            test_list = "\n".join([f"Тест: {test.title} - Категория: {test.category.name}" for test in tests])
        else:
            test_list = "Нет доступных тестов."

        # Удаляем меню и пересылаем сообщение с тестами
        await callback.message.edit_text("Существующие тесты:\n" + test_list, reply_markup=None)

        # Отправляем главное меню после списка тестов
        await callback.message.answer("Выберите пункт меню:", reply_markup=kb.main)
        
    except Exception as e:
        await callback.message.answer(f"Произошла ошибка при получении тестов: {e}")

@router.callback_query(F.data.startswith('create-question_'))
async def create_question(callback: CallbackQuery, state: FSMContext):
    await callback.answer('')
    
    # Получаем ID теста, к которому нужно добавить вопрос
    test_id = int(callback.data.split('_')[1])  # Получаем ID теста из callback_data

    # Сохраняем ID теста в контексте
    await state.update_data(test_id=test_id)

    # Запрашиваем у пользователя текст вопроса
    await callback.message.edit_text(
        text="Введите текст вопроса для этого теста:"
    )
    await state.set_state(Form.waiting_for_question_text)


@router.message(Form.waiting_for_question_text)
async def process_new_question(message: Message, state: FSMContext):
    question_text = message.text.strip()

    if not question_text:
        await message.answer("Текст вопроса не может быть пустым. Попробуйте снова.")
        return

    # Сохраняем текст вопроса в состоянии и запрашиваем варианты ответов
    await state.update_data(question_text=question_text)
    
    await message.answer("Теперь введите варианты ответа для этого вопроса (по одному на каждое сообщение):")
    
    await state.set_state(Form.waiting_for_question_options)
