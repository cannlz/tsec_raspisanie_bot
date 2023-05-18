import os, glob
from asyncore import loop
import requests
import datetime
from bs4 import BeautifulSoup
import asyncio
from webserver import keep_alive
from aiogram import types, executor, Dispatcher, Bot
from aiogram.utils.markdown import hlink
from misc.spamCH import rate_limit
import middlewares
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import sqlite3 as sq
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
import time
from testExelRead import *
from updateRaspisanie import *


my_secret = os.environ['my_secret']
bot = Bot(my_secret)

dp = Dispatcher(bot, storage=MemoryStorage())
middlewares.setup(dp)
#global baseMain, cur
baseMain = sq.connect('tsec_base.db')
cur = baseMain.cursor()

#ОБНОВЛЕНИЕ РАСПИСАНИЯ БОТА /// время на хосте -4 часа от нашего
async def check_update():
    while True:
        lt = time.localtime()
        if lt.tm_min < 5 and lt.tm_hour == 9:
            await deleteAll()
        else:
            await checkDriver('update')
        await asyncio.sleep(120)

#ОТПРАВКА УВЕДОМЛЕНИЙ О РАСПИСАНИИ
async def popupsend():
    while True:
        timenow = time.localtime()
        userinfo = baseMain.execute(f'SELECT popup_settings, user_id, selected_group, selected_class, type_rasp, checkpopup FROM users').fetchall()
        for typepopup in userinfo:
            if typepopup[0] == 'Утро' and typepopup[5] == 0:
                if timenow.tm_hour == 2:
                    convertGroup = ""
                    if typepopup[2] == "ИТЭС":
                        convertGroup = "rasp_ites"
                    elif typepopup[2] == "ТС":
                        convertGroup = "rasp_tc"
                    elif typepopup[2] == "СПСиПБ":
                        convertGroup = "rasp_spsipb"
                    elif typepopup[2] == "РЦПО":
                        convertGroup = "rasp_rpco"
                    elif typepopup[2] == "ППКРС":
                        convertGroup = "rasp_ppkrc"
                    tomorrow = datetime.date.today()
                    try:
                        antspam = ""
                        sqldata = baseMain.execute(f'SELECT date FROM "{convertGroup}"').fetchall()  #получаем наши идентификаторы
                        print(convertGroup)
                        for i in sqldata:  # сортируем
                            if tomorrow.strftime('%d.%m.20%y') in i[0]:  # делаем проверку есть ли наш идентификатор в тех кнопках
                                if typepopup[4] == "Текст":
                                    pathtoexel = baseMain.execute(f'SELECT exelpath FROM "{convertGroup}" WHERE date = "{i[0]}"').fetchone()[0]
                                    answerTextRasp = await checktextRasp(typepopup[3], pathtoexel)
                                    rasp = '\n\n'.join(answerTextRasp[0])
                                    date = answerTextRasp[1]
                                    antspam = "Найдено"
                                    await bot.send_message(typepopup[1], text=f"Расписание занятий на {date}({i[0]}):\n\n{rasp}")
                                    baseMain.execute(f'UPDATE users SET checkpopup = 1 WHERE user_id="{typepopup[1]}"')
                                    baseMain.commit()
                                    print("good popup: ", typepopup[2])
                                else:
                                    raspisanie = baseMain.execute(f'SELECT * FROM "{convertGroup}" WHERE date = "{i[0]}"').fetchall()  # получаем данные о нашем юзере по его идентификатору он хранится в callbackk_query.data
                                    print(tomorrow.strftime('%d.%m.20%y'))
                                    antspam = "Найдено"
                                    print(antspam)
                                    text = hlink(raspisanie[0][2], raspisanie[0][3])
                                    photo = open(raspisanie[0][4], 'rb')
                                    await bot.send_photo(typepopup[1],photo,text,parse_mode='HTML')
                                    baseMain.execute(f'UPDATE users SET checkpopup = 1 WHERE user_id="{typepopup[1]}"')
                                    baseMain.commit()
                                    print("good popup: ", typepopup[2])
                        if antspam == "":
                            print(f"Не найдено {typepopup[2]} \n" + tomorrow.strftime('%d.%m.20%y'))
                            await bot.send_message(typepopup[1],"Не найдено расписания на сегодня",disable_notification=True)
                            baseMain.execute(f'UPDATE users SET checkpopup = 1 WHERE user_id="{typepopup[1]}"')
                            baseMain.commit()
                            print("good popup: ", typepopup[2])
                    except Exception as e:
                        print("Spamm error", e)

            elif typepopup[0] == 'День' and typepopup[5] == 0:
                if timenow.tm_hour == 17:
                    convertGroup = ""
                    if typepopup[2] == "ИТЭС":
                        convertGroup = "rasp_ites"
                    elif typepopup[2] == "ТС":
                        convertGroup = "rasp_tc"
                    elif typepopup[2] == "СПСиПБ":
                        convertGroup = "rasp_spsipb"
                    elif typepopup[2] == "РЦПО":
                        convertGroup = "rasp_rpco"
                    elif typepopup[2] == "ППКРС":
                        convertGroup = "rasp_ppkrc"
                    today = datetime.date.today()
                    tomorrow = today + datetime.timedelta(days=1)
                    try:
                        antspam = ""
                        sqldata = baseMain.execute(f'SELECT date FROM "{convertGroup}"').fetchall()  #получаем наши идентификаторы
                        for i in sqldata:  # сортируем
                            if tomorrow.strftime('%d.%m.20%y') in i[0]:  # делаем проверку есть ли наш идентификатор в тех кнопках
                                if typepopup[4] == "Текст":
                                    pathtoexel = baseMain.execute(f'SELECT exelpath FROM "{convertGroup}" WHERE date = "{i[0]}"').fetchone()[0]
                                    answerTextRasp = await checktextRasp(typepopup[3], pathtoexel)
                                    rasp = '\n\n'.join(answerTextRasp[0])
                                    date = answerTextRasp[1]
                                    antspam = "Найдено"
                                    await bot.send_message(typepopup[1], text=f"Расписание занятий на {date}({i[0]}):\n\n{rasp}")
                                    baseMain.execute(f'UPDATE users SET checkpopup = 1 WHERE user_id="{typepopup[1]}"')
                                    baseMain.commit()
                                    print("good popup: ", typepopup[2])
                                else:
                                    raspisanie = baseMain.execute(f'SELECT * FROM "{convertGroup}" WHERE date = "{i[0]}"').fetchall()  # получаем данные о нашем юзере по его идентификатору он хранится в callbackk_query.data
                                    print(tomorrow.strftime('%d.%m.20%y'))
                                    antspam = "Найдено"
                                    print(antspam)
                                    text = hlink(raspisanie[0][2], raspisanie[0][3])
                                    photo = open(raspisanie[0][4], 'rb')
                                    await bot.send_photo(typepopup[1],photo,text,parse_mode='HTML')
                                    baseMain.execute(f'UPDATE users SET checkpopup = 1 WHERE user_id="{typepopup[1]}"')
                                    baseMain.commit()
                                    print("good popup: ", typepopup[2])
                        if antspam == "":
                            print(f"Не найдено {typepopup[2]} \n" + tomorrow.strftime('%d.%m.20%y'))
                            await bot.send_message(typepopup[1],"Не найдено расписания на сегодня",disable_notification=True)
                            baseMain.execute(f'UPDATE users SET checkpopup = 1 WHERE user_id="{typepopup[1]}"')
                            baseMain.commit()
                            print("good popup: ", typepopup[2])
                    except Exception as e:
                        print("Spamm error", e)

            elif typepopup[0] == 'Вечер' and typepopup[5] == 0:
                if timenow.tm_hour == 11:
                    convertGroup = ""
                    if typepopup[2] == "ИТЭС":
                        convertGroup = "rasp_ites"
                    elif typepopup[2] == "ТС":
                        convertGroup = "rasp_tc"
                    elif typepopup[2] == "СПСиПБ":
                        convertGroup = "rasp_spsipb"
                    elif typepopup[2] == "РЦПО":
                        convertGroup = "rasp_rpco"
                    elif typepopup[2] == "ППКРС":
                        convertGroup = "rasp_ppkrc"
                    today = datetime.date.today()
                    tomorrow = today + datetime.timedelta(days=1)
                    try:
                        antspam = ""
                        sqldata = baseMain.execute(f'SELECT date FROM "{convertGroup}"').fetchall()  #получаем наши идентификаторы
                        for i in sqldata:  # сортируем
                            if tomorrow.strftime('%d.%m.20%y') in i[0]:  # делаем проверку есть ли наш идентификатор в тех кнопках
                                if typepopup[4] == "Текст":
                                    pathtoexel = baseMain.execute(f'SELECT exelpath FROM "{convertGroup}" WHERE date = "{i[0]}"').fetchone()[0]
                                    answerTextRasp = await checktextRasp(typepopup[3], pathtoexel)
                                    rasp = '\n\n'.join(answerTextRasp[0])
                                    date = answerTextRasp[1]
                                    antspam = "Найдено"
                                    await bot.send_message(typepopup[1], text=f"Расписание занятий на {date}({i[0]}):\n\n{rasp}")
                                    baseMain.execute(f'UPDATE users SET checkpopup = 1 WHERE user_id="{typepopup[1]}"')
                                    baseMain.commit()
                                    print("good popup: ", typepopup[2])
                                else:
                                    raspisanie = baseMain.execute(f'SELECT * FROM "{convertGroup}" WHERE date = "{i[0]}"').fetchall()  # получаем данные о нашем юзере по его идентификатору он хранится в callbackk_query.data
                                    print(tomorrow.strftime('%d.%m.20%y'))
                                    antspam = "Найдено"
                                    print(antspam)
                                    text = hlink(raspisanie[0][2], raspisanie[0][3])
                                    photo = open(raspisanie[0][4], 'rb')
                                    await bot.send_photo(typepopup[1],photo,text,parse_mode='HTML')
                                    baseMain.execute(f'UPDATE users SET checkpopup = 1 WHERE user_id="{typepopup[1]}"')
                                    baseMain.commit()
                                    print("good popup: ", typepopup[2])
                        if antspam == "":
                            print(f"Не найдено {typepopup[2]} \n" + tomorrow.strftime('%d.%m.20%y'))
                            await bot.send_message(typepopup[1],"Не найдено расписания на сегодня",disable_notification=True)
                            baseMain.execute(f'UPDATE users SET checkpopup = 1 WHERE user_id="{typepopup[1]}"')
                            baseMain.commit()
                            print("good popup: ", typepopup[2])
                    except Exception as e:
                        print("Spamm error", e)

        await asyncio.sleep(150)
        


