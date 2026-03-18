from aiogram import Router, F, types
from aiogram.filters import CommandStart
import os
from aiogram.fsm.context import FSMContext
from psycopg import AsyncConnection
import google.generativeai as genai
from config.config import Config, load_config
from lexicon.lexicon import LEXICON

Config = load_config()

SERVICE_TEXTS = {
    LEXICON["help_button_for_user"],
    LEXICON["reboot_button"],
}

os.environ['HTTP_PROXY'] = Config.proxy.http 
os.environ['HTTPS_PROXY'] = Config.proxy.https

genai.configure(api_key=Config.api.api)
model = genai.GenerativeModel('gemini-2.5-flash')

router = Router()

@router.message(F.text & ~F.text.startswith("/") & ~F.text.in_(SERVICE_TEXTS))
async def ai_chat(message: types.Message, state: FSMContext):
    await message.bot.send_chat_action(chat_id=message.chat.id, action='typing')
    
    data = await state.get_data()
    history = data.get("history", [])
    
    history.append({'role': 'user', 'parts': [message.text]})
    
    try:
        response = await model.generate_content_async(history)
        answer = response.text or "Отправьте сообщение еще раз."
        
        history.append({'role': 'model', 'parts': [answer]})

        if len(history) > 20:
            history = history[-20:]
        
        await state.update_data(history=history)
        
        await message.answer(answer)
    
    except Exception as e:
        print(f'Гугл крашнулся: {e}')
        
        if history:
            history.pop()
            await state.update_data(history=history)
            await message.answer('🛠️Проблемы на стороне GOOGLE. Попробуй написать еще раз')
