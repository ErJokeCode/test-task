from datetime import datetime, timezone
import logging
import time
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
import asyncio
from aiohttp import ClientSession

from config import settings
from models.user import User
from models.message import Message

_log = logging.getLogger(__name__)

bot = Bot(token=settings.TOKEN)
dp = Dispatcher()


@dp.message(Command('start'))
async def start(message: types.Message):
    user = User(
        user_id=message.chat.id,
        first_name=message.chat.first_name,
        last_name=message.chat.last_name,
        username=message.chat.username
    )

    try:
        async with ClientSession() as session:
            async with session.post(f"{settings.SERVER_URL}/chat/bot/user", json=user.model_dump()) as response:
                if response.status == 200:
                    _log.info("User added")
                    await message.answer('Привет! Это чат с кем-то)) Напиши первое сообщение!')
                elif response.status == 400:
                    _log.error("User already added")
                    await message.answer('Привет! Ты уже есть в системе)')
                else:
                    _log.error("User not added")
                    await message.answer('Привет! Ошибка на сервере( Попробуй еще раз выполнить команду /start')
    except Exception as e:
        _log.error("User not added")
        await message.answer('Привет! Ошибка связи с сервером( Попробуй еще раз выполнить команду /start')


@dp.message()
async def all_messages(message: types.Message):
    if message.text is None:
        await message.answer('Почему-то сообщение пустое(')
        return

    m_msg = Message(
        user_id=message.chat.id,
        text=message.text
    )

    try:
        async with ClientSession() as session:
            async with session.post(f"{settings.SERVER_URL}/chat/bot/{message.chat.id}", json=m_msg.model_dump()) as response:
                if response.status == 200:
                    _log.info("Message added")
                    msg = await message.answer('Сообщение отправлено!')
                    time.sleep(3)
                    await msg.delete()
                else:
                    _log.error("Message not added")
                    await message.answer('Ошибка на сервере(')
    except Exception as e:
        _log.error("Message not added. Error: %s", e)
        await message.answer('Ошибка связи с сервером(')


async def main():
    _log.info("Start bot")
    await dp.start_polling(bot)
    _log.info("Stop bot")

if __name__ == '__main__':
    asyncio.run(main())