#ГЛАВНОЕ МЕНЮ
user_id = ""
@rate_limit(limit=3, key='start')
@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await message.delete()
    markup = InlineKeyboardMarkup()  # создаём клавиатуру
    markup.row_width = 1  # кол-во кнопок в строке
    keyboard_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard_admin = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_allGroups = types.KeyboardButton("Все отделения")
    btn_ites = types.KeyboardButton("Расписание ИТЭС")
    btn_ts = types.KeyboardButton("Расписаниe ТС")
    btn_nineClass = types.KeyboardButton("Расписание 9 класса")
    btn_spsipb = types.KeyboardButton("Расписание СПСиПБ")
    btn_rcpo = types.KeyboardButton("Расписание РЦПО")
    btn_ppkrc = types.KeyboardButton("Расписание ППКРС")
    btn_help = types.KeyboardButton("Написать вопрос")
    btn_admin = types.KeyboardButton("Расписание на завтра")
    btn_raspnow = types.KeyboardButton("Расписание на сегодня")
    btn_priemnaya_k = types.KeyboardButton("Приемная комиссия")
    btn_settings = types.KeyboardButton("⚙️Настройки")
    btn_admin2 = types.KeyboardButton("/messages")
    keyboard_admin.add(btn_ites, btn_ts, btn_nineClass, btn_spsipb, btn_rcpo,btn_ppkrc, btn_admin, btn_raspnow, btn_admin2, btn_settings)
    markup.add(InlineKeyboardButton(text="ИТЭС", callback_data="ИТЭС"))  #Создаём кнопки, i[1] - название, i[2] - каллбек дата
    markup.add(InlineKeyboardButton(text="ТС", callback_data="ТС"))  #Создаём кнопки, i[1] - название, i[2] - каллбек дата
    markup.add(InlineKeyboardButton(text="СПСиПБ", callback_data="СПСиПБ"))  #Создаём кнопки, i[1] - название, i[2] - каллбек дата
    markup.add(InlineKeyboardButton(text="РЦПО", callback_data="РЦПО"))  #Создаём кнопки, i[1] - название, i[2] - каллбек дата
    markup.add(InlineKeyboardButton(text="ППКРС", callback_data="ППКРС"))  #Создаём кнопки, i[1] - название, i[2] - каллбек дата

    try:
        result = baseMain.execute(f'SELECT selected_group FROM users WHERE user_id = "{message.from_user.id}"').fetchone()
        print(result)
        if result != None:
            if message.from_user.id == 407073449:
                await message.answer("Бот для расписания занятий", reply_markup=keyboard_admin)
            elif result[0] == 'ИТЭС':
                keyboard_markup.add(btn_ites, btn_raspnow, btn_admin).add(btn_allGroups, btn_settings, btn_help).add(btn_priemnaya_k)
                await message.answer("Бот для расписания занятий", reply_markup=keyboard_markup)
            elif result[0] == 'ТС':
                keyboard_markup.add(btn_ts, btn_raspnow, btn_admin).add(btn_allGroups, btn_settings, btn_help).add(btn_priemnaya_k)
                await message.answer("Бот для расписания занятий", reply_markup=keyboard_markup)
            elif result[0] == 'СПСиПБ':
                keyboard_markup.add(btn_spsipb, btn_raspnow, btn_admin).add(btn_allGroups, btn_settings, btn_help).add(btn_priemnaya_k)
                await message.answer("Бот для расписания занятий", reply_markup=keyboard_markup)
            elif result[0] == 'РЦПО':
                keyboard_markup.add(btn_rcpo, btn_raspnow, btn_admin).add(btn_allGroups, btn_settings, btn_help).add(btn_priemnaya_k)
                await message.answer("Бот для расписания занятий", reply_markup=keyboard_markup)
            elif result[0] == 'ППКРС':
                keyboard_markup.add(btn_ppkrc, btn_raspnow, btn_admin).add(btn_allGroups, btn_settings, btn_help).add(btn_priemnaya_k)
                await message.answer("Бот для расписания занятий", reply_markup=keyboard_markup)
            print("id есть в базе", result[0])
            print("user_id: ", message.from_user.id)
        else:
            await message.answer("Выбери своё отделение", reply_markup=markup)
    except:
        await message.answer("Выбери своё отделение", reply_markup=markup)

#ГЛАВНОЕ МЕНЮ Кнопка назад
user_id = ""
@rate_limit(limit=3, key='start')
@dp.message_handler(lambda message: message.text == "❌Назад")
async def process_start_command(message: types.Message):
    await message.delete()
    markup = InlineKeyboardMarkup()  # создаём клавиатуру
    markup.row_width = 1  # кол-во кнопок в строке
    keyboard_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard_admin = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_allGroups = types.KeyboardButton("Все отделения")
    btn_ites = types.KeyboardButton("Расписание ИТЭС")
    btn_ts = types.KeyboardButton("Расписаниe ТС")
    btn_nineClass = types.KeyboardButton("Расписание 9 класса")
    btn_spsipb = types.KeyboardButton("Расписание СПСиПБ")
    btn_rcpo = types.KeyboardButton("Расписание РЦПО")
    btn_ppkrc = types.KeyboardButton("Расписание ППКРС")
    btn_help = types.KeyboardButton("Написать вопрос")
    btn_admin = types.KeyboardButton("Расписание на завтра")
    btn_raspnow = types.KeyboardButton("Расписание на сегодня")
    btn_priemnaya_k = types.KeyboardButton("Приемная комиссия")
    btn_settings = types.KeyboardButton("⚙️Настройки")
    btn_admin2 = types.KeyboardButton("/messages")
    keyboard_admin.add(btn_ites, btn_ts, btn_nineClass, btn_spsipb, btn_rcpo,btn_ppkrc, btn_admin, btn_raspnow, btn_admin2, btn_settings)
    markup.add(InlineKeyboardButton(text="ИТЭС", callback_data="ИТЭС"))  #Создаём кнопки, i[1] - название, i[2] - каллбек дата
    markup.add(InlineKeyboardButton(text="ТС", callback_data="ТС"))  #Создаём кнопки, i[1] - название, i[2] - каллбек дата
    markup.add(InlineKeyboardButton(text="СПСиПБ", callback_data="СПСиПБ"))  #Создаём кнопки, i[1] - название, i[2] - каллбек дата
    markup.add(InlineKeyboardButton(text="РЦПО", callback_data="РЦПО"))  #Создаём кнопки, i[1] - название, i[2] - каллбек дата
    markup.add(InlineKeyboardButton(text="ППКРС", callback_data="ППКРС"))  #Создаём кнопки, i[1] - название, i[2] - каллбек дата

    try:
        result = baseMain.execute(f'SELECT selected_group FROM users WHERE user_id = "{message.from_user.id}"').fetchone()
        print(result)
        if result != None:
            if message.from_user.id == 407073449:
                await message.answer("Бот для расписания занятий", reply_markup=keyboard_admin)
            elif result[0] == 'ИТЭС':
                keyboard_markup.add(btn_ites, btn_raspnow, btn_admin).add(btn_allGroups, btn_settings, btn_help).add(btn_priemnaya_k)
                await message.answer("Бот для расписания занятий", reply_markup=keyboard_markup)
            elif result[0] == 'ТС':
                keyboard_markup.add(btn_ts, btn_raspnow, btn_admin).add(btn_allGroups, btn_settings, btn_help).add(btn_priemnaya_k)
                await message.answer("Бот для расписания занятий", reply_markup=keyboard_markup)
            elif result[0] == 'СПСиПБ':
                keyboard_markup.add(btn_spsipb, btn_raspnow, btn_admin).add(btn_allGroups, btn_settings, btn_help).add(btn_priemnaya_k)
                await message.answer("Бот для расписания занятий", reply_markup=keyboard_markup)
            elif result[0] == 'РЦПО':
                keyboard_markup.add(btn_rcpo, btn_raspnow, btn_admin).add(btn_allGroups, btn_settings, btn_help).add(btn_priemnaya_k)
                await message.answer("Бот для расписания занятий", reply_markup=keyboard_markup)
            elif result[0] == 'ППКРС':
                keyboard_markup.add(btn_ppkrc, btn_raspnow, btn_admin).add(btn_allGroups, btn_settings, btn_help).add(btn_priemnaya_k)
                await message.answer("Бот для расписания занятий", reply_markup=keyboard_markup)
            print("id есть в базе", result[0])
            print("user_id: ", message.from_user.id)
        else:
            await message.answer("Выбери своё отделение", reply_markup=markup)
    except:
        await message.answer("Выбери своё отделение", reply_markup=markup)

