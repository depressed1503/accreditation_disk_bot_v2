import asyncio

from aiogram import Bot, Dispatcher

from src.config import SETTINGS
from src.handlers import routers
from src.middlewares.access import AccessMiddleware


async def main():
    bot = Bot(token=SETTINGS["TELEGRAM_TOKEN"])
    dp = Dispatcher()

    dp.message.middleware(AccessMiddleware())
    dp.callback_query.middleware(AccessMiddleware())

    dp.include_routers(*routers)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())