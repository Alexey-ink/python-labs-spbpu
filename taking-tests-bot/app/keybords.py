from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from app.database.requests import get_categories

from aiogram.utils.keyboard import InlineKeyboardBuilder


main = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Создать новый тест', callback_data = 'new-test')],
    [InlineKeyboardButton(text='Посмотреть существующие тесты', callback_data = 'show-tests')],
    [InlineKeyboardButton(text='Добавить или удалить вопросы', callback_data = 'add-delete-tests')],
    [InlineKeyboardButton(text='Удалить тест или тему', callback_data = 'delete-topic-test')],
    [InlineKeyboardButton(text='Пройти тест по выбору', callback_data = 'take-test')]
    ]
)

async def categories():
    all_categories = await get_categories()
    keyboard = InlineKeyboardBuilder()

    for category in all_categories:
        keyboard.add(InlineKeyboardButton(text=category.name, callback_data=f"category_{category.id}"))
    keyboard.add(InlineKeyboardButton(text='⭕️ Главное меню', callback_data='to_main'))
    return keyboard.adjust(2).as_markup()


async def categories():
    all_categories = await get_categories()
    keyboard = InlineKeyboardBuilder()

    for category in all_categories:
        keyboard.add(InlineKeyboardButton(text=category.name, callback_data=f"category_{category.id}"))
    keyboard.add(InlineKeyboardButton(text='⭕️ Главное меню', callback_data='to_main'))
    return keyboard.adjust(2).as_markup()


async def categories_tests():
    all_categories = await get_categories()
    keyboard = InlineKeyboardBuilder()

    for category in all_categories:
        keyboard.add(InlineKeyboardButton(text=category.name, callback_data=f"category-tests_{category.id}"))
    keyboard.add(InlineKeyboardButton(text='⭕️ Главное меню', callback_data='to_main'))
    return keyboard.adjust(2).adjust(1, 1).as_markup()

async def choose_category():
    all_categories = await get_categories()
    buttons = []
    row = []

    for i, category in enumerate(all_categories):
        row.append(InlineKeyboardButton(text=category.name, callback_data=f"category_{category.id}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)

    buttons.append([InlineKeyboardButton(text='🆕 Создать новую тему', callback_data='create_new_category')])
    buttons.append([InlineKeyboardButton(text='⏪ Назад', callback_data='to_main')])

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard
    

async def test_created_keyboard(test_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🆕 Создать вопрос", callback_data=f"create-question_{test_id}")],
            [InlineKeyboardButton(text="⭕️ Главное меню", callback_data="to_main")]
        ]
    )



def create_category_keyboard(categories):
    """Создает клавиатуру для выбора категории."""
    buttons = [
        InlineKeyboardButton(text=category.name, callback_data=f"exam-category_{category.id}") 
        for category in categories
    ]
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[buttons[i:i + 2] for i in range(0, len(buttons), 2)]  # Два столбца
    )
    keyboard.inline_keyboard.append([InlineKeyboardButton(text="⏪ Назад", callback_data="to_main")])
    return keyboard

def create_test_keyboard(tests):
    """Создает клавиатуру для выбора теста из категории."""
    buttons = [
        InlineKeyboardButton(text=test.title, callback_data=f"start-test_{test.id}") 
        for test in tests
    ]
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[buttons[i:i + 2] for i in range(0, len(buttons), 2)]  # Два столбца
    )
    keyboard.inline_keyboard.append([InlineKeyboardButton(text="⭕️ Главное меню", callback_data="to_main")])
    return keyboard