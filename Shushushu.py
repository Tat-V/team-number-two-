#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

import logging
import os
from functools import wraps
from selenium import webdriver

# from setup import PROXY, TOKEN, TOKEN_WEATHER
from setup import PROXY, TOKEN

from Covid import *
from Files import *
from UrlRequests import *

# from google.cloud import speech_v1
# from google.cloud.speech_v1 import enums


# import subprocess
from telegram import Bot, Update, InputMediaPhoto, PhotoSize, bot
from telegram.ext import CallbackContext, CommandHandler, Filters, MessageHandler, Updater
import pymongo
from pymongo import MongoClient

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.

LOG_ACTIONS = []
CITY = 'Nizhny Novgorod'
bot = Bot(
    token=TOKEN,
    base_url=PROXY,  # delete it if connection via VPN
)
client = MongoClient('localhost', 27017)
db = client["ThePyProject"]
collection = db["HistoryCollection"]
covid_collection_t = db["CovidCollectionToday"]
covid_collection_y = db["CovidCollectionYesterday"]
covid_collection_wa = db["CovidCollectionWeekAgo"]


os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "path_to_your_.json_credential_file"


# class SpeechToText:
#     def __init__(self, local_file_path):
#         self.local_file_path = local_file_path
#
#     def sample_recognize(self):
#         transcript = ''
#         client = speech_v1.SpeechClient()
#         language_code = "ru-RU"
#         sample_rate_hertz = 48000
#         encoding = enums.RecognitionConfig.AudioEncoding.LINEAR16
#         config = {
#             "language_code": language_code,
#             "sample_rate_hertz": sample_rate_hertz,
#             "encoding": encoding,
#         }
#         with os.io.open(self.local_file_path, "rb") as f:
#             content = f.read()
#         audio = {"content": content}
#         response = client.recognize(config, audio)
#         for result in response.results:
#             alternative = result.alternatives[0]
#             transcript = alternative.transcript
#         if transcript == '':
#             transcript = 'Не удалось перевести.'
#         return transcript
#
#
# def voice_message(update: Update, context: CallbackContext):
#     file_info = context.bot.get_file(update.message.voice.file_id)
#     file_info.download('VOICE.ogg')
#     command = [
#         r'Project\bin\ffmpeg.exe', # путь до ffmpeg.exe
#         '-i', 'VOICE.ogg',
#         '-ar', '48000',
#         'VOICE.wav'
#     ]
#     proc = subprocess.Popen(command)
#     proc.wait()
#     transcript = SpeechToText("./VOICE.wav")
#     update.message.reply_text(transcript.sample_recognize())
#     path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'VOICE.wav')
#     os.remove(path)


def log_action(function):
    def inner(*args, **kwargs):
        update = args[0]
        funcname = function.__name__
        if update and hasattr(update, 'message') and hasattr(update, 'effective_user'):
            Files.new_log(Files, update, funcname)
        return function(*args, **kwargs)
    return inner


