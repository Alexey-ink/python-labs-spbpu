from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from app.database.requests import get_categories

from aiogram.utils.keyboard import InlineKeyboardBuilder

main = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Создать новый тест', callback_data = 'new-test')],
    [InlineKeyboardButton(text='Посмотреть существующие тесты', callback_data = 'show-tests')],
    [InlineKeyboardButton(text='Пройти тест по выбору', callback_data = 'take-test')]
    ]
)

async def categories():
    all_categories = await get_categories()
    keyboard = InlineKeyboardBuilder()

    for category in all_categories:
        keyboard.add(InlineKeyboardButton(text=category.name, callback_data=f"category_{category.id}"))
    keyboard.add(InlineKeyboardButton(text='На главную', callback_data='to_main'))
    return keyboard.adjust(2).as_markup()


async def categories():
    all_categories = await get_categories()
    keyboard = InlineKeyboardBuilder()

    for category in all_categories:
        keyboard.add(InlineKeyboardButton(text=category.name, callback_data=f"category_{category.id}"))
    keyboard.add(InlineKeyboardButton(text='На главную', callback_data='to_main'))
    return keyboard.adjust(2).as_markup()

async def choose_category():
    all_categories = await get_categories()
    keyboard = InlineKeyboardBuilder()

    for category in all_categories:
        keyboard.add(InlineKeyboardButton(text=category.name, callback_data=f"category_{category.id}"))
    keyboard.add(InlineKeyboardButton(text='Создать новую тематику', callback_data='create_new_category'))
    keyboard.add(InlineKeyboardButton(text='Назад', callback_data='to_main'))
    return keyboard.adjust(2).adjust(1, 1).as_markup()

async def test_created_keyboard(test_id: int) -> InlineKeyboardMarkup:
    # Это клавиатура для пользователя, которая появляется после создания теста
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Создать вопрос", callback_data=f"create-question_{test_id}")],
            [InlineKeyboardButton(text="Главное меню", callback_data="to_main")]
        ]
    )

