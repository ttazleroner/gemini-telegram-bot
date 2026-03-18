from aiogram.types import KeyboardButton 
from lexicon.lexicon import LEXICON

# решил вынести создание кнопок в отдельный файл (папка -> файл)

help_user = KeyboardButton(text=LEXICON['help_button_for_user'])
reboot_bot = KeyboardButton(text=LEXICON['reboot_button'])
