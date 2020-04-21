#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

import logging
import random
from datetime import datetime, date, timedelta
import requests
import os
from functools import wraps
from selenium import webdriver
import pandas as pd
import matplotlib.pyplot as plt
from setup import PROXY, TOKEN, TOKEN_WEATHER
from google.cloud import speech_v1
from google.cloud.speech_v1 import enums
import subprocess
from telegram import Bot, Update, InputMediaPhoto, PhotoSize, bot
from telegram.ext import CallbackContext, CommandHandler, Filters, MessageHandler, Updater

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


os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "path_to_your_.json_credential_file"

class CovidStatistics:
    def top_five(self):
        raise RuntimeError

    def image_create(self):
        raise RuntimeError



class files:
    HistoryFile = "History.txt"
    AdminHistoryFile = "Admin_History.txt"
    FilmFile = 'Film Library.txt'

    def NewLog(self, update, funcname):
        LOG_ACTIONS.append({
            'user': update.effective_user.first_name,
            'user id': update.message.chat.id,
            'function': funcname,
            'message': update.message.text,
            'time': datetime.now().strftime("%Y-%m-%d %H.%M")})
        if str(LOG_ACTIONS[-1]['function']).find('admin') == -1:
            with open(files.HistoryFile, "a", encoding="UTF-8") as file_h:
                for key, value in LOG_ACTIONS[-1].items():
                    file_h.write(key + ':' + (str(value)) + "\t")
                file_h.write("\n")
        elif str(LOG_ACTIONS[-1]['function']).find('admin') != -1:
            with open(files.AdminHistoryFile, "a", encoding="UTF-8") as handler:
                for key, value in LOG_ACTIONS[-1].items():
                    handler.write(key + ':' + (str(value)) + "\t")
                handler.write("\n")

    def history(self):
        """Send user last 5 records from history."""
        hist = ""
        with open(files.HistoryFile, "r", encoding="UTF-8") as file_h:
            hist_all = file_h.readlines()
            if len(hist_all) > 4:
                for i in range(-1, -6, -1):
                    hist += hist_all[i]
            else:
                hist = "\t".join(hist_all)
        return hist

    def DeleteLogs(self):
        k = 0
        with open(files.HistoryFile, "r", encoding="UTF-8") as file_h:
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
        with open(files.HistoryFile, 'w') as file_h:
            file_h.writelines(hist_all[k:])


class CovidStats(CovidStatistics):
    def Upload(self):
        yesterday = date.today() - timedelta(days=1)
        y = str(yesterday)[: 4]
        m = str(yesterday)[5: 7]
        d = str(yesterday)[8:]
        url = f'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/{m}-{d}-{y}.csv'
        data = pd.read_csv(url)
        return data

    def Sort(self, data, ascending):
        data = data.sort_values('Confirmed', ascending=ascending)
        data['Province_State'] = data['Province_State'].fillna('')
        return data

    def top_five(self, data):
        top_5 = data[['Province_State', 'Country_Region', 'Last_Update', 'Confirmed', 'Deaths', 'Recovered']].iloc[:5]
        text = ''
        for col in top_5:
            text += col + '\t\t'
        text += '\n\n'
        for i in top_5.values:
            for j in i:
                text += str(j) + '\t\t'
            text += '\n\n'
        return text

    def image_create(self,data):
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


class UrlRequests:
    def get_film(self, update):
        text = open(files.FilmFile, 'r')
        film_list = text.read().split()
        film_name = film_list[random.randint(0, len(film_list) - 1)]
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
        return [title,rating,length,main_role]

    def get_weather(TOKEN, CITY):
        url = f'http://api.weatherstack.com/current?access_key={TOKEN}&query={CITY}'

        r = requests.get(url)
        if r.status_code == 200:
            r = r.json()
            city = r.get('request')['query']
            time = r.get('current')['observation_time']
            temperature = r.get('current')['temperature']
            weather_descriptions = r.get('current')['weather_descriptions'][0]
            wind_speed = r.get('current')['wind_speed']
            wind_speed = round(wind_speed * 1000.0 / 3600.0)
            weather_now = 'Город: ' + city + '\n' + 'Время снятия данных: ' + str(time) + '\n' + 'Температура: ' + \
                          str(temperature) + '℃' + '\n' + 'Скорость ветра: ' + str(wind_speed) + ' м/c' + '\n' \
                          + weather_descriptions
        else:
            weather_now = 'Функция в данный момент недоступна'
        return weather_now


