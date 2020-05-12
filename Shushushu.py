#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
import logging
from functools import wraps
from selenium import webdriver
import subprocess

from setup import PROXY, TOKEN

from Covid import *
from Files import *
from UrlRequests import *
from SpeechToText import *

from telegram import Bot, Update, bot
from telegram.ext import CallbackContext, CommandHandler, Filters, MessageHandler, Updater
import re
from pymongo import MongoClient

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.

LOG_ACTIONS = []
CITY = 'Nizhny Novgorod'

# bot = Bot(
#     token=TOKEN,
#     base_url=PROXY,  # delete it if connection via VPN
# )

client = MongoClient('localhost', 27017)
db = client["ThePyProject"]
collection = db["HistoryCollection"]
covid_collection_t = db["CovidCollectionToday"]
covid_collection_y = db["CovidCollectionYesterday"]
covid_collection_wa = db["CovidCollectionWeekAgo"]


def voice_message(update: Update, context: CallbackContext):
    file_info = context.bot.get_file(update.message.voice.file_id)
    file_info.download('VOICE.ogg')
    command = [
        'C:Project/bin/ffmpeg.exe',  # путь до ffmpeg.exe
        '-i', 'VOICE.ogg',
        '-ar', '48000',
        'VOICE.wav'
    ]
    proc = subprocess.Popen(command)
    proc.wait()
    transcript = SpeechToText("./VOICE.wav")
    update.message.reply_text(transcript.sample_recognize())
    path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'VOICE.wav')
    os.remove(path)


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
def clear_db(update: Update, context: CallbackContext):
    """clear the whole database including history and all covids"""
    client.drop_database('ThePyProject')
    update.message.reply_text('Ready!')


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


def get_date(date_in):
    try :
        y = re.findall(r"\d{4}$", date_in)
        m = re.findall(r"\d{2}", str(re.findall(r"\.\d{2}\.", date_in)))
        d = str(int(re.findall(r"^\d{2}", date_in)[0]) - 1)
        return y, m, d
    except:
        try:
            y = re.findall(r"\d{4}$", date_in)
            d = str(int(re.findall(r"\d{2}", str(re.findall(r"-\d{2}-", date_in)))[0]) - 1)
            m = re.findall(r"^\d{2}", date_in)
            return y, m, d
        except:
            return 0


@log_action
@decorator_error
def covid_chosen_date(update: Update, context: CallbackContext):
    update.message.reply_text('You\'ll be provided with some covid info by chosen date')
    a = update.message['text'].replace('/corona_stats', '').strip()
    d = get_date(a)
    if d == 0:
        update.message.reply_text("Sorry, format is incorrect, try call function again!")
    else:
        try:
            data = CovidStats.upload_chosen_date(CovidStats, *d[0], *d[1], d[2])
            text = CovidStats.top_five(CovidStats, data)
            update.message.reply_text('Here you can find some statistic about top-5 covid infected regions')
            update.message.reply_text(text)
        except:
            update.message.reply_text('Sorry, something got wrong with it...')


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


@log_action
@decorator_error
def weather(update: Update, context: CallbackContext):
    update.message.reply_text(UrlRequests.get_weather())


@log_action
@decorator_error
def fact(update: Update, context: CallbackContext):
    update.message.reply_text(UrlRequests.get_cat_fact())


def main():
    # Connect via  proxy
    REQUEST_KWARGS = {
        'proxy_url': PROXY,
        # Optional, if you need authentication:
        # 'urllib3_proxy_kwargs': {
        #     'username': 'name',
        #     'password': 'passwd',
        # }
    }
    updater = Updater(TOKEN, request_kwargs=REQUEST_KWARGS, use_context=True)

    # updater = Updater(bot=bot, use_context=True)

    # on different commands - answer in Telegram
    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CommandHandler('help', help))
    updater.dispatcher.add_handler(CommandHandler('history', history))
    updater.dispatcher.add_handler(CommandHandler('settings', admin_settings))
    updater.dispatcher.add_handler(CommandHandler('clean', admin_check_period))
    updater.dispatcher.add_handler(CommandHandler('clean_db', clear_db))
    updater.dispatcher.add_handler(CommandHandler('fact', fact))
    updater.dispatcher.add_handler(CommandHandler('news', rbc_news))
    updater.dispatcher.add_handler(CommandHandler('covid', covid))
    updater.dispatcher.add_handler(CommandHandler('smile', smile))
    updater.dispatcher.add_handler(CommandHandler('weather', weather))
    updater.dispatcher.add_handler(CommandHandler('film', film))
    updater.dispatcher.add_handler(CommandHandler('dynamics', corona_stats_dynamics))
    updater.dispatcher.add_handler(CommandHandler('corona_stats', covid_chosen_date))


    # on noncommand i.e message - echo the message on Telegram
    updater.dispatcher.add_handler(MessageHandler(Filters.text, echo))
    updater.dispatcher.add_handler(MessageHandler(Filters.voice, voice_message))

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
