#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

import logging
import datetime
from functools import wraps
from setup import PROXY, TOKEN
from telegram import Bot, Update
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
        update.message.reply_text('Список функций для администрирования: ')


@log_action
@decorator_error
def chat_list(update: Update, context: CallbackContext):
    """Send a list of all available functions when the command /list is issued."""
    update.message.reply_text('Доступные команды:\n/start\n/help\n/history')


@log_action
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
    updater.dispatcher.add_handler(CommandHandler('adminsettings', admin_settings))

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