class CovidStatsDaily(CovidStatistics):
    @staticmethod
    def read_covid_data(date):
        y = str(date)[: 4]
        m = str(date)[5: 7]
        d = str(date)[8:]

        url = f'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/{m}-{d}-{y}.csv'
        return pd.read_csv(url)

    def __init__(self):
        self.today = date.today() - timedelta(days=1)  # т.к. выкладывают поздно, от-но мск времени
        self.yesterday = date.today() - timedelta(days=2)

        self.data_t = self.read_covid_data(self.today)
        self.data_y = self.read_covid_data(self.yesterday)

        self.data_t = self.data_t.sort_values('Confirmed', ascending=False)
        self.data_y = self.data_y.sort_values('Confirmed', ascending=False)

        self.confirmed_dif = self.data_t['Confirmed'].sum() - self.data_y['Confirmed'].sum()
        self.dead_dif = self.data_t['Deaths'].sum() - self.data_y['Deaths'].sum()
        self.recov_dif = self.data_t['Recovered'].sum() - self.data_y['Recovered'].sum()

    def image_create(self):
        fig, ax = plt.subplots(figsize=(15, 15))

        ax.bar("Confirmed", self.confirmed_dif, color="#FFA07A")
        ax.bar("Dead", self.dead_dif, color="#B0E0E6")
        ax.bar("Recovered", self.recov_dif, color="#7CFC00")
        # plt.text("Confirmed", all_confirmed_dif, str(all_confirmed_dif))
        plt.title(f"Daily changes in... (from {self.yesterday} to {self.today})")
        fig.savefig("Covid_stats")

    def top_five(self):
        top_5_t = self.data_t[
                      ['Province_State', 'Country_Region', 'Last_Update', 'Confirmed', 'Deaths', 'Recovered']].iloc[:5]
        top_5_y = self.data_y[
                      ['Province_State', 'Country_Region', 'Last_Update', 'Confirmed', 'Deaths', 'Recovered']].iloc[:5]

        fig = plt.figure(figsize=(15, 15))
        plt.subplot(1, 2, 1).set_title("Today")
        ax = plt.pie(top_5_t["Confirmed"], labels=top_5_t["Country_Region"], autopct='%1.1f%%')
        plt.subplot(1, 2, 2).set_title("Yesterday")
        ax = plt.pie(top_5_y["Confirmed"], labels=top_5_t["Country_Region"], autopct='%1.1f%%')
        fig.savefig("Top_5_pie")

        fig = plt.figure(figsize=(15, 15))
        plt.subplot(2, 1, 1).set_title("Today")
        ax = plt.bar(top_5_t["Country_Region"], top_5_t["Confirmed"], color="#FF6347")
        plt.subplot(2, 1, 2).set_title("Yesterday")
        ax = plt.bar(top_5_y["Country_Region"], top_5_y["Confirmed"], color="#87CEFA")
        fig.savefig("Top_5_bar")

        self.data_t = self.data_t.sort_values('Deaths', ascending=False)
        self.data_y = self.data_y.sort_values('Deaths', ascending=False)
        top_5_t = self.data_t[
                      ['Province_State', 'Country_Region', 'Last_Update', 'Confirmed', 'Deaths', 'Recovered']].iloc[:5]
        top_5_y = self.data_y[
                      ['Province_State', 'Country_Region', 'Last_Update', 'Confirmed', 'Deaths', 'Recovered']].iloc[:5]

        fig = plt.figure(figsize=(15, 15))
        plt.subplot(2, 1, 1).set_title("Today")
        ax = plt.bar(top_5_t["Country_Region"], top_5_t["Deaths"], color="#FF6347")
        plt.subplot(2, 1, 2).set_title("Yesterday")
        ax = plt.bar(top_5_y["Country_Region"], top_5_y["Deaths"], color="#87CEFA")
        fig.savefig("Top_5_bar_death")


