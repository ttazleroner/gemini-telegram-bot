from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from psycopg import AsyncConnection
from aiogram.types import Message
from infrastructure.database.request_start import add_user_to_db, check_users
from config.config import load_config
from lexicon.lexicon import LEXICON

from aiogram.utils.keyboard import ReplyKeyboardBuilder
from make_buttons.button import reboot_bot, help_user

builder = ReplyKeyboardBuilder()

builder.add(reboot_bot, help_user)

builder.adjust(1,1)

size_button = builder.as_markup(resize_keyboard=True)



router = Router()


@router.message(CommandStart())
async def start_message(message: Message, conn: AsyncConnection, state: FSMContext ):
    user = message.from_user
    await state.clear()
    try:
        await add_user_to_db(
            conn=conn,
            user_id=user.id,
            username=user.username
        )
    except Exception as e:
        print(f'Не получилось записать юзера в базу {e}')
    await message.answer(text = LEXICON['/start'], reply_markup=size_button)


@router.message(F.text == LEXICON['help_button_for_user'])
async def help_message(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(text=LEXICON['/help'])
    