#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

import logging
import datetime
import requests
from functools import wraps
from setup import PROXY, TOKEN
from telegram import Bot, Update
from telegram.ext import CallbackContext, CommandHandler, Filters, MessageHandler, Updater
import random

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
            'time': datetime.datetime.now().strftime("%Y-%m-%d %H.%M"), })
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
def admin_settings(update: Update, context: CallbackContext):
    """Send a list of AdminOnly commands"""
    if update.effective_user.first_name =='Meseyoshi':
        update.message.reply_text('Список функций для администрирования:\n/clean ')




@log_action
@decorator_error
def chat_list(update: Update, context: CallbackContext):
    """Send a list of all available functions when the command /list is issued."""
    update.message.reply_text('Доступные команды:\n/start\n/help\n/history\n/fact')


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
        hist_time = datetime.datetime.strptime(hist_time, "%Y-%m-%d %H.%M")
        now = datetime.datetime.now()
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
    print(cat_fact)
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
