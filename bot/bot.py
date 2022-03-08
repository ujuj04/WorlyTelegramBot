import config
import logging
import pymongo
from pymongo import MongoClient
import languages
import translation
import functional

from aiogram import Bot, Dispatcher, executor, types

#Cluster + DB
cluster = MongoClient("mongodb+srv://Worly:Worly@cluster0.8qjio.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
db = cluster["WorlyBot"]
collection = db["Test"]

post1 = {
    "name": "Timofey",
    "age": 23
}

collection.insert_one(post1)

#log level
logging.basicConfig(level=logging.INFO)

#bot init
bot = Bot(token=config.TOKEN)
dp = Dispatcher(bot)


# @dp.message_handler(commands=["tr"])
# async def translate(message: types.Message):


#run long-polling
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)