#ГЛАВНОЕ МЕНЮ CALLBACK
@dp.callback_query_handler(text_startswith="start", state="*")
async def start_callback(call: types.CallbackQuery):
    await call.message.delete()
    markup = InlineKeyboardMarkup()  # создаём клавиатуру
    markup.row_width = 1  # кол-во кнопок в строке
    keyboard_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard_admin = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_allGroups = types.KeyboardButton("Все отделения")
    btn_ites = types.KeyboardButton("Расписание ИТЭС")
    btn_ts = types.KeyboardButton("Расписаниe ТС")
    btn_nineClass = types.KeyboardButton("Расписание 9 класса")
    btn_spsipb = types.KeyboardButton("Расписание СПСиПБ")
    btn_rcpo = types.KeyboardButton("Расписание РЦПО")
    btn_ppkrc = types.KeyboardButton("Расписание ППКРС")
    btn_help = types.KeyboardButton("Написать вопрос")
    btn_admin = types.KeyboardButton("Расписание на завтра")
    btn_raspnow = types.KeyboardButton("Расписание на сегодня")
    btn_priemnaya_k = types.KeyboardButton("Приемная комиссия")
    btn_settings = types.KeyboardButton("⚙️Настройки")
    btn_admin2 = types.KeyboardButton("/messages")
    keyboard_admin.add(btn_ites, btn_ts, btn_nineClass, btn_spsipb, btn_rcpo,btn_ppkrc, btn_admin, btn_raspnow, btn_admin2, btn_settings)
    markup.add(InlineKeyboardButton(text="ИТЭС", callback_data="ИТЭС"))  #Создаём кнопки, i[1] - название, i[2] - каллбек дата
    markup.add(InlineKeyboardButton(text="ТС", callback_data="ТС"))  #Создаём кнопки, i[1] - название, i[2] - каллбек дата
    markup.add(InlineKeyboardButton(text="СПСиПБ", callback_data="СПСиПБ"))  #Создаём кнопки, i[1] - название, i[2] - каллбек дата
    markup.add(InlineKeyboardButton(text="РЦПО", callback_data="РЦПО"))  #Создаём кнопки, i[1] - название, i[2] - каллбек дата
    markup.add(InlineKeyboardButton(text="ППКРС", callback_data="ППКРС"))  #Создаём кнопки, i[1] - название, i[2] - каллбек дата

    try:
        result = baseMain.execute(f'SELECT selected_group FROM users WHERE user_id = "{call.from_user.id}"').fetchone()
        print(result)
        if result != None:
            if call.from_user.id == 407073449:
                await call.message.answer("Бот для расписания занятий", reply_markup=keyboard_admin)
            elif result[0] == 'ИТЭС':
                keyboard_markup.add(btn_ites, btn_raspnow, btn_admin).add(btn_allGroups, btn_settings, btn_help).add(btn_priemnaya_k)
                await call.message.answer("Бот для расписания занятий", reply_markup=keyboard_markup)
            elif result[0] == 'ТС':
                keyboard_markup.add(btn_ts, btn_raspnow, btn_admin).add(btn_allGroups, btn_settings, btn_help).add(btn_priemnaya_k)
                await call.message.answer("Бот для расписания занятий", reply_markup=keyboard_markup)
            elif result[0] == 'СПСиПБ':
                keyboard_markup.add(btn_spsipb, btn_raspnow, btn_admin).add(btn_allGroups, btn_settings, btn_help).add(btn_priemnaya_k)
                await call.message.answer("Бот для расписания занятий", reply_markup=keyboard_markup)
            elif result[0] == 'РЦПО':
                keyboard_markup.add(btn_rcpo, btn_raspnow, btn_admin).add(btn_allGroups, btn_settings, btn_help).add(btn_priemnaya_k)
                await call.message.answer("Бот для расписания занятий", reply_markup=keyboard_markup)
            elif result[0] == 'ППКРС':
                keyboard_markup.add(btn_ppkrc, btn_raspnow, btn_admin).add(btn_allGroups, btn_settings, btn_help).add(btn_priemnaya_k)
                await call.message.answer("Бот для расписания занятий", reply_markup=keyboard_markup)
            print("id есть в базе", result[0])
            print("user_id: ", call.from_user.id)
        else:
            await call.message.answer("Выбери своё отделение", reply_markup=markup)
    except:
        await call.message.answer("Выбери своё отделение", reply_markup=markup)

#ВСЕ ОТДЕЛЕНИЯ
@dp.message_handler(lambda message: message.text == "Все отделения")
async def process_start_command(message: types.Message):
    await message.delete()

    keyboard_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_ites = types.KeyboardButton("Расписание ИТЭС")
    btn_ts = types.KeyboardButton("Расписаниe ТС")
    btn_nineClass = types.KeyboardButton("Расписание 9 класса")
    btn_spsipb = types.KeyboardButton("Расписание СПСиПБ")
    btn_rcpo = types.KeyboardButton("Расписание РЦПО")
    btn_ppkrc = types.KeyboardButton("Расписание ППКРС")
    btn_back = types.KeyboardButton("❌Назад")
    keyboard_markup.add(btn_ites, btn_ts, btn_nineClass, btn_spsipb, btn_rcpo,btn_ppkrc, btn_back)
    await message.answer("Все отделения ТОЛЬЯТТИНСКОГО СОЦИАЛЬНО-ЭКОНОМИЧЕСКОГО КОЛЛЕДЖА", reply_markup=keyboard_markup)

#МЕНЮ НАСТРОЕК
@dp.message_handler(lambda message: message.text == "⚙️Настройки")
async def parser(message: types.Message):
    markup = InlineKeyboardMarkup()  # создаём клавиатуру
    markup.row_width = 1  # кол-во кнопок в строке
    markup.add(InlineKeyboardButton(text="Включить уведомления", callback_data="allow_push"))
    markup.add(InlineKeyboardButton(text="Изменить вид расписания", callback_data="type_rasp"))
    markup.add(InlineKeyboardButton(text="Выбрать группу", callback_data="type_group"))
    markup.add(InlineKeyboardButton(text="Выбрать отделение", callback_data="type_otedelenie"))
    markup.add(InlineKeyboardButton(text="❌Закрыть", callback_data="start"))

    userinfo = baseMain.execute(f'SELECT * FROM users WHERE user_id = "{message.from_user.id}"').fetchone()
    await message.answer(f"⚙️Меню настроек пользоваетеля {userinfo[1]} \n\nОтделение: {userinfo[3]}\nГруппа: {userinfo[4]}\nВключить уведомления о расписании: {userinfo[5]} \nВид расписания(текст/картинка): {userinfo[6]}", reply_markup=markup)


#ВКЛЮЧЕНИЕ УВВЕДОМЛЕНИЙ
@dp.callback_query_handler(text_startswith="allow_push", state="*")
async def start_callback(call: types.CallbackQuery):
    markup = InlineKeyboardMarkup()  # создаём клавиатуру
    markup.row_width = 1  # кол-во кнопок в строке
    markup.add(InlineKeyboardButton(text="Утро", callback_data="Утро"))
    markup.add(InlineKeyboardButton(text="День", callback_data="День"))
    markup.add(InlineKeyboardButton(text="Вечер", callback_data="Вечер"))
    markup.add(InlineKeyboardButton(text="Выключить уведомления", callback_data="Нет"))
    markup.add(InlineKeyboardButton(text="❌Закрыть", callback_data="start"))

    await call.message.delete()
    userinfo = baseMain.execute(f'SELECT *  FROM users WHERE user_id = "{call.from_user.id}"').fetchone()
    await call.message.answer(f"⚙️Меню настроек пользоваетеля {userinfo[1]} \n\nВыберете удобное время для получения уведомлений о расписании на завтрашний день:", reply_markup=markup)


#ИЗМЕНЕНИЕ ТИПА РАСПИСАНИЯ(КАРТИКА/ТЕКСТ)
@dp.callback_query_handler(text_startswith="type_rasp", state="*")
async def start_callback(call: types.CallbackQuery):
    markup = InlineKeyboardMarkup()  # создаём клавиатуру
    markup.row_width = 1  # кол-во кнопок в строке
    markup.add(InlineKeyboardButton(text="Включить уведомления", callback_data="allow_push"))
    markup.add(InlineKeyboardButton(text="Изменить вид расписания", callback_data="type_rasp"))
    markup.add(InlineKeyboardButton(text="Выбрать группу", callback_data="type_group"))
    markup.add(InlineKeyboardButton(text="Выбрать отделение", callback_data="type_otedelenie"))
    markup.add(InlineKeyboardButton(text="❌Закрыть", callback_data="start"))
    
    if baseMain.execute(f'SELECT type_rasp FROM users WHERE user_id = "{call.from_user.id}"').fetchone()[0] == "Текст":
        baseMain.execute(f'UPDATE users SET type_rasp="Картинка" WHERE user_id="{call.from_user.id}"')
        baseMain.commit()
        userinfo = baseMain.execute(f'SELECT *  FROM users WHERE user_id = "{call.from_user.id}"').fetchone()
        await call.message.delete()
        await call.message.answer(f"⚙️Меню настроек пользоваетеля {userinfo[1]} \n\nОтделение: {userinfo[3]}\nГруппа: {userinfo[4]}\nВключить уведомления о расписании: {userinfo[5]} \nВид расписания(текст/картинка): {userinfo[6]}", reply_markup=markup)
    else:
        baseMain.execute(f'UPDATE users SET type_rasp="Текст" WHERE user_id="{call.from_user.id}"')
        baseMain.commit()
        userinfo = baseMain.execute(f'SELECT *  FROM users WHERE user_id = "{call.from_user.id}"').fetchone()
        await call.message.delete()
        await call.message.answer(f"⚙️Меню настроек пользоваетеля {userinfo[1]} \n\nОтделение: {userinfo[3]}\nГруппа: {userinfo[4]}\nВключить уведомления о расписании: {userinfo[5]} \nВид расписания(текст/картинка): {userinfo[6]}", reply_markup=markup)


#ВЫБОР ОТДЕЛЕНИЯ
@dp.callback_query_handler(text_startswith="type_otedelenie", state="*")
async def start_callback(call: types.CallbackQuery):
    markup = InlineKeyboardMarkup()  # создаём клавиатуру
    markup.row_width = 2  # кол-во кнопок в строке
    markup.add(InlineKeyboardButton(text="ИТЭС", callback_data="ИТЭС"))  #Создаём кнопки, i[1] - название, i[2] - каллбек дата
    markup.add(InlineKeyboardButton(text="ТС", callback_data="ТС"))  #Создаём кнопки, i[1] - название, i[2] - каллбек дата
    markup.add(InlineKeyboardButton(text="СПСиПБ", callback_data="СПСиПБ"))  #Создаём кнопки, i[1] - название, i[2] - каллбек дата
    markup.add(InlineKeyboardButton(text="РЦПО", callback_data="РЦПО"))  #Создаём кнопки, i[1] - название, i[2] - каллбек дата
    markup.add(InlineKeyboardButton(text="ППКРС", callback_data="ППКРС"))  #Создаём кнопки, i[1] - название, i[2] - каллбек дата
    markup.add(InlineKeyboardButton(text="❌Закрыть", callback_data="start"))
    userinfo = baseMain.execute(f'SELECT * FROM users WHERE user_id = "{call.from_user.id}"').fetchone()
    await call.message.delete()
    await call.message.answer(f"⚙️Меню настроек пользоваетеля {userinfo[1]} \n\nОтделение: {userinfo[3]}\nГруппа: {userinfo[4]}\nВключить уведомления о расписании: {userinfo[5]} \nВид расписания(текст/картинка): {userinfo[6]}", reply_markup=markup)

