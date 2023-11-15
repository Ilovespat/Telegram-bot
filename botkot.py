import telebot
import requests
import psycopg2
import datetime
import time
from random import randint
from bs4 import BeautifulSoup
from collections import OrderedDict
from telebot import types

API_TOKEN = ''
DB_CONFIG = {'dbname': '', 'user': '', 'password': '', 'host': ''}
REPLACE_VALUES = OrderedDict(
    [(".", ""), (",", ""), ("/", ""), ("-", ""), (" ", ""), ("января", "01"), ("февраля", "02"),
     ("марта", "03"), ("апреля", "04"), ("мая", "05"), ("июня", "06"), ("июля", "07"), ("августа", "08"),
     ("сентября", "09"), ("октября", "10"), ("ноября", "11"), ("декабря", "12"), ])
HELP = """
/start - приветствие и описание
/help - вывести список команд
/card - выбрать метафорическую карту
/day - предсказание на день
/year -  предсказание на год
/vopros - ответ на твой вопрос 
/monetka - кинь монетку
/strana - куда поехать без визы
/pirozhok - стишок-пирожок
/numer - число судьбы по дате рождения"""
START = (
    "Я котик-ботик. Могу сделать предсказание тебе на день, на год, ответить на твой вопрос, "
    "вычислить число судьбы или подбросить монетку."
    "Могу повеселить стишком-пирожком. А еще могу показать метафорическую карту - выбираешь в уме свой вопрос или "
    "проблему, получаешь карту."
    " Что увидишь в карте и будет ответом. На 14 февраля шлю валентинки.")
BOT = telebot.TeleBot(API_TOKEN)


# Функция для отображения кнопочного меню
def main_keyboard():
    global CLOSEKEYBOARD
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    key1 = types.KeyboardButton('Метафорическая карта')
    key2 = types.KeyboardButton('Предсказание на день')
    key3 = types.KeyboardButton('Предсказание на год')
    key4 = types.KeyboardButton('Кинуть монетку')
    key5 = types.KeyboardButton('Куда поехать без визы')
    key6 = types.KeyboardButton('Стишок-пирожок')
    key7 = types.KeyboardButton('Число судьбы по дате рождения')
    key8 = types.KeyboardButton('Помощь')
    key9 = types.KeyboardButton('Ответ на вопрос')
    CLOSEKEYBOARD = types.ReplyKeyboardRemove()
    markup.add(key1, key2, key3, key4, key5, key6, key7, key8, key9)
    return markup


# Хендлеры для получения команд в чатботе
def handler_text_menu():
    @BOT.message_handler(content_types=['text'])
    def text_handler(message):
        if message.text == 'Число судьбы по дате рождения':
            numerology(message)
        if message.text == 'Помощь':
            help(message)
        if message.text == 'Метафорическая карта':
            card(message)
        if message.text == 'Предсказание на день':
            day(message)
        if message.text == 'Предсказание на год':
            year(message)
        if message.text == 'Кинуть монетку':
            monetka(message)
        if message.text == 'Куда поехать без визы':
            strana(message)
        if message.text == 'Стишок-пирожок':
            pirozhok(message)
        if message.text == 'Ответ на вопрос':
            vopros(message)
        if message.text not in ['Ответ на вопрос', 'Стишок-пирожок', 'Куда поехать без визы', 'Кинуть монетку',
                                'Предсказание на год', 'Предсказание на день', 'Метафорическая карта', 'Помощь',
                                'Число судьбы по дате рождения']:
            BOT.send_message(message.chat.id, text=f'{message.text} бе-бе-бе')
            BOT.send_message(message.chat.id, text=f'Давай пока общаться через команды /help или /start :D')


@BOT.message_handler(commands=["start"])
def start(message):
    if message.text == '/start':
        global chat_id
        global nameuser
        global username
        chat_id = message.chat.id
        nameuser = message.from_user.first_name
        username = message.from_user.username
    BOT.send_message(message.chat.id, f'Привет, {nameuser}! {START}', reply_markup=main_keyboard())
    handler_text_menu()
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO public.users (name, chat_id, username) VALUES (%s, %s, %s)', (nameuser, chat_id,
                                                                                                  username,))
        cursor.close()
        conn.commit()
        conn.close()
    except Exception as e:
        print(e)
    finally:
        if str(datetime.datetime.now().date().strftime("%d.%m")) == '14.02':
            time.sleep(1)
            BOT.send_message(message.chat.id, 'Сегодня 14 февраля, тебе уже подарили валентинку? В любом случае, держи '
                                              'валентинку от меня <3')
            valentine()


@BOT.message_handler(commands=["help"])
def help(message):
    BOT.send_message(message.chat.id, HELP)


@BOT.message_handler(commands=["monetka"])
def monetka(message):
    text = monetka_choice()
    BOT.send_message(message.chat.id, text)


