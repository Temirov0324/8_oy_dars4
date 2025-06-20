import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv
import os
from database import init_db
from handlers import register_handlers


async def main():
    init_db()


    load_dotenv()
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise ValueError("BOT_TOKEN .env faylida topilmadi!")


    bot = Bot(token=token)
    dp = Dispatcher(storage=MemoryStorage())


    register_handlers(dp)


    print("Bot ishga tushdi...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())