#ВЫБОР ГРУППЫ
@dp.callback_query_handler(text_startswith="type_group", state="*")
async def start_callback(call: types.CallbackQuery):
    markup = InlineKeyboardMarkup()  # создаём клавиатуру
    markup.row_width = 3  # кол-во кнопок в строке

    listItes = ["ИСП-11/12","ИСП-21/22","ИСП-31/32","ИСП-41/42","ОДЛ-11","ОДЛ-21","ОДЛ-31/32","К-31","Кип-11","Мци-11","А-31","А-41"]
    listTc = ["ВК-11","МВ-11","МТЭ-11","ВК-21","МВ-21","МТЭ-21","ОВМ-11","МТЭ-31","ВК-31","ВК-41","МВ-41","ТЭ-41"]
    listSpSIPB = ["П-11","ПБ-11","ПБ-12","ПБ-13","ПД-11","ПД-12","ПД-13","П-21","ПБ-21","ПБ-22","ПД-21","ПД-22","ПД-23","П-31","ПБ-31","ПБ-32","ПБ-33","ПД-31","ПД-32","ПД-33","П-41","ПБ-41","ПБ-42","ПБ-43"]
    listRCPO = ["НПА-11","НПА-21","НПА-31"]
    listPPKRC = ["Жкх-11 ","Св-11 ","Св-12 ","Пк-11 ","ТХМИ-11 ","Жкх-21 ","Кип-21 ","Св-21 ","Св-22 ","Пк-21","Жкх-31","Жкх-32","Кип-31","Рм-31 ","Св-31 ","Св-32","Пк-31 "]

    userinfo = baseMain.execute(f'SELECT * FROM users WHERE user_id = "{call.from_user.id}"').fetchone()
    if userinfo[3] == "ИТЭС":
        for calldata in listItes:  # делаем проверку есть ли наш идентификатор в тех кнопках
            markup.add(InlineKeyboardButton(text=calldata, callback_data=calldata))  #Создаём кнопки, i[1] - название, i[2] - каллбек дата
    elif userinfo[3] == "ТС":
        for calldata in listTc:  # делаем проверку есть ли наш идентификатор в тех кнопках
            markup.add(InlineKeyboardButton(text=calldata, callback_data=calldata))  #Создаём кнопки, i[1] - название, i[2] - каллбек дата
    elif userinfo[3] == "СПСиПБ":
        for calldata in listSpSIPB:  # делаем проверку есть ли наш идентификатор в тех кнопках
            markup.add(InlineKeyboardButton(text=calldata, callback_data=calldata))  #Создаём кнопки, i[1] - название, i[2] - каллбек дата
    elif userinfo[3] == "РЦПО":
        for calldata in listRCPO:  # делаем проверку есть ли наш идентификатор в тех кнопках
            markup.add(InlineKeyboardButton(text=calldata, callback_data=calldata))  #Создаём кнопки, i[1] - название, i[2] - каллбек дата    
    elif userinfo[3] == "ППКРС":
        for calldata in listPPKRC:  # делаем проверку есть ли наш идентификатор в тех кнопках
            markup.add(InlineKeyboardButton(text=calldata, callback_data=calldata))  #Создаём кнопки, i[1] - название, i[2] - каллбек дата    
    else:
        await call.message.delete()
        await call.message.answer(f"❌У вас не выбрано отделение. Вам нужно указать отделение в настройках\n⚙️Меню настроек пользоваетеля {userinfo[1]} \n\nОтделение: {userinfo[3]}\nГруппа: {userinfo[4]}\nВключить уведомления о расписании: {userinfo[5]} \nВид расписания(текст/картинка): {userinfo[6]}", reply_markup=markup)

    markup.add(InlineKeyboardButton(text="❌Закрыть", callback_data="start"))
    
    await call.message.delete()
    await call.message.answer(f"⚙️Меню настроек пользоваетеля {userinfo[1]} \n\nОтделение: {userinfo[3]}\nГруппа: {userinfo[4]}\nВключить уведомления о расписании: {userinfo[5]} \nВид расписания(текст/картинка): {userinfo[6]}", reply_markup=markup)


