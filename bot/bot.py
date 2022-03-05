import config
import logging
import languages
import translation
import functional

from aiogram import Bot, Dispatcher, executor, types

#log level
logging.basicConfig(level=logging.INFO)

#bot init
bot = Bot(token=config.TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=["tr"])
async def translate(message: types.Message):


#run long-polling
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)













