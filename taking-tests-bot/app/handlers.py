from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

import app.database.requests as rq
import app.keybords as kb

import logging

class Form(StatesGroup):
    waiting_for_category_name = State()  # Ожидание ввода названия категории
    waiting_for_test_name = State()  # Ожидание ввода названия теста
    waiting_for_question_text = State()  # Ожидание ввода текста вопроса
    waiting_for_question_options = State()  # Ожидание ввода вариантов для вопроса
    waiting_for_correct_option = State()  # Ожидание выбора правильного ответа для вопроса

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    await rq.set_user(
        tg_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name
    )
    await message.answer(
        "Вас приветствует бот для прохождения тестов!\nВыберите пункт меню: ",
        reply_markup=kb.main
    )


@router.callback_query(F.data == 'new-test')
async def new_test(callback: CallbackQuery, state: FSMContext):
    await callback.answer('')
    await callback.message.edit_text(
        text="Выберите тему или создайте новую:",
        reply_markup=await kb.choose_category()
    )

    await state.set_state(Form.waiting_for_category_name)  # Устанавливаем состояние ожидания категории


@router.callback_query(F.data == 'delete-topic-test')
async def handle_delete_topic_test(callback: CallbackQuery):
    """Обработчик для удаления теста или темы."""
    keyboard = InlineKeyboardBuilder()

    keyboard.add(InlineKeyboardButton(text='Удалить тест', callback_data='delete-test'))
    keyboard.add(InlineKeyboardButton(text='Удалить тему', callback_data='delete-topic'))
    keyboard.add(InlineKeyboardButton(text='⏪ Назад', callback_data='to_main'))

    await callback.message.edit_text(
        text="Выберите действие:",
        reply_markup=keyboard.adjust(2).as_markup()
    )

@router.callback_query(F.data == 'delete-test')
async def handle_delete_test(callback: CallbackQuery):
    """Обработчик для выбора теста для удаления."""
    tests = await rq.get_all_tests()  # Получаем список тестов

    if not tests:
        await callback.answer("Нет доступных тестов для удаления.", show_alert=True)
        return

    keyboard = InlineKeyboardBuilder()

    for test in tests:
        keyboard.add(InlineKeyboardButton(text=test.title, callback_data=f'delete_test_{test.id}'))

    keyboard.add(InlineKeyboardButton(text='⏪ Назад', callback_data='delete-topic-test'))


    await callback.message.edit_text(
        text="Выберите тест для удаления:",
        reply_markup=keyboard.adjust(2).as_markup()
    )

@router.callback_query(F.data.startswith('delete_test_'))
async def confirm_delete_test(callback: CallbackQuery):
    """Обработчик подтверждения удаления теста."""
    test_id = int(callback.data.split('_')[2])

    try:
        await rq.delete_test(test_id)  # Функция для удаления теста из базы данных
        await callback.message.edit_text("Тест успешно удален.", reply_markup=None)
        await callback.message.answer("Выберите пункт меню:", reply_markup=kb.main)
        
    except Exception as e:
        await callback.message.answer(f"Ошибка при удалении теста: {e}")

@router.callback_query(F.data == 'delete-topic')
async def handle_delete_topic(callback: CallbackQuery):
    """Обработчик для выбора темы для удаления."""
    categories = await rq.get_categories()  # Получаем список всех категорий

    if not categories:
        await callback.answer("Нет доступных тем для удаления.", show_alert=True)
        return

    keyboard = InlineKeyboardBuilder()

    for category in categories:
        keyboard.add(InlineKeyboardButton(text=category.name, callback_data=f'delete_category_{category.id}'))

    keyboard.add(InlineKeyboardButton(text='⏪ Назад', callback_data='delete-topic-test'))

    await callback.message.edit_text(
        text="Выберите тему для удаления:",
        reply_markup=keyboard.adjust(2).as_markup()
    )

@router.callback_query(F.data.startswith('delete_category_'))
async def confirm_delete_category(callback: CallbackQuery):
    """Обработчик подтверждения удаления категории."""
    category_id = int(callback.data.split('_')[2])

    try:
        await rq.delete_category(category_id)  # Функция для удаления категории из базы данных
        await callback.message.edit_text("Тема успешно удалена.", reply_markup=None)
        await callback.message.answer("Выберите пункт меню:", reply_markup=kb.main)
    except Exception as e:
        await callback.message.answer(f"Ошибка при удалении темы: {e}")



@router.callback_query(F.data == 'create_new_category')
async def create_new_category(callback: CallbackQuery, state: FSMContext):
    await callback.answer('')
    await callback.message.edit_text(
        text="Введите название новой темы для тестов",
    )
    await state.set_state(Form.waiting_for_category_name)  # Ожидание ввода категории


