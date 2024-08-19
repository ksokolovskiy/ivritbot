from aiogram.dispatcher import Dispatcher
import config
from aiogram import types
from aiogram.utils import executor
from keyboards import keyboards
from base_data import sq_db
from aiogram import Bot
import random

from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage

import datetime

import asyncio


import time

bot = Bot(config.api_token_tg)
storage = MemoryStorage()
bot = Bot(token=config.api_token_tg)
dp = Dispatcher(bot, storage=storage)

class Waiting(StatesGroup):
    waiting_for_translate = State()

class Block_user(StatesGroup):
    waiting_for_id_user = State()

class White_user(StatesGroup):
    waiting_for_id_user = State()

class add_word(StatesGroup):
    word = State()
    word2 = State()
    word3 = State()

class del_word(StatesGroup):
    word = State()

class add_words(StatesGroup):
    add_words = State()

class waiting_edit_timer(StatesGroup):
    waiting_for_time_step = State()


async def my_job():
    while True:
        users = sq_db.get_users()
        list = sq_db.get_timer()
        interval = list[0][0]
        last_time = list[0][1]
        now = datetime.datetime.now()
        text = str(last_time)
        last_time = now - datetime.timedelta(minutes=int(interval))
        result = datetime.datetime.strptime(text, '%Y-%m-%d %H:%M:%S.%f')
        if last_time >= result:
            for i in users:
                state_with: FSMContext = dp.current_state(chat=i[0], user=i[0])
                current_state = await state_with.get_state()
                access = sq_db.check_acess(i[1])
                if access:
                    if current_state is None:
                        verbs = sq_db.get_verbs()
                        verb = random.choice(verbs)
                        print(verb)
                        verb_inf = random.randint(1, 2)
                        if verb_inf == 1:
                            verb_inf_string = ' (инфинитив)'
                        if verb_inf == 2:
                            verb_inf_string = ' (мужской ед. число)'
                        text = verb[0] + f'{verb_inf_string}'
                        await bot.send_message(i[0], text, reply_markup=keyboards.verb)
                        await state_with.set_state(Waiting.waiting_for_translate)
                        await state_with.update_data(verb_inf=verb_inf)
                        await state_with.update_data(verb=verb[0])
                        sq_db.update_timer(str(now))
                    else:
                        await bot.send_message(i[0], 'Ты не ответил на предыдущее слово. Чтобы получать новые слова, сначала реши с ним.')
                        sq_db.update_timer(str(now))
            else:
                pass
        await asyncio.sleep(10)


async def on_starup(x):
    print('Bot is working!')
    asyncio.create_task(my_job())


@dp.message_handler(commands='test', state='*')
async def test(message: types.Message):
    state_with: FSMContext = dp.current_state(chat=message.chat.id, user=message.from_user.id)
    current_state = await state_with.get_state()
    print(current_state)

@dp.message_handler(commands='start', state='*')
async def start(message: types.Message):
    try:
        sq_db.add_user(message.from_user.id, message.from_user.username)
    except Exception as e:
        print(e)
    access = sq_db.check_acess(message.from_user.username)
    if access:
        await message.answer(
            'Привет, я буду присылать тебе глаголы на русском, в ответ жду от тебя его перевод на Иврит, начнем?',
            reply_markup=keyboards.go)
    else:
        await message.answer('Ошибка, у тебя нет доступа к боту.')



@dp.message_handler(state=Waiting.waiting_for_translate)
async def all_message(message: types.Message, state: FSMContext):
    access = sq_db.check_acess(message.from_user.username)
    if access:
        if message.text == '/keyword':
            await message.answer('Сначала дай ответ на предыдущее слово')
        elif message.text == '/start':
            await message.answer(
                'Привет, я буду присылать тебе глаголы на русском, в ответ жду от тебя его перевод на Иврит. Сейчас у тебя есть слово, на которое ты не дал ответ. Пожалуйста, сначала ответь на него, а потом мы приступим к новым.')
        else:
            verbs = sq_db.get_verbs()
            data = await state.get_data()
            inf = int(data['verb_inf'])
            suc_verb = 'text'
            verb = data['verb']
            for i in verbs:
                if i[0] == verb:
                    suc_verb = i[inf]
            if message.text == suc_verb:
                await message.answer('Верно!')
                await state.finish()
            else:
                await message.answer('Не правильно :( Попробуй еще.')
    else:
        await message.answer('Ошибка, у тебя нет доступа к боту.')


