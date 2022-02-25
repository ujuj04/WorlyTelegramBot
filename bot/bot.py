import config
import logging
import messaging
import translation

from aiogram import Bot, Dispatcher, executor, types

#log level
logging.basicConfig(level=logging.INFO)

#bot init
bot = Bot(token=config.TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=["tr"], commands_prefix="!/")
async def translate(message: types.Message):
    await message.answer("(en){} --> (ru){}".format(message.text.split(' ')[1::],
                                                    translation.start(message.text.split(' ')[1::])))


#run long-polling
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)