def decorator_error(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as er:
            print("Error! " + str(er) + ', ' + "function: " + func.__name__)
    return wrapper


@log_action
@decorator_error
def start(update: Update, context: CallbackContext):
    """Send a message when the command /start is issued."""
    update.message.reply_text(f'Привет, {update.effective_user.first_name}!\nОтправь команду /help, чтобы получить '
                              f'список команд!')


@log_action
@decorator_error
def rbc_news(update: Update, context: CallbackContext):
    options = webdriver.FirefoxOptions()
    options.add_argument('headless')
    #options.add_argument(f'window-size={512},{512}')
    options.add_argument('hide-scrollbars')

    driver = webdriver.Firefox(firefox_options=options)
    driver.get("https://nn.rbc.ru/")
    driver.get_screenshot_as_file('source_pack/img_news.png')
    driver.quit()

    Bot.send_photo(bot, update.message.chat.id, open('source_pack/img_news.png', 'rb'))


@log_action
@decorator_error
def corona_stats_dynamics(update: Update, context: CallbackContext):
    cd = CovidStatsDaily()
    cd.image_create()
    cd.top_five()

    update.message.reply_text('Below you\'ll be provided with daily changes in covid-19 statistics')
    Bot.send_photo(bot, update.message.chat.id, open('source_pack/Covid_stats.png', 'rb'))
    update.message.reply_text('Top-5 injured countries by Confirmed')
    Bot.send_photo(bot, update.message.chat.id, open('source_pack/Top_5_pie.png', 'rb'))
    Bot.send_photo(bot, update.message.chat.id, open('source_pack/Top_5_bar.png', 'rb'))
    update.message.reply_text('Top-5 injured countries by Death')
    Bot.send_photo(bot, update.message.chat.id, open('source_pack/Top_5_bar_death.png', 'rb'))


@log_action
@decorator_error
def clear_db(update: Update, context: CallbackContext):
    """clear the whole database including history and all covids"""
    client.drop_database('ThePyProject')


@log_action
@decorator_error
def admin_settings(update: Update, context: CallbackContext):
    """Send a list of AdminOnly commands"""
    if update.effective_user.first_name =='Meseyoshi':
        update.message.reply_text('Список функций для администрирования:\n/clean\n/clear_db')


@log_action
@decorator_error
def film(update: Update, context: CallbackContext):
    data = UrlRequests.get_film(UrlRequests, update)
    update.message.reply_text('Название: ' + data[0] +'\n'+'Рейтинг на IMDb: ' + data[1] + '\n'+'Длительность: '
                              + data[2]+'\n'+'В главной роли:' + data[3])


@log_action
@decorator_error
def covid(update: Update, context: CallbackContext):
    '''Send user top-5 covid infected provinces'''
    data = CovidStats.upload(CovidStats)
    text = CovidStats.top_five(CovidStats, data)
    update.message.reply_text('Here you can find some statistic about top-5 covid infected regions')
    update.message.reply_text(text)
    update.message.reply_text('And about about top-5 covid least infected regions')
    text = CovidStats.top_five(CovidStats, data)
    update.message.reply_text(text)
    CovidStats.image_create(CovidStats, data)
    Bot.send_photo(bot, update.message.chat.id, open('source_pack/Covid_statistics.png', 'rb'))
    Bot.send_photo(bot, update.message.chat.id, open('source_pack/Covid_weekly_changes.png', 'rb'))


@log_action
@decorator_error
def smile(update: Update, context: CallbackContext):
    '''Send user a smile'''
    smiles = ["\U0001F601", "Грузовичок" + "\U0001F69A" + "Везет улыбочки!", "\U0001F601", "\U0001F606",
              "\U0001F60B", "\U0001F60F", "\U0001F609", "\U0001F606",
              "\U0001F633" + "Задача для сеньора" + "\U0001F633"]
    s = random.randint(0, len(smiles) - 1)
    update.message.reply_text(smiles[s])


@log_action
@decorator_error
def help(update: Update, context: CallbackContext):
    """Send a list of all available functions when the command /list is issued."""
    update.message.reply_text('Доступные команды:\n/history\n/fact\n/weather\n/smile\n/film\n/covid\n'
                              '/news\n/dynamics\n')


@log_action
@decorator_error
def echo(update: Update, context: CallbackContext):
    """Echo the user message."""
    update.message.reply_text(update.message.text)


@log_action
@decorator_error
def error(update: Update, context: CallbackContext):
    """Log Errors caused by Updates."""
    logger.warning(f'Update {update} caused error {context.error}')


@log_action
@decorator_error
def history(update: Update, context: CallbackContext):
    update.message.reply_text(Files.history(Files))


@log_action
@decorator_error
def admin_check_period(update: Update, context: CallbackContext):
    Files.delete_logs(Files)
    mes = 'Готово!'
    update.message.reply_text(mes)


# @log_action
# @decorator_error
# def weather(update: Update, context: CallbackContext):
#     update.message.reply_text(UrlRequests.get_weather(TOKEN_WEATHER, CITY))


@log_action
@decorator_error
def fact(update: Update, context: CallbackContext):
    r = requests.get('https://cat-fact.herokuapp.com/facts')
    cat_fact = ''
    if r.status_code == 200:
        cats_dict = dict(r.json())
        cats_dict = cats_dict.get('all')
        kol_fact = len(cats_dict)
        fact_upvotes = cats_dict[0]['upvotes']
        cat_fact = cats_dict[0]['text']
        for i in range(1, kol_fact):
            if cats_dict[i]['upvotes'] > fact_upvotes:
                fact_upvotes = cats_dict[i]['upvotes']
                cat_fact = cats_dict[i]['text']
    update.message.reply_text(cat_fact)


def main():
    updater = Updater(bot=bot, use_context=True)

    # on different commands - answer in Telegram
    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CommandHandler('help', help))
    updater.dispatcher.add_handler(CommandHandler('history', history))
    updater.dispatcher.add_handler(CommandHandler('settings', admin_settings))
    updater.dispatcher.add_handler(CommandHandler('clean', admin_check_period))
    updater.dispatcher.add_handler(CommandHandler('fact', fact))
    updater.dispatcher.add_handler(CommandHandler('news', rbc_news))
    updater.dispatcher.add_handler(CommandHandler('covid', covid))
    updater.dispatcher.add_handler(CommandHandler('smile', smile))
    # updater.dispatcher.add_handler(CommandHandler('weather', weather))
    updater.dispatcher.add_handler(CommandHandler('film', film))
    updater.dispatcher.add_handler(CommandHandler('dynamics', corona_stats_dynamics))


    # on noncommand i.e message - echo the message on Telegram
    updater.dispatcher.add_handler(MessageHandler(Filters.text, echo))
    # updater.dispatcher.add_handler(MessageHandler(Filters.voice, voice_message))

    # log all errors
    updater.dispatcher.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    logger.info('Start Bot')
    main()