@dp.callback_query_handler(text='go')
async def go_callback(callback: types.CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    print(current_state)
    if current_state is None:
        verbs = sq_db.get_verbs()
        verb = random.choice(verbs)
        print(verb)
        verb_inf = random.randint(1, 2)
        if verb_inf == 1:
            verb_inf_string = ' (инфинитив)'
        if verb_inf == 2:
            verb_inf_string = ' (мужской ед. число)'
        text = verb[0] + f'{verb_inf_string}'
        await callback.message.answer(text, reply_markup=keyboards.verb)
        await state.set_state(Waiting.waiting_for_translate)
        await state.update_data(verb_inf=verb_inf)
        await state.update_data(verb=verb[0])
        await callback.message.edit_reply_markup()
    else:
        await callback.message.answer('Ошибка, сначала дай ответ на предыдущее слово.')

@dp.message_handler(commands='keyword', state='*')
async def start(message: types.Message, state: FSMContext):
    access = sq_db.check_acess(message.from_user.username)
    if access:
        current_state = await state.get_state()
        print(current_state)
        if current_state is None:
            verbs = sq_db.get_verbs()
            verb = random.choice(verbs)
            print(verb)
            verb_inf = random.randint(1, 2)
            if verb_inf == 1:
                verb_inf_string = ' (инфинитив)'
            if verb_inf == 2:
                verb_inf_string = ' (мужской ед. число)'
            text = verb[0] + f'{verb_inf_string}'
            await message.answer(text, reply_markup=keyboards.verb)
            await state.set_state(Waiting.waiting_for_translate)
            await state.update_data(verb_inf=verb_inf)
            await state.update_data(verb=verb[0])
        else:
            await message.answer('Ошибка, сначала дай ответ на предыдущее слово.')
    else:
        await message.answer('Ошибка, у тебя нет доступа к боту.')

@dp.callback_query_handler(text='no_keywords', state='*')
async def go_callback(callback: types.CallbackQuery, state: FSMContext):
    text = callback.message.text.partition(' (')[0]
    sq_db.add_stop_keyword(callback.from_user.id, text)
    await callback.message.edit_reply_markup()
    await callback.message.answer('Хорошо, слово добавлено в исключение. Больше его показывать не буду.')
    await state.finish()

@dp.callback_query_handler(text='next_keywords', state='*')
async def go_callback(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_reply_markup()
    verbs = sq_db.get_verbs()
    data = await state.get_data()
    verb = data['verb']
    inf = int(data['verb_inf'])
    for i in verbs:
        if i[0] == verb:
            suc_verb = i[inf]
    await callback.message.answer(f'Правильный ответ - {suc_verb}. \nЧтобы получить новое слово, используй команду /keyword')
    await state.finish()


@dp.message_handler(commands='admin', state='*')
async def start(message: types.Message):
    if message.from_user.id in config.admins:
        await message.answer('Меню администратора', reply_markup=keyboards.admin)
    else:
        await message.answer('Ошибка, у тебя нет доступа к данному разделу.')


@dp.callback_query_handler(text='block_user', state='*')
async def go_callback(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer('Введи username пользователя.')
    await state.set_state(Block_user.waiting_for_id_user)


@dp.message_handler(state=Block_user.waiting_for_id_user)
async def block_user(message: types.Message, state: FSMContext):
    username_user = message.text
    users = sq_db.get_users()
    block_user_id = 0
    for i in users:
        if i[1] == username_user:
            block_user_id = i[0]
            print(block_user_id)
    if block_user_id == 0:
        await message.answer('Ошибка, пользователь не найден.')
        await state.finish()
    else:
        sq_db.block_user(block_user_id)
        await message.answer('Пользователь успешно заблокирован.')
        await state.finish()


@dp.callback_query_handler(text='white_user', state='*')
async def go_callback(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer('Введи username пользователя.')
    await state.set_state(White_user.waiting_for_id_user)

@dp.message_handler(state=White_user.waiting_for_id_user)
async def block_user(message: types.Message, state: FSMContext):
    username_user = message.text
    users = sq_db.get_users()
    white_user_id = 0
    for i in users:
        if i[1] == username_user:
            white_user_id = i[0]
            print(white_user_id)
    if white_user_id == 0:
        await message.answer('Ошибка, пользователь не найден.')
        await state.finish()
    else:
        sq_db.white_user(white_user_id)
        await message.answer('Пользователь успешно разблокирован.')
        await state.finish()

@dp.callback_query_handler(text='add_word', state='*')
async def go_callback(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer('Введи слово на русском.')
    await state.set_state(add_word.word)

@dp.message_handler(state=add_word.word)
async def add_word_1(message: types.Message, state: FSMContext):
    await message.answer('Теперь введи слово на иврите в инфинитиве.')
    await state.update_data(rus=message.text)
    await state.set_state(add_word.word2)

@dp.message_handler(state=add_word.word2)
async def add_word_2(message: types.Message, state: FSMContext):
    await message.answer('Теперь введи слово на иврите в мужском инфинитиве.')
    await state.update_data(inf=message.text)
    await state.set_state(add_word.word3)

@dp.message_handler(state=add_word.word3)
async def add_word_3(message: types.Message, state: FSMContext):
    await state.update_data(inf_man=message.text)
    data = await state.get_data()
    await state.finish()
    sq_db.add_verb(data['rus'], data['inf'], data['inf_man'])
    print(data)
    await message.answer('Слово добавлено.')


@dp.callback_query_handler(text='get_words', state='*')
async def go_callback(callback: types.CallbackQuery, state: FSMContext):
    sq_db.get_excel()
    f = open("files_xlsx/result.xlsx", "rb")
    await bot.send_document(callback.message.chat.id, f)
    f.close()

@dp.callback_query_handler(text='import_words', state='*')
async def go_callback(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer('Пришли мне файл .xlsx для импорта новых слов.')
    await state.set_state(add_words.add_words)

@dp.message_handler(content_types=['document'],state=add_words.add_words)
async def add_words_1(message: types.Message, state: FSMContext):
    if message.content_type == 'document':
        if message.document.file_name.partition('.')[2] == 'xlsx':
            await message.document.download(destination_file='files_xlsx/new_words.xlsx')
            sq_db.add_words()
            await message.answer('Ок, слова добавлены.')
            await state.finish()
        else:
            await message.answer('Ошибка, это не .xlsx, вернись в меню и попробуй заново.')
            await state.finish()
    else:
        await message.answer('Ошибка, это не .xlsx, вернись в меню и попробуй заново.')
        await state.finish()


@dp.callback_query_handler(text='del_word', state='*')
async def delete_word(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer('Введи слово на русском, которое хочешь удалить.')
    await state.set_state(del_word.word)

@dp.message_handler(state=del_word.word)
async def delete_word_2(message: types.Message, state: FSMContext):
    await state.finish()
    status = sq_db.del_word(message.text)
    print(status)
    await state.finish()
    if status:
        await message.answer('Слово удалено.')
    else:
        await message.answer('Ошибка, такого слова нет в словаре.')


@dp.callback_query_handler(text='edit_timer', state='*')
async def go_callback(callback: types.CallbackQuery, state: FSMContext):
    timer = sq_db.get_timer()
    await callback.message.answer(f'Введи количество минут для таймера отправки новых слов. Интервал сейчас: {timer[0][0]}')
    await state.set_state(waiting_edit_timer.waiting_for_time_step)


def is_int(str):
    try:
        int(str)
        return True
    except ValueError:
        return False


@dp.message_handler(state=waiting_edit_timer.waiting_for_time_step)
async def edit_timer(message: types.Message, state: FSMContext):
    step = message.text
    step_int = is_int(step)
    if step_int:
        sq_db.update_time_step(int(step))
        await message.answer('Таймер успешно изменен')
    else:
        'Ошибка. Ты ввел не число.'
    await state.finish()



if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_starup, skip_updates=True)









