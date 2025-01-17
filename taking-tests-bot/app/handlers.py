from aiogram import F, Router, types
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

import app.database.requests as rq
import app.keybords as kb
import random

import logging

class Form(StatesGroup):
    waiting_for_category_name = State()  # Ожидание ввода названия категории
    waiting_for_test_name = State()  # Ожидание ввода названия теста
    waiting_for_question_text = State()  # Ожидание ввода текста вопроса
    waiting_for_question_options = State()  # Ожидание ввода вариантов для вопроса
    waiting_for_correct_option = State()  # Ожидание выбора правильного ответа для вопроса
    testing = State()

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
    tests = await rq.get_all_tests() 

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
        await rq.delete_test(test_id)
        await callback.message.edit_text("Тест успешно удален.", reply_markup=None)
        await callback.message.answer("Выберите пункт меню:", reply_markup=kb.main)
        
    except Exception as e:
        await callback.message.answer(f"Ошибка при удалении теста: {e}")

@router.callback_query(F.data == 'delete-topic')
async def handle_delete_topic(callback: CallbackQuery):
    """Обработчик для выбора темы для удаления."""
    categories = await rq.get_categories()

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
        await rq.delete_category(category_id) 
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
    await state.set_state(Form.waiting_for_category_name) 


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
        await state.clear()
    except Exception as e:
        await message.answer(f"Произошла ошибка при создании категории: {e}")


@router.callback_query(F.data.startswith('category_'))
async def choose_category(callback: CallbackQuery, state: FSMContext):
    category_id = int(callback.data.split('_')[1])  
    await callback.answer('')
    await callback.message.edit_text(
        text="Введите название нового теста:",
    )
    await state.update_data(category_id=category_id) 
    await state.set_state(Form.waiting_for_test_name)  


@router.message(Form.waiting_for_test_name)
async def process_new_test(message: Message, state: FSMContext):
    test_name = message.text.strip()

    if not test_name:
        await message.answer("Название теста не может быть пустым. Попробуйте снова.")
        return

    try:
        data = await state.get_data()
        category_id = data.get('category_id')


        new_test = await rq.create_test(test_name, category_id)
        if not new_test:
            raise Exception("Не удалось создать тест. Возможно, произошла ошибка в базе данных.")

        await message.answer(
            f"Тест '{test_name}' успешно создан!",
            reply_markup=await kb.test_created_keyboard(new_test.id) 
        )
        await state.clear()
    except Exception as e:
        await message.answer(f"Произошла ошибка при создании теста: {e}")


@router.callback_query(F.data == 'show-tests')
async def show_tests(callback: CallbackQuery):
    await callback.answer('')
    try:
        tests = await rq.get_all_tests()

        if tests:
            test_list = "\n".join([f"<i>📝</i> <b> {test.title} </b> - <i>Тема:</i> {test.category.name}\n" for test in tests])
        else:
            test_list = "<i>Нет доступных тестов.</i>"

        await callback.message.edit_text(
            text=f"<b>Существующие тесты:\n</b>\n{test_list}",
            reply_markup=None,
            parse_mode="HTML"
        )

        await callback.message.answer("Выберите пункт меню:", reply_markup=kb.main, parse_mode="HTML")

    except Exception as e:
        await callback.message.answer(f"Произошла ошибка при получении тестов: <i>{e}</i>", parse_mode="HTML")


@router.callback_query(F.data.startswith('create-question_'))
async def create_question(callback: CallbackQuery, state: FSMContext):
    await callback.answer('')
    
    test_id = int(callback.data.split('_')[1]) 
    await state.update_data(test_id=test_id)

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

    await state.update_data(question_text=question_text)
    
    await message.answer("Теперь введите варианты ответа для этого вопроса (по одному на каждое сообщение):")
    
    await state.set_state(Form.waiting_for_question_options)


@router.message(Form.waiting_for_question_options)
async def process_question_options(message: Message, state: FSMContext):
    options = message.text.strip()

    if not options:
        await message.answer("Вариант ответа не может быть пустым. Попробуйте снова.")
        return

    data = await state.get_data()
    question_options = data.get('question_options', [])

    if len(question_options) >= 4:
        await message.answer("Максимальное количество вариантов ответа — 4. Пожалуйста, завершите ввод.")
        return

    question_options.append(options)
    await state.update_data(question_options=question_options)

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

        data = await state.get_data()
        logging.info(f"Полученные данные: {data}")

        question_text = data.get('question_text')
        question_options = data.get('question_options', [])

        if len(question_options) < 4:
            await message.answer("Недостаточное количество вариантов ответа. Проверьте ввод.")
            return

        await state.update_data(correct_option=correct_option)

        data = await state.get_data()

        logging.info(f"Добавляем вопрос: {question_text}, варианты: {question_options}, правильный: {correct_option}")

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
        text="Выберите тест для добавления или удаления вопроса:",
        reply_markup=keyboard.adjust(1).as_markup()
    )


@router.callback_query(F.data.startswith("edit-test_"))
async def handle_test_selection(callback: CallbackQuery):
    test_id = int(callback.data.split("_")[1])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Добавить вопрос", callback_data=f"add_questions_{test_id}")],
        [InlineKeyboardButton(text="Удалить вопрос", callback_data=f"delete_questions_{test_id}")],
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
    
    await state.set_state(Form.waiting_for_question_text)


