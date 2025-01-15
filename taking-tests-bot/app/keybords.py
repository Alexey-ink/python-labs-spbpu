from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup

keyBoard = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Создать новый тест')], 
                                      [KeyboardButton(text='Посмотреть существующие тесты')],
                                      [KeyboardButton(text='Пройти тест по выбору')]],
                            resize_keyboard=True,
                            input_field_placeholder='Выберите пункт меню...')

main = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Создать новый тест', callback_data = 'new-test')],
    [InlineKeyboardButton(text='Посмотреть существующие тесты', callback_data = 'show-tests')],
    [InlineKeyboardButton(text='Пройти тест по выбору', callback_data = 'take-test')]
    ]
)