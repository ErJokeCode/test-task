import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
import asyncio

from config import settings

_log = logging.getLogger(__name__)

bot = Bot(token=settings.TOKEN)
dp = Dispatcher()


@dp.message(Command('start'))
async def start(message: types.Message):
    await message.reply("Hello!")


async def main():
    _log.info("Start bot")
    await dp.start_polling()

if __name__ == '__main__':
    asyncio.run(main())
