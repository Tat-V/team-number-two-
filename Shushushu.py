#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

import logging
import random
from datetime import datetime, date, timedelta
import requests
from functools import wraps
from selenium import webdriver
import pandas as pd
import matplotlib.pyplot as plt
from setup import PROXY, TOKEN
from telegram import Bot, Update, InputMediaPhoto, PhotoSize, bot
from telegram.ext import CallbackContext, CommandHandler, Filters, MessageHandler, Updater

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.

LOG_ACTIONS = []


def log_action(function):
    def inner(*args, **kwargs):
        update = args[0]
        if update and hasattr(update, 'message') and hasattr(update, 'effective_user'):
            LOG_ACTIONS.append({
            'user': update.effective_user.first_name,
            'user id': update.message.chat.id,
            'function': function.__name__,
            'message': update.message.text,
            'time': datetime.now().strftime("%Y-%m-%d %H.%M"), })
            if str(LOG_ACTIONS[-1]['function']).find('admin') == -1:
                with open("History.txt", "a", encoding="UTF-8") as file_h:
                    for key, value in LOG_ACTIONS[-1].items():
                        file_h.write(key + ':' + (str(value)) + "\t")
                    file_h.write("\n")
            elif str(LOG_ACTIONS[-1]['function']).find('admin') != -1:
                with open("Admin_History.txt", "a", encoding="UTF-8") as handler:
                    for key, value in LOG_ACTIONS[-1].items():
                        handler.write(key + ':' + (str(value)) + "\t")
                    handler.write("\n")
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
    update.message.reply_text(f'Привет, {update.effective_user.first_name}!\nОтправь команду /list, чтобы получить '
                              f'список команд!')


@log_action
@decorator_error
def chat_help(update: Update, context: CallbackContext):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Введи команду /start для начала. ')


@log_action
@decorator_error
def rbc_news(update: Update, context: CallbackContext):
    options = webdriver.FirefoxOptions()
    options.add_argument('headless')
    #options.add_argument(f'window-size={512},{512}')
    options.add_argument('hide-scrollbars')

    driver = webdriver.Firefox(firefox_options=options)
    driver.get("https://nn.rbc.ru/")
    driver.get_screenshot_as_file('img_news.png')
    driver.quit()

    img = open('img_news.png', 'rb')
    Bot.send_photo(update.message.chat.id, img)
    # url = "https://api.telegram.org/bot<1106935180:AAE6Ho9x2n50edAqLb7d2-mmWx0O8WczHzY>/sendPhoto";
    # files = {'photo': img}
    # data = {'chat_id': update.message.chat.id}
    # r = requests.post(url, files=files, data=data)
    # print(r.json())


@log_action
@decorator_error
def admin_settings(update: Update, context: CallbackContext):
    """Send a list of AdminOnly commands"""
    if update.effective_user.first_name =='Meseyoshi':
        update.message.reply_text('Список функций для администрирования:\n/clean  ')


@log_action
@decorator_error
def film(update: Update, context: CallbackContext):
    text = open('Film Library.txt','r')
    film_list = text.read().split()
    film_name = film_list[random.randint(0, len(film_list)-1)]
    url = f"https://imdb-internet-movie-database-unofficial.p.rapidapi.com/film/{film_name}"
    headers = {
        'x-rapidapi-host': "imdb-internet-movie-database-unofficial.p.rapidapi.com",
        'x-rapidapi-key': "99bdeb0c42mshab03bca44e75a6fp188e06jsn6d8755719252"
    }
    r = requests.request("GET", url, headers=headers)
    r = dict(r.json())
    title = r['title']
    rating = r['rating']
    length = r['length']
    main_role = r['cast'][0]['actor']
    update.message.reply_text('Название: '+title+'\n'+'Рейтинг на IMDb: '+rating+'\n'+'Длительность: '+length+'\n'+'В '
                             'главной роли: '+main_role)



