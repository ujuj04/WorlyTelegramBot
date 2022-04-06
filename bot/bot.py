import config
import logging
import pymongo
from pymongo import MongoClient
import translation
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

    def user_add(self, user_id):
        user = self.users.find_one({"user_id": user_id})

        if user is not None:
            return "Пользователь уже зарегестрирован"

        user = {
            "user_id": user_id,
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


@dp.message_handler(commands=["game"])
async def create_game(message: types.Message, state: FSMContext):
    attr = message.text.split()

    if attr.__len__() < 2 or not attr[1].isdigit():
        attr.append('3')

    game = {
        "rounds": int(attr[1]),
    }

    _game = WordyGuesser(game)
    rounds = game["rounds"]
    rounds -= 1
    await state.update_data(roundsNum=rounds)
    await Form.GameIsGoing.set()
    await message.answer('Мы напишем тебе слово на русском и 4 варианта ответа на английском.'
                         '\nТвоя задача определить, какой из вариантов ответа является правильным переводом.'
                         '\nЧтобы ответить, напиши это слово на английском.')
    await message.answer('Напиши ready, чтобы начать игру.')


@dp.message_handler(state=Form.GameIsGoing)
async def PrintWords(message: types.Message, state: FSMContext):

    right, wrongs = WordyGuesser.generateReply()
    words = [right[0], wrongs[0], wrongs[1], wrongs[2]]

    await message.answer(translation.start(right[0], srcLang=1033, dstLang=1049).replace(';', ','))

    random.shuffle(words)
    text = '1. {}\n2. {}\n3. {}\n4. {}'.format(words[0], words[1], words[2], words[3])

    await message.answer(text)
    await state.update_data(rightAns=right[0])
    await Form.GameIsActive.set()


@dp.message_handler(state=Form.GameIsActive)
async def GameInProcess(message: types.Message, state: FSMContext):

    data = await state.get_data()
    finAns = data.get('rightAns')
    rounds = data.get('roundsNum')

    if message.text == finAns and rounds == 0:

        user = db.users.find_one({"user_id": message.from_user.id})
        db.users.update_one({"user_id": message.from_user.id}, {"$set": {"points": user["points"] + 1}})

        if user["nickname"] != 'Noname':
            nick = user["nickname"]
        else:
            nick = user["user_id"]

        await message.answer('Ответ правильный!\n{} Ты получаешь 1 очко!\n\nИгра окончена!'.format(nick))
        await state.finish()

    if message.text == finAns and rounds != 0:
        user = db.users.find_one({"user_id": message.from_user.id})
        db.users.update_one({"user_id": message.from_user.id}, {"$set": {"points": user["points"] + 1}})
        rounds -= 1

        if user["nickname"] != 'Noname':
            nick = user["nickname"]
        else:
            nick = user["user_id"]

        await message.answer('Ответ правильный!\n{} получает 1 очко!\n\n'
                             'Напиши ready, чтобы продолжить'.format(nick))
        await state.update_data(roundsNum=rounds)
        await Form.GameIsGoing.set()

    elif message.text != finAns:

        await message.answer('Неверный ответ, попробуй еще раз.')


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
    await message.reply(translation.start(word=word, srcLang=1033, dstLang=1049).replace(';', ','))


@dp.message_handler(commands=["trRu"])
async def translate(message: types.Message):
    word = message.text.split()[1]
    await message.reply(translation.start(word=word, srcLang=1049, dstLang=1033).replace(';', ','))


@dp.message_handler(commands=["profile"])
async def print_points(message: types.Message):
    user = db.users.find_one({"user_id": message.from_user.id})
    await message.reply('Твои пользователькие данные:'
                        '\n\n\U0001F58A   Никнейм: {}'
                        '\n\n\U0001F464   User id: {}'
                        '\n\n\U0001FA99   Количество очков: {} '.format(user['nickname'], user['user_id'], user['points']))


@dp.message_handler(commands=["leaderboards"])
async def print_leaders(message: types.Message):
    print(message)
    users = db.users.find({})
    leaders = [('.  .  .  .  .', 0),
               ('.  .  .  .  .', 0),
               ('.  .  .  .  .', 0)]
    for user in users:
        user_points = user['points']
        if user_points > leaders[0][1]:
            leaders[0] = [user['nickname'], user_points]
        leaders.sort(key=lambda user: user[1])
    await message.answer('Таблица лидеров:\n\n'
                        '\U0001F947 {} - {} очков \n\n'
                        '\U0001F948 {} - {} очков\n\n'
                        '\U0001F949 {} - {} очков'
                        '\n\n Играй и зарабатывай очки, чтобы попасть в лидеры.'.format(leaders[2][0], leaders[2][1],
                                           leaders[1][0], leaders[1][1],
                                           leaders[0][0], leaders[0][1]))


@dp.message_handler(commands=["start"])
async def greetings(message: types.Message):
    await message.answer('Привет, меня зовут Worly!'
                         '\nЯ пытаюсь сделать изучение иностранных языков легким и интересным.'
                         '\n\nДля начала давай зарегестрируем тебя:'
                         '\n\nНапиши /user_add - и мы добавим тебя в нашу систему.'
                         '\n\nНапиши /set_nickname и свое имя - тогда другие пользователи будут знать, кто ты.'
                         '\nПример: /set_nickname Tim.'
                         '\n\n\nВот, что я могу:'
                         '\n\n/trEn - я переведу любое слово с английского на русский\nПример: /trEn walk.'
                         '\n\n/trRu - я переведу любое слово с русского на английский\nПример: /trRu ходить.'                        
                         '\n\n/game и количество раундов - начнется игра в слова.\nПример: /game 5'
                         '\n\n/profile - выведет твои пользовательские данные'
                         '\n\n(P.S. Ты можешь добавь меня в любой чат и соревноваться с друзьями!)')

#run long-polling
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)