#ВЫБОР СВОЕГО ОТДЕЛЕНИЯ И ПОКАЗ РАСПИСАНИЯ(КАРТИНКА) /// ЛОВИТ ВЫБРАННУЮ ГРУППУ И ОТДЕЛЕНИЕ /// ЛОВИТ ВЫБОР ВРЕМЕНИ УВЕДОМЛЕНИЙ
@dp.callback_query_handler(lambda call: True)
async def stoptopupcall(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    result_str = callback_query.data.split(".")[0]
    search_str = callback_query.data.partition('.')[2]
    print(result_str, search_str)

    markup = InlineKeyboardMarkup()  # создаём клавиатуру
    markup.row_width = 1  # кол-во кнопок в строке
    markup.add(InlineKeyboardButton(text="Включить уведомления", callback_data="allow_push"))
    markup.add(InlineKeyboardButton(text="Изменить вид расписания", callback_data="type_rasp"))
    markup.add(InlineKeyboardButton(text="Выбрать группу", callback_data="type_group"))
    markup.add(InlineKeyboardButton(text="Выбрать отделение", callback_data="type_otedelenie"))
    markup.add(InlineKeyboardButton(text="❌Закрыть", callback_data="start"))
    
    #Ловит отделение и запускает выбор группы, если новый пользователь
    if callback_query.data != "" and "." not in callback_query.data and "-" not in callback_query.data:
        #Выбор уведомлений
        if 'Утро' in callback_query.data or 'День' in callback_query.data or 'Вечер' in callback_query.data or 'Нет' in callback_query.data:
            baseMain.execute(f'UPDATE users SET popup_settings="{callback_query.data}" WHERE user_id="{callback_query.from_user.id}"')
            baseMain.commit()
            await callback_query.message.delete()
            userinfo = baseMain.execute(f'SELECT *  FROM users WHERE user_id = "{callback_query.from_user.id}"').fetchone()
            await callback_query.message.answer(f"⚙️Меню настроек пользоваетеля {userinfo[1]} \n\nОтделение: {userinfo[3]}\nГруппа: {userinfo[4]}\nВключить уведомления о расписании: {userinfo[5]} \nВид расписания(текст/картинка): {userinfo[6]}", reply_markup=markup)
        else:
            if baseMain.execute(f"SELECT user_id FROM users WHERE user_id = {callback_query.from_user.id}").fetchone() == None:
                await callback_query.message.delete()
                try:
                    baseMain.execute(f'INSERT INTO users (user_id, username, selected_group, selected_class, popup_settings, type_rasp) VALUES ("{callback_query.from_user.id}", "{str(callback_query.from_user.username)}", "{str(callback_query.data)}", "Нет", "Нет", "Картинка");')
                    baseMain.commit()
                except:
                    baseMain.execute(f'INSERT INTO users (user_id, username, selected_group, selected_class, popup_settings, type_rasp) VALUES ("{callback_query.from_user.id}", "None", "{str(callback_query.data)}", "Нет", "Нет", "Картинка");')
                    baseMain.commit()
                markup = InlineKeyboardMarkup()  # создаём клавиатуру
                markup.row_width = 3  # кол-во кнопок в строке

                listItes = ["ИСП-11/12","ИСП-21/22","ИСП-31/32","ИСП-41/42","ОДЛ-11","ОДЛ-21","ОДЛ-31/32","К-31","Кип-11","Мци-11","А-31","А-41"]
                listTc = ["ВК-11","МВ-11","МТЭ-11","ВК-21","МВ-21","МТЭ-21","ОВМ-11","МТЭ-31","ВК-31","ВК-41","МВ-41","ТЭ-41"]
                listSpSIPB = ["П-11","ПБ-11","ПБ-12","ПБ-13","ПД-11","ПД-12","ПД-13","П-21","ПБ-21","ПБ-22","ПД-21","ПД-22","ПД-23","П-31","ПБ-31","ПБ-32","ПБ-33","ПД-31","ПД-32","ПД-33","П-41","ПБ-41","ПБ-42","ПБ-43"]
                listRCPO = ["НПА-11","НПА-21","НПА-31"]
                listPPKRC = ["Жкх-11 ","Св-11 ","Св-12 ","Пк-11 ","ТХМИ-11 ","Жкх-21 ","Кип-21 ","Св-21 ","Св-22 ","Пк-21","Жкх-31","Жкх-32","Кип-31","Рм-31 ","Св-31 ","Св-32","Пк-31 "]
                
                userinfo = baseMain.execute(f'SELECT * FROM users WHERE user_id = "{callback_query.from_user.id}"').fetchone()
                if userinfo[3] == "ИТЭС":
                    for calldata in listItes:  # делаем проверку есть ли наш идентификатор в тех кнопках
                        markup.add(InlineKeyboardButton(text=calldata, callback_data=calldata))  #Создаём кнопки, i[1] - название, i[2] - каллбек дата
                elif userinfo[3] == "ТС":
                    for calldata in listTc:  # делаем проверку есть ли наш идентификатор в тех кнопках
                        markup.add(InlineKeyboardButton(text=calldata, callback_data=calldata))  #Создаём кнопки, i[1] - название, i[2] - каллбек дата
                elif userinfo[3] == "СПСиПБ":
                    for calldata in listSpSIPB:  # делаем проверку есть ли наш идентификатор в тех кнопках
                        markup.add(InlineKeyboardButton(text=calldata, callback_data=calldata))  #Создаём кнопки, i[1] - название, i[2] - каллбек дата
                elif userinfo[3] == "РЦПО":
                    for calldata in listRCPO:  # делаем проверку есть ли наш идентификатор в тех кнопках
                        markup.add(InlineKeyboardButton(text=calldata, callback_data=calldata))  #Создаём кнопки, i[1] - название, i[2] - каллбек дата    
                elif userinfo[3] == "ППКРС":
                    for calldata in listPPKRC:  # делаем проверку есть ли наш идентификатор в тех кнопках
                        markup.add(InlineKeyboardButton(text=calldata, callback_data=calldata))  #Создаём кнопки, i[1] - название, i[2] - каллбек дата
                await callback_query.message.answer(f"Укажите вашу группу: \n\n⚙️Начальные настройки пользователя: {userinfo[1]} \n\nОтделение: {userinfo[3]}\nГруппа: {userinfo[4]}", reply_markup=markup)

            else:
                baseMain.execute(f'UPDATE users SET selected_group="{callback_query.data}" WHERE user_id="{callback_query.from_user.id}"')
                baseMain.commit()
                await callback_query.message.delete()
                try:
                    markup = InlineKeyboardMarkup()  # создаём клавиатуру
                    markup.row_width = 3  # кол-во кнопок в строке

                    listItes = ["ИСП-11/12","ИСП-21/22","ИСП-31/32","ИСП-41/42","ОДЛ-11","ОДЛ-21","ОДЛ-31/32","К-31","Кип-11","Мци-11","А-31","А-41"]
                    listTc = ["ВК-11","МВ-11","МТЭ-11","ВК-21","МВ-21","МТЭ-21","ОВМ-11","МТЭ-31","ВК-31","ВК-41","МВ-41","ТЭ-41"]
                    listSpSIPB = ["П-11","ПБ-11","ПБ-12","ПБ-13","ПД-11","ПД-12","ПД-13","П-21","ПБ-21","ПБ-22","ПД-21","ПД-22","ПД-23","П-31","ПБ-31","ПБ-32","ПБ-33","ПД-31","ПД-32","ПД-33","П-41","ПБ-41","ПБ-42","ПБ-43"]
                    listRCPO = ["НПА-11","НПА-21","НПА-31"]
                    listPPKRC = ["Жкх-11 ","Св-11 ","Св-12 ","Пк-11 ","ТХМИ-11 ","Жкх-21 ","Кип-21 ","Св-21 ","Св-22 ","Пк-21","Жкх-31","Жкх-32","Кип-31","Рм-31 ","Св-31 ","Св-32","Пк-31 "]
                    
                    userinfo = baseMain.execute(f'SELECT * FROM users WHERE user_id = "{callback_query.from_user.id}"').fetchone()
                    if userinfo[3] == "ИТЭС":
                        for calldata in listItes:  # делаем проверку есть ли наш идентификатор в тех кнопках
                            markup.add(InlineKeyboardButton(text=calldata, callback_data=calldata))  #Создаём кнопки, i[1] - название, i[2] - каллбек дата
                    elif userinfo[3] == "ТС":
                        for calldata in listTc:  # делаем проверку есть ли наш идентификатор в тех кнопках
                            markup.add(InlineKeyboardButton(text=calldata, callback_data=calldata))  #Создаём кнопки, i[1] - название, i[2] - каллбек дата
                    elif userinfo[3] == "СПСиПБ":
                        for calldata in listSpSIPB:  # делаем проверку есть ли наш идентификатор в тех кнопках
                            markup.add(InlineKeyboardButton(text=calldata, callback_data=calldata))  #Создаём кнопки, i[1] - название, i[2] - каллбек дата
                    elif userinfo[3] == "РЦПО":
                        for calldata in listRCPO:  # делаем проверку есть ли наш идентификатор в тех кнопках
                            markup.add(InlineKeyboardButton(text=calldata, callback_data=calldata))  #Создаём кнопки, i[1] - название, i[2] - каллбек дата    
                    elif userinfo[3] == "ППКРС":
                        for calldata in listPPKRC:  # делаем проверку есть ли наш идентификатор в тех кнопках
                            markup.add(InlineKeyboardButton(text=calldata, callback_data=calldata))  #Создаём кнопки, i[1] - название, i[2] - каллбек дата
                    await callback_query.message.answer(f"Укажите вашу группу: \n\n⚙️Начальные настройки пользователя: {userinfo[1]} \n\nОтделение: {userinfo[3]}\nГруппа: {userinfo[4]}", reply_markup=markup)
                except:
                    pass

    #Ловит группу пользователя
    elif "-" in callback_query.data:
        baseMain.execute(f'UPDATE users SET selected_class="{callback_query.data}" WHERE user_id="{callback_query.from_user.id}"')
        baseMain.commit()

        await callback_query.message.delete()
        userinfo = baseMain.execute(f'SELECT *  FROM users WHERE user_id = "{callback_query.from_user.id}"').fetchone()
        await callback_query.message.answer(f'⚙️Меню настроек пользоваетеля {userinfo[1]} \n\nОтделение: {userinfo[3]}\nГруппа: {userinfo[4]}\nВключить уведомления о расписании: {userinfo[5]} \nВид расписания(текст/картинка): {userinfo[6]}\n\nНажмите "❌Закрыть" для выхода из меню настроек', reply_markup=markup)
    
    

    #ВЫВОДИМ РАСПИСАНИЕ ИТЭС
    if result_str == "1":
        sqldata = baseMain.execute("SELECT date FROM rasp_ites").fetchall()  #получаем наши идентификаторы
        sortdata = []  # список отсортированных
        for i in sqldata:  # сортируем
            sortdata.append(i[0])  # добавляем отсортированные tgid в спислк
        if search_str in sortdata:  # делаем проверку есть ли наш идентификатор в тех кнопках
            checkType = baseMain.execute(f'SELECT type_rasp, selected_class, selected_group FROM users WHERE user_id = "{callback_query.from_user.id}"').fetchone()
            if checkType[0] == "Текст" and checkType[2] == 'ИТЭС':
                pathtoexel = baseMain.execute(f'SELECT exelpath FROM rasp_ites WHERE date = "{search_str}"').fetchone()[0]
                answerTextRasp = await checktextRasp(checkType[1], pathtoexel)
                rasp = '\n\n'.join(answerTextRasp[0])
                date = answerTextRasp[1]
                await bot.send_message(callback_query.from_user.id, text=f"Расписание занятий на {date}({search_str}):\n\n{rasp}")
                await callback_query.message.delete()
            else:
                raspisanie = baseMain.execute("SELECT * FROM rasp_ites WHERE date = (?)", (search_str, )).fetchall()  # получаем данные о нашем юзере по его идентификатору он хранится в callbackk_query.data
                text = hlink(raspisanie[0][2], raspisanie[0][3])
                photo = open(raspisanie[0][4], 'rb')
                await bot.send_photo(callback_query.from_user.id,
                                    photo=photo,
                                    caption=text,
                                    parse_mode='HTML')
                await callback_query.message.delete()

    #ВЫВОДИМ РАСПИСАНИЕ ТС
    elif result_str == "2":
        sqldata = baseMain.execute("SELECT date FROM rasp_tc").fetchall()  #получаем наши идентификаторы
        sortdata = []  # список отсортированных
        for i in sqldata:  # сортируем
            sortdata.append(i[0])  # добавляем отсортированные tgid в спислк
        if search_str in sortdata:  # делаем проверку есть ли наш идентификатор в тех кнопках
            checkType = baseMain.execute(f'SELECT type_rasp, selected_class, selected_group FROM users WHERE user_id = "{callback_query.from_user.id}"').fetchone()
            if checkType[0] == "Текст" and checkType[2] == 'ТС':
                pathtoexel = baseMain.execute(f'SELECT exelpath FROM rasp_tc WHERE date = "{search_str}"').fetchone()[0]
                answerTextRasp = await checktextRasp(checkType[1], pathtoexel)
                rasp = '\n\n'.join(answerTextRasp[0])
                date = answerTextRasp[1]
                await bot.send_message(callback_query.from_user.id, text=f"Расписание занятий на {date}({search_str}):\n\n{rasp}")
                await callback_query.message.delete()
            else: 
                raspisanie = baseMain.execute("SELECT * FROM rasp_tc WHERE date = (?)", (search_str, )).fetchall()  # получаем данные о нашем юзере по его идентификатору он хранится в callbackk_query.data
                text = hlink(raspisanie[0][2], raspisanie[0][3])
                photo = open(raspisanie[0][4], 'rb')
                await bot.send_photo(callback_query.from_user.id,
                                    photo=photo,
                                    caption=text,
                                    parse_mode='HTML')
                await callback_query.message.delete()

    #ВЫВОДИМ РАСПИСАНИЕ СПСИПБ
    elif result_str == "4":
        sqldata = baseMain.execute("SELECT date FROM rasp_spsipb").fetchall(
        )  #получаем наши идентификаторы
        sortdata = []  # список отсортированных
        for i in sqldata:  # сортируем
            sortdata.append(i[0])  # добавляем отсортированные tgid в спислк
        if search_str in sortdata:  # делаем проверку есть ли наш идентификатор в тех кнопках
            checkType = baseMain.execute(f'SELECT type_rasp, selected_class, selected_group FROM users WHERE user_id = "{callback_query.from_user.id}"').fetchone()
            if checkType[0] == "Текст" and checkType[2] == 'СПСиПБ':
                pathtoexel = baseMain.execute(f'SELECT exelpath FROM rasp_spsipb WHERE date = "{search_str}"').fetchone()[0]
                answerTextRasp = await checktextRasp(checkType[1], pathtoexel)
                rasp = '\n\n'.join(answerTextRasp[0])
                date = answerTextRasp[1]
                await bot.send_message(callback_query.from_user.id, text=f"Расписание занятий на {date}({search_str}):\n\n{rasp}")
                await callback_query.message.delete()
            else: 
                raspisanie = baseMain.execute("SELECT * FROM rasp_spsipb WHERE date = (?)", (search_str, )).fetchall()  # получаем данные о нашем юзере по его идентификатору он хранится в callbackk_query.data
                text = hlink(raspisanie[0][2], raspisanie[0][3])
                photo = open(raspisanie[0][4], 'rb')
                await bot.send_photo(callback_query.from_user.id,
                                    photo=photo,
                                    caption=text,
                                    parse_mode='HTML')
                await callback_query.message.delete()

    #ВЫВОДИМ РАСПИСАНИЕ РЦПО
    elif result_str == "5":
        sqldata = baseMain.execute("SELECT date FROM rasp_rpco").fetchall(
        )  #получаем наши идентификаторы
        sortdata = []  # список отсортированных
        for i in sqldata:  # сортируем
            sortdata.append(i[0])  # добавляем отсортированные tgid в спислк
        if search_str in sortdata:  # делаем проверку есть ли наш идентификатор в тех кнопках
            checkType = baseMain.execute(f'SELECT type_rasp, selected_class, selected_group FROM users WHERE user_id = "{callback_query.from_user.id}"').fetchone()
            if checkType[0] == "Текст" and checkType[2] == 'РЦПО':
                pathtoexel = baseMain.execute(f'SELECT exelpath FROM rasp_rpco WHERE date = "{search_str}"').fetchone()[0]
                answerTextRasp = await checktextRasp(checkType[1], pathtoexel)
                rasp = '\n\n'.join(answerTextRasp[0])
                date = answerTextRasp[1]
                await bot.send_message(callback_query.from_user.id, text=f"Расписание занятий на {date}({search_str}):\n\n{rasp}")
                await callback_query.message.delete()
            else: 
                raspisanie = baseMain.execute("SELECT * FROM rasp_rpco WHERE date = (?)", (search_str, )).fetchall()  # получаем данные о нашем юзере по его идентификатору он хранится в callbackk_query.data
                text = hlink(raspisanie[0][2], raspisanie[0][3])
                photo = open(raspisanie[0][4], 'rb')
                await bot.send_photo(callback_query.from_user.id,
                                    photo=photo,
                                    caption=text,
                                    parse_mode='HTML')
                await callback_query.message.delete()

    #ВЫВОДИМ РАСПИСАНИЕ ППКРС
    elif result_str == "6":
        sqldata = baseMain.execute("SELECT date FROM rasp_ppkrc").fetchall(
        )  #получаем наши идентификаторы
        sortdata = []  # список отсортированных
        for i in sqldata:  # сортируем
            sortdata.append(i[0])  # добавляем отсортированные tgid в спислк
        if search_str in sortdata:  # делаем проверку есть ли наш идентификатор в тех кнопках
            checkType = baseMain.execute(f'SELECT type_rasp, selected_class, selected_group FROM users WHERE user_id = "{callback_query.from_user.id}"').fetchone()
            if checkType[0] == "Текст" and checkType[2] == 'ППКРС':
                pathtoexel = baseMain.execute(f'SELECT exelpath FROM rasp_ppkrc WHERE date = "{search_str}"').fetchone()[0]
                answerTextRasp = await checktextRasp(checkType[1], pathtoexel)
                rasp = '\n\n'.join(answerTextRasp[0])
                date = answerTextRasp[1]
                await bot.send_message(callback_query.from_user.id, text=f"Расписание занятий на {date}({search_str}):\n\n{rasp}")
                await callback_query.message.delete()
            else: 
                raspisanie = baseMain.execute("SELECT * FROM rasp_ppkrc WHERE date = (?)", (search_str, )).fetchall()  # получаем данные о нашем юзере по его идентификатору он хранится в callbackk_query.data
                text = hlink(raspisanie[0][2], raspisanie[0][3])
                photo = open(raspisanie[0][4], 'rb')
                await bot.send_photo(callback_query.from_user.id,
                                    photo=photo,
                                    caption=text,
                                    parse_mode='HTML')
                await callback_query.message.delete()


class AwaitMessages(StatesGroup):
    messagesend = State()
    messageHelp = State()

#НАПИСАНИЕ СООБЩЕНИЙ ДЛЯ АДМИНА
@dp.message_handler(commands=['messages'])
async def process_fio_add(message: types.Message):
    if message.from_user.id == 407073449:
        await message.answer('Сообщение всем: ')
        await AwaitMessages.messagesend.set()

#РАССЫЛКА СООБЩЕНИЙ ДЛЯ АДМИНА
@dp.message_handler(state=AwaitMessages.messagesend)  # Принимаем состояние
async def started(message: types.Message, state: FSMContext):
    async with state.proxy() as proxy:  # Устанавливаем состояние ожидания
        proxy['messagesend'] = message.text
    if proxy["messagesend"] != "/messages":
        chksend = 0
        dataUser = baseMain.execute("SELECT user_id FROM users").fetchall()
        for i in dataUser:
            try:
                await bot.send_message(i[0], proxy["messagesend"])
                chksend += 1
            except Exception:
                pass
                print("error_send")
                time.sleep(1)
                #i += 1
        await state.finish()  # Выключаем состояние
        await bot.send_message(
            407073449, "Отправлено  " + str(chksend) + " Пользователям")

    else:
        await state.finish()  # Выключаем состояние

#ПОЛУЧЕНИЕ СООБЩЕНИЯ ТП ДЛЯ АДМИНА
@dp.message_handler(state=AwaitMessages.messageHelp)  # Принимаем состояние
async def help(message: types.Message, state: FSMContext):
    async with state.proxy() as proxy:  # Устанавливаем состояние ожидания
        proxy['messageHelp'] = message.text
    if proxy["messageHelp"] != "Написать вопрос":
        await bot.send_message(407073449,
                               "👀 Вам задан вопрос 👉: " + proxy["messageHelp"])
        await state.finish()  # Выключаем состояние
        await bot.send_message(message.from_user.id, "Вопрос отправлен!")
    else:
        await state.finish()  # Выключаем состояние

#ВЫДАЁТ КНОПКИ С ДАТАМИ И ТЕКСТ(ПАРСИТ С САЙАТ ЗАЧЕМ-ТО) /// РАСПИСАНИЕ НА ЗАВТРА/СЕГОДНЯ
@rate_limit(limit=2, key='text')
@dp.message_handler(content_types=['text'])
async def parser(message: types.Message):
    if (message.text == "Расписание ИТЭС"):
        markup = InlineKeyboardMarkup()  # создаём клавиатуру
        markup.row_width = 1  # кол-во кнопок в строке
        sqldata = baseMain.execute("SELECT date FROM rasp_ites").fetchall(
        )  #получаем наши идентификаторы
        sortdata = []  # список отсортированных
        for i in sqldata:  # сортируем
            sortdata.append(i[0])  # добавляем отсортированные tgid в спислк
        for z in sortdata:  # делаем проверку есть ли наш идентификатор в тех кнопках
            s_indicator = "1." + z
            markup.add(InlineKeyboardButton(text=z, callback_data=s_indicator))  #Создаём кнопки, i[1] - название, i[2] - каллбек дата
        url = "https://tcek63.ru/studentam/raspisanie-zanyatiy/"
        r = requests.get(url=url)
        soup = BeautifulSoup(r.text, "lxml")
        articles_cards = soup.find_all('div', class_='acc')[0].find_all(
            'div', class_='acc_head')
        for article in articles_cards:
            try:
                article_desc = article.find("a").text.strip()
            except:
                article_desc = ""
        await message.answer(article_desc, reply_markup=markup)

    elif (message.text == "Расписаниe ТС"):
        markup = InlineKeyboardMarkup()  # создаём клавиатуру
        markup.row_width = 1  # кол-во кнопок в строке
        sqldata = baseMain.execute("SELECT date FROM rasp_tc").fetchall(
        )  #получаем наши идентификаторы
        sortdata = []  # список отсортированных
        for i in sqldata:  # сортируем
            sortdata.append(i[0])  # добавляем отсортированные tgid в спислк
        for z in sortdata:  # делаем проверку есть ли наш идентификатор в тех кнопках
            s_indicator = "2." + z
            markup.add(InlineKeyboardButton(text=z, callback_data=s_indicator))  #Создаём кнопки, i[1] - название, i[2] - каллбек дата
        url = "https://tcek63.ru/studentam/raspisanie-zanyatiy/"
        r = requests.get(url=url)
        soup = BeautifulSoup(r.text, "lxml")
        articles_cards = soup.find_all('div', class_='acc')[1].find_all(
            'div', class_='acc_head')
        for article in articles_cards:
            try:
                article_desc = article.find("a").text.strip()
            except:
                article_desc = ''
        await message.answer(article_desc, reply_markup=markup)

    elif (message.text == "Расписание 9 класса"):
        url = "https://tcek63.ru/studentam/raspisanie-zanyatiy/"
        r = requests.get(url=url)
        article_url1 = ""
        soup = BeautifulSoup(r.text, "lxml")
        articles_cards = soup.find_all('div', class_='acc')[2].find_all('div', class_='acc_body')
        linkcheck = soup.find('div', class_='acc_body').find_all('a',href=True)
        article_url1 = ""
        for article in articles_cards:
            for i in linkcheck:
                try:
                    article_url = article.find_all("img")[0].get("src")
                    article_url1 = "https://tcek63.ru/" + article_url
                except:
                    article_url1 = 'no_link'
            text = hlink(message.text, article_url1)
            await message.answer(text,
                                 parse_mode='HTML',
                                 disable_web_page_preview=0)

    elif (message.text == "Расписание СПСиПБ"):
        markup = InlineKeyboardMarkup()  # создаём клавиатуру
        markup.row_width = 1  # кол-во кнопок в строке
        sqldata = baseMain.execute("SELECT date FROM rasp_spsipb").fetchall(
        )  #получаем наши идентификаторы
        sortdata = []  # список отсортированных
        for i in sqldata:  # сортируем
            sortdata.append(i[0])  # добавляем отсортированные tgid в спислк
        for z in sortdata:  # делаем проверку есть ли наш идентификатор в тех кнопках
            s_indicator = "4." + z
            markup.add(InlineKeyboardButton(text=z, callback_data=s_indicator))  #Создаём кнопки, i[1] - название, i[2] - каллбек дата

        url = "https://tcek63.ru/studentam/raspisanie-zanyatiy/"
        r = requests.get(url=url)
        soup = BeautifulSoup(r.text, "lxml")
        articles_cards = soup.find_all('div', class_='acc')[3].find_all('div', class_='acc_head')
        for article in articles_cards:
            try:
                article_desc = article.find("a").text.strip()
            except:
                article_desc = ''
        await message.answer(article_desc, reply_markup=markup)

    elif (message.text == "Расписание РЦПО"):
        markup = InlineKeyboardMarkup()  # создаём клавиатуру
        markup.row_width = 1  # кол-во кнопок в строке
        sqldata = baseMain.execute("SELECT date FROM rasp_rpco").fetchall(
        )  #получаем наши идентификаторы
        sortdata = []  # список отсортированных
        for i in sqldata:  # сортируем
            sortdata.append(i[0])  # добавляем отсортированные tgid в спислк
        for z in sortdata:  # делаем проверку есть ли наш идентификатор в тех кнопках
            s_indicator = "5." + z
            markup.add(InlineKeyboardButton(text=z, callback_data=s_indicator)
                       )  #Создаём кнопки, i[1] - название, i[2] - каллбек дата

        url = "https://tcek63.ru/studentam/raspisanie-zanyatiy/"
        r = requests.get(url=url)
        soup = BeautifulSoup(r.text, "lxml")
        articles_cards = soup.find_all('div', class_='acc')[4].find_all(
            'div', class_='acc_head')
        for article in articles_cards:
            try:
                article_desc = article.find("a").text.strip()
            except:
                article_desc = ''
        await message.answer(article_desc, reply_markup=markup)

    elif (message.text == "Расписание ППКРС"):
        markup = InlineKeyboardMarkup()  # создаём клавиатуру
        markup.row_width = 1  # кол-во кнопок в строке
        sqldata = baseMain.execute("SELECT date FROM rasp_ppkrc").fetchall(
        )  #получаем наши идентификаторы
        sortdata = []  # список отсортированных
        for i in sqldata:  # сортируем
            sortdata.append(i[0])  # добавляем отсортированные tgid в спислк
        for z in sortdata:  # делаем проверку есть ли наш идентификатор в тех кнопках
            s_indicator = "6." + z
            markup.add(InlineKeyboardButton(text=z, callback_data=s_indicator)
                       )  #Создаём кнопки, i[1] - название, i[2] - каллбек дата

        url = "https://tcek63.ru/studentam/raspisanie-zanyatiy/"
        r = requests.get(url=url)
        soup = BeautifulSoup(r.text, "lxml")
        articles_cards = soup.find_all('div', class_='acc')[0].find_all(
            'div', class_='acc_head')
        for article in articles_cards:
            try:
                article_desc = article.find("a").text.strip()
            except:
                article_desc = ''
        await message.answer(article_desc, reply_markup=markup)
    
    elif (message.text == "Приемная комиссия"):
        text = hlink('БОТ "Приемная комиссия"', "https://t.me/Priyemnaya_komissiyaTSEKBOT")
        await message.answer("По всем вопросам, связанным с приемной комиссией: " + text, parse_mode='HTML') 

    elif (message.text == "Расписание на завтра"):
        today = datetime.date.today()
        tomorrow = today + datetime.timedelta(days=1)
        sqluser = baseMain.execute("SELECT selected_group FROM users WHERE user_id = (?)",(message.from_user.id, )).fetchone()
        print(sqluser[0])
        if sqluser[0] == "ИТЭС":
            try:
                antspam = ""
                sqldata = baseMain.execute("SELECT date FROM rasp_ites").fetchall()  #получаем наши идентификаторы
                for i in sqldata:  # сортируем
                    print(i)
                    if tomorrow.strftime('%d.%m.20%y') in i[0]:  # делаем проверку есть ли наш идентификатор в тех кнопках
                        checkType = baseMain.execute(f'SELECT type_rasp, selected_class FROM users WHERE user_id = "{message.from_user.id}"').fetchone()
                        if checkType[0] == "Текст":
                            pathtoexel = baseMain.execute(f'SELECT exelpath FROM rasp_ites WHERE date = "{i[0]}"').fetchone()[0]
                            answerTextRasp = await checktextRasp(checkType[1], pathtoexel)
                            rasp = '\n\n'.join(answerTextRasp[0])
                            date = answerTextRasp[1]
                            antspam = "Найдено"
                            await message.delete()
                            await bot.send_message(message.from_user.id, text=f"Расписание занятий на {date}({i[0]}):\n\n{rasp}")
                        else:
                            await message.delete()
                            raspisanie = baseMain.execute(f'SELECT * FROM rasp_ites WHERE date = "{i[0]}"').fetchall()  # получаем данные о нашем юзере по его идентификатору он хранится в callbackk_query.data
                            print(tomorrow.strftime('%d.%m.20%y'))
                            antspam = "Найдено"
                            print(antspam)
                            text = hlink(raspisanie[0][2], raspisanie[0][3])
                            photo = open(raspisanie[0][4], 'rb')
                            await bot.send_photo(message.from_user.id,
                                                photo,
                                                text,
                                                parse_mode='HTML')
                if antspam == "":
                    print("Не найдено ИТЭС \n" +
                          tomorrow.strftime('%d.%m.20%y'))
                    await bot.send_message(message.from_user.id,
                                           "Не найдено",
                                           disable_notification=True)
            except Exception as e:
                print("Spamm error", e)

        elif sqluser[0] == "ТС":
            try:
                antspam = ""
                sqldata = baseMain.execute("SELECT date FROM rasp_tc").fetchall()  #получаем наши идентификаторы
                for i in sqldata:  # сортируем
                    if tomorrow.strftime('%d.%m.20%y') in i[0]:  # делаем проверку есть ли наш идентификатор в тех кнопках
                        checkType = baseMain.execute(f'SELECT type_rasp, selected_class FROM users WHERE user_id = "{message.from_user.id}"').fetchone()
                        if checkType[0] == "Текст":
                            pathtoexel = baseMain.execute(f'SELECT exelpath FROM rasp_tc WHERE date = "{i[0]}"').fetchone()[0]
                            answerTextRasp = await checktextRasp(checkType[1], pathtoexel)
                            rasp = '\n\n'.join(answerTextRasp[0])
                            date = answerTextRasp[1]
                            antspam = "Найдено"
                            await message.delete()
                            await bot.send_message(message.from_user.id, text=f"Расписание занятий на {date}({i[0]}):\n\n{rasp}")
                        else:
                            await message.delete()
                            raspisanie = baseMain.execute(f'SELECT * FROM rasp_tc WHERE date = "{i[0]}"').fetchall()  # получаем данные о нашем юзере по его идентификатору он хранится в callbackk_query.data
                            print(tomorrow.strftime('%d.%m.20%y'))
                            antspam = "Найдено"
                            print(antspam)
                            text = hlink(raspisanie[0][2], raspisanie[0][3])
                            photo = open(raspisanie[0][4], 'rb')
                            await bot.send_photo(message.from_user.id,
                                                photo,
                                                text,
                                                parse_mode='HTML')
                if antspam == "":
                    print("Не найдено ТС \n" + tomorrow.strftime('%d.%m.20%y'))
                    await bot.send_message(message.from_user.id,
                                           "Не найдено",
                                           disable_notification=True)
            except:
                print("Spamm error")

        elif sqluser[0] == "СПСиПБ":
            try:
                antspam = ""
                sqldata = baseMain.execute("SELECT date FROM rasp_spsipb").fetchall()  #получаем наши идентификаторы
                for i in sqldata:  # сортируем
                    if tomorrow.strftime('%d.%m.20%y') in i[0]:  # делаем проверку есть ли наш идентификатор в тех кнопках
                        checkType = baseMain.execute(f'SELECT type_rasp, selected_class FROM users WHERE user_id = "{message.from_user.id}"').fetchone()
                        if checkType[0] == "Текст":
                            pathtoexel = baseMain.execute(f'SELECT exelpath FROM rasp_spsipb WHERE date = "{i[0]}"').fetchone()[0]
                            answerTextRasp = await checktextRasp(checkType[1], pathtoexel)
                            rasp = '\n\n'.join(answerTextRasp[0])
                            date = answerTextRasp[1]
                            antspam = "Найдено"
                            await message.delete()
                            await bot.send_message(message.from_user.id, text=f"Расписание занятий на {date}({i[0]}):\n\n{rasp}")
                        else:
                            await message.delete()
                            raspisanie = baseMain.execute(f'SELECT * FROM rasp_spsipb WHERE date = "{i[0]}"').fetchall()  # получаем данные о нашем юзере по его идентификатору он хранится в callbackk_query.data
                            print(tomorrow.strftime('%d.%m.20%y'))
                            antspam = "Найдено"
                            print(antspam)
                            text = hlink(raspisanie[0][2], raspisanie[0][3])
                            photo = open(raspisanie[0][4], 'rb')
                            await bot.send_photo(message.from_user.id,
                                                photo,
                                                text,
                                                parse_mode='HTML')
                if antspam != "Найдено":
                    print("Не найдено СПСиПБ \n" +
                          tomorrow.strftime('%d.%m.20%y'))
                    await bot.send_message(message.from_user.id,
                                           "Не найдено",
                                           disable_notification=True)
            except:
                print("Spamm error")

        elif sqluser[0] == "РЦПО":
            try:
                antspam = ""
                sqldata = baseMain.execute("SELECT date FROM rasp_rpco").fetchall()  #получаем наши идентификаторы
                sortdata = []  # список отсортированных
                for i in sqldata:  # сортируем
                    sortdata.append(i[0])  # добавляем отсортированные tgid в спислк
                    if tomorrow.strftime('%d.%m.20%y') in i[0]:  # делаем проверку есть ли наш идентификатор в тех кнопках
                        checkType = baseMain.execute(f'SELECT type_rasp, selected_class FROM users WHERE user_id = "{message.from_user.id}"').fetchone()
                        if checkType[0] == "Текст":
                            pathtoexel = baseMain.execute(f'SELECT exelpath FROM rasp_rpco WHERE date = "{i[0]}"').fetchone()[0]
                            answerTextRasp = await checktextRasp(checkType[1], pathtoexel)
                            rasp = '\n\n'.join(answerTextRasp[0])
                            date = answerTextRasp[1]
                            antspam = "Найдено"
                            await message.delete()
                            await bot.send_message(message.from_user.id, text=f"Расписание занятий на {date}({i[0]}):\n\n{rasp}")
                        else:
                            await message.delete()
                            raspisanie = baseMain.execute(f'SELECT * FROM rasp_rpco WHERE date = "{i[0]}"').fetchall()  # получаем данные о нашем юзере по его идентификатору он хранится в callbackk_query.data
                            print(tomorrow.strftime('%d.%m.20%y'))
                            antspam = "Найдено"
                            print(antspam)
                            text = hlink(raspisanie[0][2], raspisanie[0][3])
                            photo = open(raspisanie[0][4], 'rb')
                            await bot.send_photo(message.from_user.id,
                                                photo,
                                                text,
                                                parse_mode='HTML')
                if antspam != "Найдено":
                    print("Не найдено РЦПО \n" +
                          tomorrow.strftime('%d.%m.20%y'))
                    await bot.send_message(message.from_user.id,
                                           "Не найдено",
                                           disable_notification=True)
            except:
                print("Spamm error")

        elif sqluser[0] == "ППКРС":
            try:
                antspam = ""
                sqldata = baseMain.execute("SELECT date FROM rasp_ppkrc").fetchall()  #получаем наши идентификаторы
                sortdata = []  # список отсортированных
                for i in sqldata:  # сортируем
                    sortdata.append(i[0])  # добавляем отсортированные tgid в спислк
                    if tomorrow.strftime('%d.%m.20%y') in i[0]:  # делаем проверку есть ли наш идентификатор в тех кнопках
                        checkType = baseMain.execute(f'SELECT type_rasp, selected_class FROM users WHERE user_id = "{message.from_user.id}"').fetchone()
                        if checkType[0] == "Текст":                       
                            pathtoexel = baseMain.execute(f'SELECT exelpath FROM rasp_ppkrc WHERE date = "{i[0]}"').fetchone()[0]
                            answerTextRasp = await checktextRasp(checkType[1], pathtoexel)
                            rasp = '\n\n'.join(answerTextRasp[0])
                            date = answerTextRasp[1]
                            antspam = "Найдено"
                            await message.delete()
                            await bot.send_message(message.from_user.id, text=f"Расписание занятий на {date}({i[0]}):\n\n{rasp}")
                        else:
                            await message.delete()
                            raspisanie = baseMain.execute(f'SELECT * FROM rasp_ppkrc WHERE date = "{i[0]}"').fetchall()  # получаем данные о нашем юзере по его идентификатору он хранится в callbackk_query.data
                            print(tomorrow.strftime('%d.%m.20%y'))
                            antspam = "Найдено"
                            print(antspam)
                            text = hlink(raspisanie[0][2], raspisanie[0][3])
                            photo = open(raspisanie[0][4], 'rb')
                            await bot.send_photo(message.from_user.id,
                                                photo,
                                                text,
                                                parse_mode='HTML')
                if antspam != "Найдено":
                    print("Не найдено ТС \n" + tomorrow.strftime('%d.%m.20%y'))
                    await bot.send_message(message.from_user.id,
                                           "Не найдено",
                                           disable_notification=True)
            except Exception as e:
                print(e, "Spamm error")
        else:
            await bot.send_message(message.from_user.id,"Вы не выбрали отделание\nПропишите /start и выберете ваше отделение", disable_notification=True)
    if message.text == "Написать вопрос":
        await message.answer('Напишите ваш вопрос: ')
        await AwaitMessages.messageHelp.set()
    elif (message.text == "Расписание на сегодня"):
        tomorrow = datetime.date.today()
        sqluser = baseMain.execute(f'SELECT selected_group FROM users WHERE user_id = "{message.from_user.id}"').fetchone()
        print(sqluser[0])
        if sqluser[0] == "ИТЭС":
            try:
                antspam = ""
                sqldata = baseMain.execute("SELECT date FROM rasp_ites").fetchall()  #получаем наши идентификаторы
                for i in sqldata:  # сортируем
                    print("Это I: ", i[0])
                    if tomorrow.strftime('%d.%m.20%y') in i[0]:  # делаем проверку есть ли наш идентификатор в тех кнопках
                        checkType = baseMain.execute(f'SELECT type_rasp, selected_class FROM users WHERE user_id = "{message.from_user.id}"').fetchone()
                        if checkType[0] == "Текст":
                            pathtoexel = baseMain.execute(f'SELECT exelpath FROM rasp_ites WHERE date = "{i[0]}"').fetchone()[0]
                            answerTextRasp = await checktextRasp(checkType[1], pathtoexel)
                            rasp = '\n\n'.join(answerTextRasp[0])
                            date = answerTextRasp[1]
                            antspam = "Найдено"
                            await message.delete()
                            await bot.send_message(message.from_user.id, text=f"Расписание занятий на {date}({i[0]}):\n\n{rasp}")
                        else:
                            await message.delete()
                            raspisanie = baseMain.execute(f'SELECT * FROM rasp_ites WHERE date = "{i[0]}"').fetchall()  # получаем данные о нашем юзере по его идентификатору он хранится в callbackk_query.data
                            print(tomorrow.strftime('%d.%m.20%y'))
                            antspam = "Найдено"
                            print(antspam)
                            text = hlink(raspisanie[0][2], raspisanie[0][3])
                            photo = open(raspisanie[0][4], 'rb')
                            await bot.send_photo(message.from_user.id,
                                                photo,
                                                text,
                                                parse_mode='HTML')
                if antspam == "":
                    print("Не найдено ИТЭС \n" + tomorrow.strftime('%d.%m.20%y'))
                    await bot.send_message(message.from_user.id,
                                           "Не найдено",
                                           disable_notification=True)
            except Exception as e:
                print("Spamm error", e)

        elif sqluser[0] == "ТС":
            try:
                antspam = ""
                sqldata = baseMain.execute("SELECT date FROM rasp_tc").fetchall()  #получаем наши идентификаторы
                for i in sqldata:  # сортируем
                    if tomorrow.strftime('%d.%m.20%y') in i[0]:  # делаем проверку есть ли наш идентификатор в тех кнопках
                        checkType = baseMain.execute(f'SELECT type_rasp, selected_class FROM users WHERE user_id = "{message.from_user.id}"').fetchone()
                        if checkType[0] == "Текст":
                            pathtoexel = baseMain.execute(f'SELECT exelpath FROM rasp_tc WHERE date = "{i[0]}"').fetchone()[0]
                            answerTextRasp = await checktextRasp(checkType[1], pathtoexel)
                            rasp = '\n\n'.join(answerTextRasp[0])
                            date = answerTextRasp[1]
                            antspam = "Найдено"
                            await message.delete()
                            await bot.send_message(message.from_user.id, text=f"Расписание занятий на {date}({i[0]}):\n\n{rasp}")
                        else:
                            await message.delete()
                            raspisanie = baseMain.execute(f'SELECT * FROM rasp_tc WHERE date = "{i[0]}"').fetchall()  # получаем данные о нашем юзере по его идентификатору он хранится в callbackk_query.data
                            print(tomorrow.strftime('%d.%m.20%y'))
                            antspam = "Найдено"
                            print(antspam)
                            text = hlink(raspisanie[0][2], raspisanie[0][3])
                            photo = open(raspisanie[0][4], 'rb')
                            await bot.send_photo(message.from_user.id,
                                                photo,
                                                text,
                                                parse_mode='HTML')
                if antspam == "":
                    print("Не найдено ТС \n" + tomorrow.strftime('%d.%m.20%y'))
                    await bot.send_message(message.from_user.id,
                                           "Не найдено",
                                           disable_notification=True)
            except:
                print("Spamm error")

        elif sqluser[0] == "СПСиПБ":
            try:
                antspam = ""
                sqldata = baseMain.execute("SELECT date FROM rasp_spsipb").fetchall()  #получаем наши идентификаторы
                for i in sqldata:  # сортируем
                    if tomorrow.strftime('%d.%m.20%y') in i[0]:  # делаем проверку есть ли наш идентификатор в тех кнопках
                        checkType = baseMain.execute(f'SELECT type_rasp, selected_class FROM users WHERE user_id = "{message.from_user.id}"').fetchone()
                        if checkType[0] == "Текст":
                            pathtoexel = baseMain.execute(f'SELECT exelpath FROM rasp_spsipb WHERE date = "{i[0]}"').fetchone()[0]
                            answerTextRasp = await checktextRasp(checkType[1], pathtoexel)
                            rasp = '\n\n'.join(answerTextRasp[0])
                            date = answerTextRasp[1]
                            antspam = "Найдено"
                            await message.delete()
                            await bot.send_message(message.from_user.id, text=f"Расписание занятий на {date}({i[0]}):\n\n{rasp}")
                        else:
                            await message.delete()
                            raspisanie = baseMain.execute(f'SELECT * FROM rasp_spsipb WHERE date = "{i[0]}"').fetchall()  # получаем данные о нашем юзере по его идентификатору он хранится в callbackk_query.data
                            print(tomorrow.strftime('%d.%m.20%y'))
                            antspam = "Найдено"
                            print(antspam)
                            text = hlink(raspisanie[0][2], raspisanie[0][3])
                            photo = open(raspisanie[0][4], 'rb')
                            await bot.send_photo(message.from_user.id,
                                                photo,
                                                text,
                                                parse_mode='HTML')
                if antspam != "Найдено":
                    print("Не найдено СПСиПБ \n" +
                          tomorrow.strftime('%d.%m.20%y'))
                    await bot.send_message(message.from_user.id,
                                           "Не найдено",
                                           disable_notification=True)
            except:
                print("Spamm error")

        elif sqluser[0] == "РЦПО":
            try:
                antspam = ""
                sqldata = baseMain.execute("SELECT date FROM rasp_rpco").fetchall()  #получаем наши идентификаторы
                sortdata = []  # список отсортированных
                for i in sqldata:  # сортируем
                    sortdata.append(i[0])  # добавляем отсортированные tgid в спислк
                    if tomorrow.strftime('%d.%m.20%y') in i[0]:  # делаем проверку есть ли наш идентификатор в тех кнопках
                        checkType = baseMain.execute(f'SELECT type_rasp, selected_class FROM users WHERE user_id = "{message.from_user.id}"').fetchone()
                        if checkType[0] == "Текст":
                            pathtoexel = baseMain.execute(f'SELECT exelpath FROM rasp_rpco WHERE date = "{i[0]}"').fetchone()[0]
                            answerTextRasp = await checktextRasp(checkType[1], pathtoexel)
                            rasp = '\n\n'.join(answerTextRasp[0])
                            date = answerTextRasp[1]
                            antspam = "Найдено"
                            await message.delete()
                            await bot.send_message(message.from_user.id, text=f"Расписание занятий на {date}({i[0]}):\n\n{rasp}")
                        else:
                            await message.delete()
                            raspisanie = baseMain.execute(f'SELECT * FROM rasp_rpco WHERE date = "{i[0]}"').fetchall()  # получаем данные о нашем юзере по его идентификатору он хранится в callbackk_query.data
                            print(tomorrow.strftime('%d.%m.20%y'))
                            antspam = "Найдено"
                            print(antspam)
                            text = hlink(raspisanie[0][2], raspisanie[0][3])
                            photo = open(raspisanie[0][4], 'rb')
                            await bot.send_photo(message.from_user.id,
                                                photo,
                                                text,
                                                parse_mode='HTML')

                if antspam != "Найдено":
                    print("Не найдено РЦПО \n" +
                          tomorrow.strftime('%d.%m.20%y'))
                    await bot.send_message(message.from_user.id,
                                           "Не найдено",
                                           disable_notification=True)
            except:
                print("Spamm error")

        elif sqluser[0] == "ППКРС":
            try:
                antspam = ""
                sqldata = baseMain.execute("SELECT date FROM rasp_ppkrc").fetchall()  #получаем наши идентификаторы
                for i in sqldata:  # сортируем
                    if tomorrow.strftime('%d.%m.20%y') in i[0]:  # делаем проверку есть ли наш идентификатор в тех кнопках
                        checkType = baseMain.execute(f'SELECT type_rasp, selected_class FROM users WHERE user_id = "{message.from_user.id}"').fetchone()
                        if checkType[0] == "Текст":
                            pathtoexel = baseMain.execute(f'SELECT exelpath FROM rasp_ppkrc WHERE date = "{i[0]}"').fetchone()[0]
                            answerTextRasp = await checktextRasp(checkType[1], pathtoexel)
                            rasp = '\n\n'.join(answerTextRasp[0])
                            date = answerTextRasp[1]
                            antspam = "Найдено"
                            await message.delete()
                            await bot.send_message(message.from_user.id, text=f"Расписание занятий на {date}({i[0]}):\n\n{rasp}")
                        else:
                            await message.delete()
                            raspisanie = baseMain.execute(f'SELECT * FROM rasp_ppkrc WHERE date = "{i[0]}"').fetchall()  # получаем данные о нашем юзере по его идентификатору он хранится в callbackk_query.data
                            print(tomorrow.strftime('%d.%m.20%y'))
                            antspam = "Найдено"
                            print(antspam)
                            text = hlink(raspisanie[0][2], raspisanie[0][3])
                            photo = open(raspisanie[0][4], 'rb')
                            await bot.send_photo(message.from_user.id,
                                                photo,
                                                text,
                                                parse_mode='HTML')
                if antspam != "Найдено":
                    print("Не найдено ТС \n" + tomorrow.strftime('%d.%m.20%y'))
                    await bot.send_message(message.from_user.id,
                                           "Не найдено",
                                           disable_notification=True)
            except:
                print("Spamm error")
        else:
            await bot.send_message(message.from_user.id,"Вы не выбрали отделание\nПропишите /start и выберете ваше отделение",disable_notification=True)




keep_alive()
if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(check_update())
    loop.create_task(popupsend())
    executor.start_polling(dp)

executor.start_polling(dp)