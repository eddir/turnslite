"""
This is a echo bot.
It echoes any incoming text messages.
"""
from aiogram import Bot, Dispatcher, executor, types

from Turnslite import Turnslite
from settings import API_TOKEN

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` or `/help` command
    """
    turnslite.recipient = message.chat.id
    turnslite.send("Перезапуск")


@dp.message_handler()
async def echo(message: types.Message):
    # old style:
    # await bot.send_message(message.chat.id, message.text)
    global turnslite

    turnslite.cycle(message.chat.id, message.text)


async def send(chat_id, message):
    await bot.send_message(chat_id, message)


if __name__ == "__main__":
    turnslite = Turnslite(bot)
    executor.start_polling(dp, skip_updates=True)