class SpeechToText:
    def __init__(self, local_file_path):
        self.local_file_path = local_file_path

    def sample_recognize(self):
        transcript = ''
        client = speech_v1.SpeechClient()
        language_code = "ru-RU"
        sample_rate_hertz = 48000
        encoding = enums.RecognitionConfig.AudioEncoding.LINEAR16
        config = {
            "language_code": language_code,
            "sample_rate_hertz": sample_rate_hertz,
            "encoding": encoding,
        }
        with os.io.open(self.local_file_path, "rb") as f:
            content = f.read()
        audio = {"content": content}
        response = client.recognize(config, audio)
        for result in response.results:
            alternative = result.alternatives[0]
            transcript = alternative.transcript
        if transcript == '':
            transcript = 'Не удалось перевести.'
        return transcript


def voice_message(update: Update, context: CallbackContext):
    file_info = context.bot.get_file(update.message.voice.file_id)
    file_info.download('VOICE.ogg')
    command = [
        r'Project\bin\ffmpeg.exe', # путь до ffmpeg.exe
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
            files.NewLog(files, update, funcname)
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
def corona_stats_dynamics(update: Update, context: CallbackContext):
    cd = CovidStatsDaily()
    cd.image_create()
    cd.top_five()

    update.message.reply_text('Below you\'ll be provided with daily changes in covid-19 statistics')
    Bot.send_photo(bot, update.message.chat.id, open('Covid_stats.png', 'rb'))
    update.message.reply_text('Top-5 injured countries by Confirmed')
    Bot.send_photo(bot, update.message.chat.id, open('Top_5_pie.png', 'rb'))
    Bot.send_photo(bot, update.message.chat.id, open('Top_5_bar.png', 'rb'))
    update.message.reply_text('Top-5 injured countries by Death')
    Bot.send_photo(bot, update.message.chat.id, open('Top_5_bar_death.png', 'rb'))




@log_action
@decorator_error
def admin_settings(update: Update, context: CallbackContext):
    """Send a list of AdminOnly commands"""
    if update.effective_user.first_name =='Meseyoshi':
        update.message.reply_text('Список функций для администрирования:\n/clean  ')


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
    data = CovidStats.Upload(CovidStats)
    data = CovidStats.Sort(CovidStats,data,False)
    text = CovidStats.top_five(CovidStats,data)
    update.message.reply_text( 'Here you can find some statistic about top-5 covid infected regions')
    update.message.reply_text(text)
    update.message.reply_text('And about about top-5 covid least infected regions')
    data = CovidStats.Sort(CovidStats, data, True)
    text = CovidStats.top_five(CovidStats, data)
    update.message.reply_text(text)
    CovidStats.image_create(CovidStats,data)
    Bot.send_photo(bot, update.message.chat.id, open('Covid_statistics.png', 'rb'))
    Bot.send_photo(bot, update.message.chat.id, open('Covid_weekly_changes.png', 'rb'))

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
    update.message.reply_text('Доступные команды:\n/history\n/fact\n/weather\n/smile\n/film\n/covid')


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
    update.message.reply_text(files.history(files))

@log_action
@decorator_error
def admin_check_period(update: Update, context: CallbackContext):
    files.DeleteLogs(files)
    mes = 'Готово!'
    update.message.reply_text(mes)


@log_action
@decorator_error
def weather(update: Update, context: CallbackContext):
    update.message.reply_text(UrlRequests.get_weather(TOKEN_WEATHER, CITY))




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
    updater.dispatcher.add_handler(CommandHandler('weather', weather))
    updater.dispatcher.add_handler(CommandHandler('film', film))
    updater.dispatcher.add_handler(CommandHandler('dynamics', corona_stats_dynamics))


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