@log_action
@decorator_error
def covid(update: Update, context: CallbackContext):
    '''Send user top-5 covid infected provinces'''

    yesterday = date.today() - timedelta(days=1)
    y = str(yesterday)[: 4]
    m = str(yesterday)[5: 7]
    d = str(yesterday)[8:]

    url=f'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/{m}-{d}-{y}.csv'
    data = pd.read_csv(url)
    data = data.sort_values('Confirmed', ascending=False)
    #data['Province/State'] = data['Province/State'].fillna('')
    data['Province_State'] = data['Province_State'].fillna('')
    #top_5 = data[['Province/State', 'Country/Region', 'Last Update', 'Confirmed', 'Deaths', 'Recovered']].iloc[:5]
    top_5 = data[['Province_State', 'Country_Region', 'Last_Update', 'Confirmed', 'Deaths', 'Recovered']].iloc[:5]

    text = ''
    for col in top_5:
        text += col + '\t\t'
    text += '\n\n'
    for i in top_5.values:
        for j in i:
            text += str(j) + '\t\t'
        text += '\n\n'

    week_ago = date.today() - timedelta(days=7)
    y = str(week_ago)[: 4]
    m = str(week_ago)[5: 7]
    d = str(week_ago)[8:]

    url = f'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/{m}-{d}-{y}.csv'
    data_ago = pd.read_csv(url)
    data_ago = data_ago.sort_values('Confirmed', ascending=False)

    all_confirmed = data['Confirmed'].sum()
    all_confirmed_ago = data_ago['Confirmed'].sum()
    all_dead = data['Deaths'].sum()
    all_dead_ago = data_ago['Deaths'].sum()
    all_recov = data['Recovered'].sum()
    all_recov_ago = data_ago['Recovered'].sum()

    fig, ax = plt.subplots(figsize=(15, 15))
    ax.bar("Confirmed til yesterday", all_confirmed, color="#FFA07A")
    ax.bar("Confirmed til week ago", all_confirmed_ago, color="#7CFC00")
    ax.bar("Dead til yesterday", all_dead, color="#FFA07A")
    ax.bar("Dead til week ago", all_dead_ago, color="#7CFC00")
    ax.bar("Recovered til yesterday", all_recov, color="#FFA07A")
    ax.bar("Recovered til week ago", all_recov_ago, color="#7CFC00")
    plt.title("Covid_statistics")
    fig.savefig("Covid_statistics")

    fig, ax = plt.subplots(figsize=(15, 15))

    ax.bar("Confirmed", all_confirmed - all_confirmed_ago, color="#FFA07A")
    ax.bar("Dead", all_dead - all_dead_ago, color="#B0E0E6")
    ax.bar("Recovered", all_recov - all_recov_ago, color="#7CFC00")
    plt.title("Weekly changes in...")
    fig.savefig("Covid_weekly_changes")

    update.message.reply_text('There you can find some statistic about top-5 covid injected regions')
    update.message.reply_text(text)
    bot.send_photo(update.message.chat.id, open('Covid_statistics.png', 'rb'))
    bot.send_photo(update.message.chat.id, open('Covid_weekly_changes.png', 'rb'))


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
def chat_list(update: Update, context: CallbackContext):
    """Send a list of all available functions when the command /list is issued."""
    update.message.reply_text('Доступные команды:\n/start\n/help\n/history\n/fact\n/weather\n/smile\n/film\n/covid')


@log_action
@decorator_error
def echo(update: Update, context: CallbackContext):
    """Echo the user message."""
    update.message.reply_text(update.message.text)

@log_action
def error(update: Update, context: CallbackContext):
    """Log Errors caused by Updates."""
    logger.warning(f'Update {update} caused error {context.error}')


@log_action
@decorator_error
def history(update: Update, context: CallbackContext):
    """Send user last 5 records from history."""
    # file_hist = open("History.txt", "r", encoding="UTF-8")
    hist = ""
    with open("History.txt", "r", encoding="UTF-8") as file_h:
        hist_all = file_h.readlines()
        if len(hist_all) > 4:
            for i in range(-1, -6, -1):
                hist += hist_all[i]
        else:
            hist = "\t".join(hist_all)
        update.message.reply_text(hist)

@log_action
@decorator_error
def admin_check_period(update: Update, context: CallbackContext):
    k = 0
    with open("History.txt", "r", encoding="UTF-8") as file_h:
        hist_all = file_h.readlines()
    for hist_line in hist_all:
        hist_line = hist_line.split('\t')
        hist_time = hist_line[-2].replace('time:', '')
        hist_time = datetime.strptime(hist_time, "%Y-%m-%d %H.%M")
        now = datetime.now()
        period = now - hist_time
        print(period)
        if period.days < 7:
            break
        k += 1
        print(k)
    with open('History.txt', 'w') as file_h:
        file_h.writelines(hist_all[k:])
    mes = 'Готово!'
    update.message.reply_text(mes)


@log_action
@decorator_error
def weather(update: Update, context: CallbackContext):
    TOKEN = 'd081cc3b0aa6fbb8e8f24d1a8216be49'
    CITY = 'Nizhny Novgorod'
    url = f'http://api.weatherstack.com/current?access_key={TOKEN}&query={CITY}'

    r = requests.get(url)
    r = r.json()
    city = r.get('request')['query']
    time = r.get('current')['observation_time']
    temperature = r.get('current')['temperature']
    weather_descriptions = r.get('current')['weather_descriptions'][0]
    wind_speed = r.get('current')['wind_speed']
    wind_speed = round(wind_speed * 1000.0 / 3600.0)
    weather_now = 'Город: ' + city + '\n' + 'Время снятия данных: ' + str(time) + '\n' + 'Температура: ' +\
                  str(temperature) + '℃' + '\n' + 'Скорость ветра: ' + str(wind_speed) + ' м/c' + '\n'\
                  + weather_descriptions
    update.message.reply_text(weather_now)


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
    bot = Bot(
        token=TOKEN,
        base_url=PROXY,  # delete it if connection via VPN
    )
    updater = Updater(bot=bot, use_context=True)

    # on different commands - answer in Telegram
    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CommandHandler('help', chat_help))
    updater.dispatcher.add_handler(CommandHandler('history', history))
    updater.dispatcher.add_handler(CommandHandler('list', chat_list))
    updater.dispatcher.add_handler(CommandHandler('settings', admin_settings))
    updater.dispatcher.add_handler(CommandHandler('clean', admin_check_period))
    updater.dispatcher.add_handler(CommandHandler('fact', fact))
    updater.dispatcher.add_handler(CommandHandler('news', rbc_news))
    updater.dispatcher.add_handler(CommandHandler('covid', covid))
    updater.dispatcher.add_handler(CommandHandler('smile', smile))
    updater.dispatcher.add_handler(CommandHandler('weather', weather))
    updater.dispatcher.add_handler(CommandHandler('film', film))

    # on noncommand i.e message - echo the message on Telegram
    updater.dispatcher.add_handler(MessageHandler(Filters.text, echo))

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