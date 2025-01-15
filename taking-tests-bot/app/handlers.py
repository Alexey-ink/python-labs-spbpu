from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command

import app.database.requests as rq
import app.keybords as kb

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