@router.message(Form.waiting_for_category_name)
async def process_new_category(message: Message, state: FSMContext):
    topic_name = message.text.strip()

    try:
        await rq.new_category(topic_name)
        await message.answer(f"Тема '{topic_name}' успешно создана!")
        await message.answer(
            text="Выберите тему или создайте новую:",
            reply_markup=await kb.choose_category()
            )
        await state.clear() # Сброс состояния
    except Exception as e:
        await message.answer(f"Произошла ошибка при создании категории: {e}")


@router.callback_query(F.data.startswith('category_'))
async def choose_category(callback: CallbackQuery, state: FSMContext):
    category_id = int(callback.data.split('_')[1])  # Получаем ID категории
    await callback.answer('')
    await callback.message.edit_text(
        text="Введите название нового теста:",
    )
    await state.update_data(category_id=category_id)  # Сохраняем выбранную категорию в контексте
    await state.set_state(Form.waiting_for_test_name)  # Ожидание ввода теста


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
    try:
        tests = await rq.get_all_tests()  # Получаем список всех тестов с категориями

        # Формируем текстовый список тестов
        if tests:
            test_list = "\n".join([f"<i>📝</i> <b> {test.title} </b> - <i>Тема:</i> {test.category.name}\n" for test in tests])
        else:
            test_list = "<i>Нет доступных тестов.</i>"

        # Удаляем меню и пересылаем сообщение с тестами
        await callback.message.edit_text(
            text=f"<b>Существующие тесты:\n</b>\n{test_list}",
            reply_markup=None,
            parse_mode="HTML"
        )

        # Отправляем главное меню после списка тестов
        await callback.message.answer("Выберите пункт меню:", reply_markup=kb.main, parse_mode="HTML")

    except Exception as e:
        await callback.message.answer(f"Произошла ошибка при получении тестов: <i>{e}</i>", parse_mode="HTML")



@router.callback_query(F.data.startswith('test_'))
async def start_test(callback: CallbackQuery, state: FSMContext):
    test_id = int(callback.data.split('_')[1])  # Получаем ID выбранного теста
    data = await state.get_data()
    category_id = data.get('category_id')

    # Получаем информацию о выбранном тесте
    test = await rq.get_test_by_id(test_id)
    
    if not test:
        await callback.answer("Тест не найден.")
        return

    # Пример начала теста — можно добавить логику для этого
    await callback.message.edit_text(
        text=f"Начинаем тест: {test.title}. Удачи!",
        reply_markup=kb.start_test_keyboard() 
    )


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


@router.message(Form.waiting_for_question_options)
async def process_question_options(message: Message, state: FSMContext):
    options = message.text.strip()

    if not options:
        await message.answer("Вариант ответа не может быть пустым. Попробуйте снова.")
        return

    # Добавляем вариант в список вариантов
    data = await state.get_data()
    question_options = data.get('question_options', [])

    # Проверяем, что количество вариантов не превышает 4
    if len(question_options) >= 4:
        await message.answer("Максимальное количество вариантов ответа — 4. Пожалуйста, завершите ввод.")
        return

    question_options.append(options)
    await state.update_data(question_options=question_options)

    # Запрашиваем следующий вариант ответа
    if len(question_options) < 4:
        await message.answer("Введите следующий вариант ответа или отправьте 'Готово', чтобы завершить создание вопроса.")
    else:
        await message.answer("Введите правильный вариант ответа (число от 1 до 4):")
        await state.set_state(Form.waiting_for_correct_option)


@router.message(Form.waiting_for_correct_option)
async def process_correct_option(message: Message, state: FSMContext):
    try:
        correct_option = int(message.text.strip())

        if correct_option < 1 or correct_option > 4:
            await message.answer("Номер правильного ответа должен быть от 1 до 4. Попробуйте снова.")
            return

        # Логируем данные состояния
        data = await state.get_data()
        logging.info(f"Полученные данные: {data}")

        question_text = data.get('question_text')
        question_options = data.get('question_options', [])

        if len(question_options) < 4:
            await message.answer("Недостаточное количество вариантов ответа. Проверьте ввод.")
            return

        # Сохраняем correct_option в состоянии
        await state.update_data(correct_option=correct_option)

        # Получаем все данные из состояния
        data = await state.get_data()

        # Логируем перед записью в базу данных
        logging.info(f"Добавляем вопрос: {question_text}, варианты: {question_options}, правильный: {correct_option}")

        # Добавляем новый вопрос с вариантами
        await rq.create_question(
            question_text=question_text,
            options=question_options,
            correct_option=correct_option,
            test_id=data.get('test_id')
        )

        await message.answer(f"Вопрос с вариантами ответов успешно добавлен!", reply_markup=kb.main)
        await state.clear()

    except ValueError:
        await message.answer("Номер правильного ответа должен быть числом. Попробуйте снова.")
    except Exception as e:
        logging.error(f"Ошибка при добавлении вопроса: {e}")
        await message.answer(f"Произошла ошибка: {e}")