@router.callback_query(F.data.startswith("delete_questions_"))
async def handle_delete_questions(callback: CallbackQuery):
    test_id = int(callback.data.split("_")[2])

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
    question_id = int(callback.data.split("_")[2])

    try:
        question = await rq.get_question_by_id(question_id)
        
        if not question:
            await callback.answer("Вопрос не найден.")
            return
        
        await rq.delete_question(question_id)

        await callback.message.edit_text(
            text=f"Вопрос '{question.question_text}' успешно удален.",
            reply_markup=None 
        )
        
        await callback.message.answer("Выберите пункт меню:", reply_markup=kb.main)

    except Exception as e:
        # Обработка ошибок
        logging.error(f"Ошибка при удалении вопроса: {e}")
        await callback.answer(f"Произошла ошибка при удалении вопроса: {e}")



@router.callback_query(F.data == 'take-test')
async def take_test(callback: CallbackQuery, state: FSMContext):
    """Обработчик для выбора категории теста."""
    categories = await rq.get_categories()

    if not categories:
        await callback.message.edit_text(
            text="К сожалению, пока нет доступных категорий для тестов. ⭕️ Главное меню",
            reply_markup=kb.main 
        )
        return

    keyboard = kb.create_category_keyboard(categories)

    await callback.message.edit_text(
        text="Выберите категорию для прохождения теста:",
        reply_markup=keyboard
    )

    await state.set_state(Form.waiting_for_category_name)


@router.callback_query(F.data.startswith("exam-category_"))
async def category_tests_handler(callback: types.CallbackQuery):
    """Показывает доступные тесты в выбранной категории."""
    category_id = int(callback.data.split("_")[1]) 
    tests = await rq.get_tests_by_category(category_id)

    if not tests:
        await callback.message.edit_text(
            "В этой категории пока нет тестов. ⭕️ Главное меню",
            reply_markup=kb.main
        )
        return

    keyboard = kb.create_test_keyboard(tests)

    await callback.message.edit_text(
        "Выберите тест, который хотите пройти:",
        reply_markup=keyboard,
    )


@router.callback_query(F.data.startswith("start-test_"))
async def start_test(callback: CallbackQuery, state: FSMContext):
    """Обработчик для начала теста."""
    try:
        test_id = int(callback.data.split("_")[1]) 
        test = await rq.get_test_by_id(test_id)

        if not test:
            await callback.message.answer("Этот тест не найден.")
            return

        questions = await rq.get_questions_by_test(test_id)

        if not questions:
            await callback.message.answer("В этом тесте нет вопросов.")
            return

        await callback.message.delete()

        await callback.message.answer(f"Тест на тему «{test.title}» начат! Удачи :)")

        # Сохраняем данные теста в состоянии
        await state.update_data(test_id=test.id, current_question=0, score=0, total_questions=len(questions))

        # Устанавливаем состояние для теста
        await state.set_state(Form.testing)  # Устанавливаем состояние "тестирование"

        # Отправляем первый вопрос
        await send_question(callback.message, questions[0], state)

    except Exception as e:
        await callback.message.answer(f"Ошибка при запуске теста: {e}")


@router.message(Form.testing)
async def answer_question(message: Message, state: FSMContext):
    """Обработчик для ответа на вопрос теста."""
    try:
        # Получаем данные из состояния
        user_data = await state.get_data()
        current_question_index = user_data.get('current_question', 0)

        # Получаем вопросы и правильный ответ для текущего вопроса
        test_id = user_data.get('test_id')
        questions = await rq.get_questions_by_test(test_id)
        question = questions[current_question_index]
        correct_answer = question.options[question.correct_option - 1].option_text

        user_answer = message.text.strip()  # Ответ пользователя

        # Получаем текущий балл и количество правильных ответов
        score = user_data.get('score', 0)

        # Проверка правильности ответа
        if user_answer == correct_answer:
            score += 1  # Увеличиваем баллы, если ответ правильный
            await message.answer("Правильный ответ! 🎉")
        else:
            await message.answer(f"Неправильный ответ! 😞 Правильный: {correct_answer}")

        # Обновляем данные в состоянии
        await state.update_data(score=score) 

        # Переход к следующему вопросу
        current_question_index += 1  # Увеличиваем индекс после проверки ответа

        if current_question_index < len(questions):
            await state.update_data(current_question=current_question_index)
            await send_question(message, questions[current_question_index], state)
        else:
            # Тест завершен, выводим итоговый результат
            total_questions = user_data.get('total_questions', 0)
            await message.answer(
                f"Тест завершен! Вы набрали {score} баллов из {total_questions}.",
                reply_markup=kb.main 
            )
            await state.clear()  # Очищаем состояние

    except Exception as e:
        await message.answer(f"Ошибка: {e}")


async def send_question(message: Message, question, state: FSMContext):
    """Отправка вопроса пользователю с обычной клавиатурой."""
    options = [option.option_text for option in question.options]

    correct_answer = options[question.correct_option - 1]
    random.shuffle(options)

    await state.update_data(correct_answer=correct_answer)

    keyboard_buttons = []
    row = []
    for i, option in enumerate(options):
        row.append(KeyboardButton(text=option)) 
        if (i + 1) % 2 == 0 or i == len(options) - 1:
            keyboard_buttons.append(row) 
            row = []

    keyboard = ReplyKeyboardMarkup(
        keyboard=keyboard_buttons,
        resize_keyboard=True,
        one_time_keyboard=True
    )

    await message.answer(
        f"Вопрос: {question.question_text}",
        reply_markup=keyboard
    )


@router.callback_query(F.data == 'to_main')
async def to_main(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        text="Выберите пункт меню:",
        reply_markup=kb.main
    )