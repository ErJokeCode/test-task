import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
import asyncio
from aiohttp import ClientSession

from config import settings

_log = logging.getLogger(__name__)

bot = Bot(token=settings.TOKEN)
dp = Dispatcher()


@dp.message(Command('start'))
async def start(message: types.Message):
    json = {
        "user_id": message.from_user.id,
        "first_name": message.from_user.first_name,
        "last_name": message.from_user.last_name,
        "username": message.from_user.username
    }

    async with ClientSession() as session:
        async with session.post(f"{settings.SERVER_URL}/chat/user", json=json) as response:
            if response.status == 200:
                _log.info("User added")
                await message.answer('Привет! Это чат с кем-то)) Напиши первое сообщение!')
            else:
                _log.error("User not added")
                await message.answer('Привет! Ошибка связи с сервером( Попробуй еще раз выполнить команду /start')


async def main():
    _log.info("Start bot")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