@router.callback_query(F.data == "add-delete-tests")
async def handle_add_delete_tests(callback: CallbackQuery):
    keyboard = await kb.categories_tests()
    await callback.message.edit_text(
        text="Выберите тему, чтобы увидеть тесты:",
        reply_markup=keyboard
    )


@router.callback_query(F.data.startswith("category-tests_"))
async def handle_category_selection(callback: CallbackQuery):
    category_id = int(callback.data.split("_")[1])
    
    # Получаем тесты в категории
    tests = await rq.get_tests_by_category(category_id)
    
    if not tests:
        await callback.answer("По этой теме тестов нет.", show_alert=True)  # Используйте show_alert для уведомления
        return

    keyboard = InlineKeyboardBuilder()

    for test in tests:
        keyboard.add(InlineKeyboardButton(text=test.title, callback_data=f"edit-test_{test.id}"))

    keyboard.add(InlineKeyboardButton(text="⏪ Назад к категориям", callback_data="add-delete-tests"))
    keyboard.add(InlineKeyboardButton(text="⭕️ Главное меню", callback_data="to_main"))
    
    await callback.message.edit_text(
        text="Выберите тест для добавления или удаления вопросов:",
        reply_markup=keyboard.adjust(1).as_markup()
    )


@router.callback_query(F.data.startswith("edit-test_"))
async def handle_test_selection(callback: CallbackQuery):
    test_id = int(callback.data.split("_")[1])
    
    # Клавиатура с действиями
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Добавить вопросы", callback_data=f"add_questions_{test_id}")],
        [InlineKeyboardButton(text="Удалить вопросы", callback_data=f"delete_questions_{test_id}")],
        [InlineKeyboardButton(text="⏪ Назад к тестам", callback_data="add-delete-tests")],
        [InlineKeyboardButton(text="⭕️ Главное меню", callback_data="to_main")]
    ])
    
    await callback.message.edit_text(
        text="Выберите действие для выбранного теста:",
        reply_markup=keyboard
    )


@router.callback_query(F.data.startswith("add_questions_"))
async def handle_add_questions(callback: CallbackQuery, state: FSMContext):
    test_id = int(callback.data.split("_")[2])

    await state.update_data(test_id=test_id)

    await callback.message.edit_text(
        text=f"Добавление вопросов для теста с ID {test_id}. Пожалуйста, следуйте инструкциям."
    )

    await callback.message.answer(
        text="Введите текст вопроса для этого теста:"
    )
    
    # Переходим к состоянию для ввода текста вопроса
    await state.set_state(Form.waiting_for_question_text)
    # Здесь можно запустить FSM для создания вопросов.


@router.callback_query(F.data.startswith("delete_questions_"))
async def handle_delete_questions(callback: CallbackQuery):
    test_id = int(callback.data.split("_")[2])

    # Получаем вопросы для теста с уникальными данными
    questions = await rq.get_questions_by_test(test_id)
    keyboard = InlineKeyboardBuilder()
    
    for question in questions:
        keyboard.add(InlineKeyboardButton(text=question.question_text, callback_data=f"delete_question_{question.id}"))
    
    keyboard.add(InlineKeyboardButton(text="⏪ Назад", callback_data=f"edit-test_{test_id}"))
    keyboard.add(InlineKeyboardButton(text="⭕️ Главное меню", callback_data="to_main"))

    await callback.message.edit_text(
        text="Выберите вопрос для удаления:",
        reply_markup=keyboard.adjust(1).as_markup()
    )

@router.callback_query(F.data.startswith("delete_question_"))
async def handle_delete_question(callback: CallbackQuery, state: FSMContext):
    # Извлекаем ID вопроса из callback_data
    question_id = int(callback.data.split("_")[2])

    try:
        # Получаем вопрос по ID
        question = await rq.get_question_by_id(question_id)
        
        if not question:
            await callback.answer("Вопрос не найден.")
            return
        
        # Удаляем вопрос из базы данных
        await rq.delete_question(question_id)

        # Отправляем уведомление пользователю
        await callback.message.edit_text(
            text=f"Вопрос '{question.question_text}' успешно удален.",
            reply_markup=None  # Можно добавить клавиатуру после удаления, если необходимо
        )
        
        # Вы можете переслать пользователя к предыдущему меню, если нужно
        await callback.message.answer("Выберите пункт меню:", reply_markup=kb.main)

    except Exception as e:
        # Обработка ошибок
        logging.error(f"Ошибка при удалении вопроса: {e}")
        await callback.answer(f"Произошла ошибка при удалении вопроса: {e}")


@router.callback_query(F.data == 'to_main')
async def to_main(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        text="Выберите пункт меню:",
        reply_markup=kb.main
    )
