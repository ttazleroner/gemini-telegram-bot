import asyncio
import sys
import logging
from aiogram import Bot, Dispatcher
from config.config import Config, load_config
from aiogram.fsm.storage.redis import RedisStorage
from handlers.start import router as start_router
from handlers.start import router as help_router
from handlers.gemini_answer import router as gemini_router
from middleware.database import DataBaseMiddleware
from infrastructure.database.dp import create_pool
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties


# да да всё тот же фикс от калловой винды 
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

async def main():
    
    config: Config = load_config()
    
    bot = Bot(
        token=config.tg_bot.token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    if config.redis.password:
        redis_url = f"redis://:{config.redis.password}@{config.redis.host}:{config.redis.port}/{config.redis.db_number}"
    else:
        redis_url = f"redis://{config.redis.host}:{config.redis.port}/{config.redis.db_number}"
    
    storage = RedisStorage.from_url(redis_url)
    
    dp = Dispatcher(storage=storage)
    logging.basicConfig(
    level=logging.INFO,
    format='%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s'
)
    logging.info(
        "🐍Запускаем бота..."
    )
    dsn = f"postgresql://{config.db.user}:{config.db.password}@{config.db.host}:{config.db.port}/{config.db.database}"
    
    pool = await create_pool(dsn)
    if not pool:
        logging.error(" Не удалось подключиться к базе.")
        return
    
    dp.update.middleware(DataBaseMiddleware(pool=pool))
    
    dp.include_routers(
        start_router,
        gemini_router
    )
    
    await bot.delete_webhook(drop_pending_updates=True)
    
    
    await dp.start_polling(bot)
    
if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Бот остановлен администратором')