@BOT.message_handler(commands=["strana"])
def strana(message):
    text = country_choice()
    BOT.send_message(message.chat.id, text)


@BOT.message_handler(commands=["pirozhok"])
def pirozhok(message):
    text = stih_choice()
    BOT.send_message(message.chat.id, text)


@BOT.message_handler(commands=["day"])
def day(message):
    a = randint(0, 5)
    text = daypred_choice()
    BOT.send_message(message.chat.id, text)


@BOT.message_handler(commands=["year"])
def year(message):
    text = yearpred_choice()
    BOT.send_message(message.chat.id, text)


@BOT.message_handler(commands=["vopros"])
def vopros(message):
    text = vopros_choice()
    BOT.send_message(message.chat.id, text)


@BOT.message_handler(commands=["card"])
def card(message):
    text = card_choice()
    BOT.send_photo(message.chat.id, text)


@BOT.message_handler(commands=["numer"])
def numerology(message):
    mess = BOT.send_message(message.chat.id, text="Пришли дату своего рождения, обещаю никому не раскрывать твой "
                                                  "возраст ;)", reply_markup=CLOSEKEYBOARD)
    BOT.register_next_step_handler(mess, numerolog)


@BOT.message_handler(commands=["card"])
def card(message):
    text = card_choice()
    BOT.send_photo(message.chat.id, text)


# отправка валентинки
def valentine():
    res = valentine_choice()
    photo = res[0]
    desc = res[1]
    BOT.send_photo(chat_id, open(photo, 'rb'), caption=desc)


# Расчет "числа судьбы" по дате рождения от пользователя
def numerolog(message):
    list_num = []
    try:
        mess = message.text.lower()
        num = multiple_replace(mess)
        if len(num) != 8:
            numdate = datetime.datetime.strptime(num, '%d%m%y').date().strftime('%d%m%Y')
        else:
            numdate = num
        list_num.extend(str(numdate))
        res = sum(map(int, numdate))
        while res >= 10:
            list_num.clear()
            for i in str(res):
                list_num.append(int(i))
            res = sum(list_num)
        text = num_choice(res)
        BOT.send_message(message.chat.id, text, reply_markup=main_keyboard())
    except Exception as e:
        print(e)
        mess = BOT.send_message(message.chat.id, text='Ой, это не дата или что-то пошло не так. Даю еще один шанс :)',
                                reply_markup=CLOSEKEYBOARD)
        BOT.register_next_step_handler(mess, numerolog)


# Замена лишних знаков и названий месяцев в вводе пользователя для расчета "числа судьбы"
def multiple_replace(source_str):
    for i, j in REPLACE_VALUES.items():
        source_str = source_str.replace(i, j)
    return source_str


# функции для выбора ответов на запрос пользователя в базе данных
def valentine_choice():
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM public.valentines')
    count_val = cursor.fetchone()
    a = randint(1, count_val[0])
    cursor.execute('SELECT valentine, description FROM public.valentines WHERE id=%s', (a,))
    valentine = cursor.fetchone()
    cursor.close()
    conn.close()
    return valentine


def stih_choice():
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM public.stihi')
    count_stihi = cursor.fetchone()
    a = randint(1, count_stihi[0])
    cursor.execute('SELECT stih FROM public.stihi WHERE id=%s', (a,))
    stih = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return stih


def country_choice():
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM public.countries')
    count_countries = cursor.fetchone()
    a = randint(1, count_countries[0])
    cursor.execute('SELECT countries FROM public.countries WHERE id=%s', (a,))
    country = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return country


def daypred_choice():
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM public.dayprediction')
    count_prediction = cursor.fetchone()
    a = randint(1, count_prediction[0])
    cursor.execute('SELECT prediction FROM public.dayprediction WHERE id=%s', (a,))
    prediction = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return prediction


def yearpred_choice():
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM public.yearprediction')
    count_prediction = cursor.fetchone()
    a = randint(1, count_prediction[0])
    cursor.execute('SELECT prediction FROM public.yearprediction WHERE id=%s', (a,))
    prediction = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return prediction


def card_choice():
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM public.pictures')
    count_pict = cursor.fetchone()
    a = randint(1, count_pict[0])
    cursor.execute('SELECT pict FROM public.pictures WHERE id=%s', (a,))
    pict = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return pict


def num_choice(res):
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute('SELECT num FROM public.num WHERE id=%s', (res,))
    text = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return text


def monetka_choice():
    a = randint(1, 3)
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute('SELECT res FROM public.monetka WHERE id=%s', (a,))
    text = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return text


def vopros_choice():
    a = randint(1, 5)
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute('SELECT otvet FROM public.vopros WHERE id=%s', (a,))
    text = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return text


BOT.polling(none_stop=True)
