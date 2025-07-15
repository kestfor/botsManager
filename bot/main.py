import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from bot.config import load_config
from bot.handlers import router

logging.basicConfig(level=logging.DEBUG)


async def main():
    cfg = load_config(config_path='../config.json')
    bot_token = cfg['bot_token']

    bot = Bot(token=bot_token)
    dp = Dispatcher()
    dp.include_router(router)

    logging.info("Starting bot...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
