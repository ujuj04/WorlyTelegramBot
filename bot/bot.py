import config
import logging
import pymongo
from pymongo import MongoClient
import translation
import functional
from random import randint
import random
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext

#log level
logging.basicConfig(level=logging.INFO)

#bot init
bot = Bot(token=config.TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


class Database():
    def __init__(self):
        cluster = MongoClient(
            "mongodb+srv://Worly:Worly@cluster0.8qjio.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")

        self.db = cluster["WorlyBot"]
        self.users = self.db["Users"]
        self.words = self.db["WordsFinal"]

    def user_add(self, chat_id):
        user = self.users.find_one({"chat_id": chat_id})

        if user is not None:
            return "User is already added"

        user = {
            "user_id": chat_id,
            "nickname": "Noname",
            "points": 0
        }

        self.users.insert_one(user)

        return "User added"


db = Database()


class Form(StatesGroup):
    GameIsActive = State()  # Will be represented in storage as 'Form:name'
    age = State()  # Will be represented in storage as 'Form:age'
    gender = State()  # Will be represented in storage as 'Form:gender'


class WordyGuesser:
    def __init__(self, game):

        self.game = game
        self.rounds = game["rounds"]
        self.timer = game["timer"]

    @staticmethod
    def generateReply():

        r_index = [randint(0, 2465)]
        w_index = [randint(0, 2465), randint(0, 2465), randint(0, 2465)]

        return WordyGuesser.get_word(r_index), WordyGuesser.get_word(w_index)

    @staticmethod
    def get_word(indexs):

        words = []

        for index in indexs:
            words.append(db.words.find_one({"index": index})["word"])
        return words


@dp.message_handler(commands=["c_game"])
async def create_game(message: types.Message, state: FSMContext):
    attr = message.text.split()

    if attr.__len__() < 3 or not attr[2].isdigit():
        attr.append('10')

    game = {
        "rounds": int(attr[1]),
        "timer": int(attr[2])
    }
    _game = WordyGuesser(game)
    rounds = game["rounds"]
    timer = game["timer"]

    while rounds > 0:

        right, wrongs = WordyGuesser.generateReply()
        rounds -= 1
        reply = False

        words = [right[0], wrongs[0], wrongs[1], wrongs[2]]

        right_tr = translation.start(right[0])

        random.shuffle(words)
        text = '??????????: {} \n\t1. {}\n\t2. {}\n\t3. {}\n\t4. {}'.format(right_tr,
                                                                       words[0], words[1], words[2], words[3])

        await Form.GameIsActive.set()
        await message.answer(text)
        await state.update_data(rightAns=right[0])


@dp.message_handler(state=Form.GameIsActive)
async def GameInProcess(message: types.Message, state: FSMContext):

    data = await state.get_data()
    finAns = data.get('rightAns')

    if message.text.lower() == finAns:
        await message.answer('??????, ????????????')
        await state.finish()
    else:
        await message.answer('??????????????????')


@dp.message_handler(commands=["user_add"])
async def user_add(message: types.Message):
    chat_id = message["from"]["id"]
    await message.answer(Database.user_add(db, chat_id))


@dp.message_handler(commands=["tr"])
async def translate(message: types.Message):
    word = message.text.split()[1]
    await message.answer(translation.start(word))


#run long-polling
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)













