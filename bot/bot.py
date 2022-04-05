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
            return "Пользователь уже зарегестрирован"

        user = {
            "user_id": chat_id,
            "nickname": "Noname",
            "points": 0
        }

        self.users.insert_one(user)

        return "Пользователь зарегестрирован"


db = Database()



class Form(StatesGroup):
    GameIsActive = State()  # Используются для подключения к проверке ответа
    GameIsGoing = State()  # Возвращает из обработки ответа обратно в принт слов

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


@dp.message_handler(commands=["g"])
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
    rounds -= 1
    await state.update_data(roundsNum=rounds)
    await Form.GameIsGoing.set()
    await message.answer('Напишите ready, если готовы начать игру.')



@dp.message_handler(state=Form.GameIsGoing)
async def PrintWords(message: types.Message, state: FSMContext):

    right, wrongs = WordyGuesser.generateReply()

    words = [right[0], wrongs[0], wrongs[1], wrongs[2]]
    await message.answer(translation.start(right[0]).replace(';', ','))
    random.shuffle(words)
    text = '1. {}\n2. {}\n3. {}\n4. {}'.format(words[0], words[1], words[2], words[3])

    await message.answer(text)
    await state.update_data(rightAns=right[0])
    data = await state.get_data()
    rounds = data.get('roundsNum')
    await Form.GameIsActive.set()






@dp.message_handler(state=Form.GameIsActive)
async def GameInProcess(message: types.Message, state: FSMContext):

    data = await state.get_data()
    finAns = data.get('rightAns')
    rounds = data.get('roundsNum')
    if message.text == finAns and rounds == 0:
        await message.answer('Первым ответил пользователь: ....., Он получает 1 очко!')
        user = db.users.find_one({"user_id": message.from_user.id})
        db.users.update_one({"user_id": message.from_user.id}, {"$set": {"points": user["points"] + 1}})
        await message.answer('Игра окончена!!!')
        await state.finish()
    if message.text == finAns and rounds != 0:
        await message.answer('Первым ответил пользователь: ....., Он получает 1 очко!\n\nНапишите ready, если готовы продолжить игру')
        user = db.users.find_one({"user_id": message.from_user.id})
        db.users.update_one({"user_id": message.from_user.id}, {"$set": {"points": user["points"] + 1}})
        rounds -= 1
        await state.update_data(roundsNum=rounds)
        await Form.GameIsGoing.set()
    elif message.text != finAns:
        await message.answer('ПОРАЖЕНИЕ')






@dp.message_handler(commands=["user_add"])
async def user_add(message: types.Message):
    chat_id = message["from"]["id"]
    await message.answer(Database.user_add(db, chat_id))

@dp.message_handler(commands=["set_nickname"])
async def user_add(message: types.Message):
    nick = message.text.split()[1]
    db.users.update_one({"user_id": message.from_user.id}, {"$set": {"nickname": nick}})
    await message.answer('Никнейм изменен')

@dp.message_handler(commands=["trEn"])
async def translate(message: types.Message):
    word = message.text.split()[1]
    await message.answer(translation.start(word))



@dp.message_handler(commands=["start"])
async def greetings(message: types.Message):
    await message.answer('Привет, меня зовут Worly! \nЯ пытаюсь сделать изучение иностранных языков легким и '
                         'интересным.'
                         ' \n\nВот, что я могу: \n/trEn - я переведу любое слово с английского на русский '
                         '\nПример ввода: /trEn walk \n\n/trRu - я переведу любое слово с русского на английский '
                         '\nПример ввода: /trRu ходить \n\n/g - начнется игра, в которую ты можешь играть один или с '
                         'друзьями '
                         '(чтобы играть с друзьями, добавь меня в любой чат!)')


#run long-polling
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)













