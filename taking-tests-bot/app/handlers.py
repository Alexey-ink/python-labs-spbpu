from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command

import app.keybords as kb

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(f"Вас приветствует бот для прохождения тестов!\nВыберите пункт меню: ", reply_markup=kb.main)


@router.message(Command('help'))
async def cmd_help(message: Message):
    await message.answer('Вы нажали на кнопку помощи')


@router.callback_query(F.data =='new-test')
async def new_test(callback: CallbackQuery):
    await callback.answer('')
    await callback.message.answer('Создаем тест...')


@router.callback_query(F.data =='show-tests')
async def show_tests(callback: CallbackQuery):
    await callback.answer('')
    await callback.message.answer('Тут будет список категорий тестов...')


@router.callback_query(F.data =='take-test')
async def take_test(callback: CallbackQuery):
    await callback.answer('')
    await callback.message.answer('Тут мы должны будем выбрать категорию...')
