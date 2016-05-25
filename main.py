#!/usr/bin/env python

"""Diary Peter is a bot that helps become more conscious of your every day life.

Diary Peter was built for the telegram platform and is available for usage
via http://telegram.me/diarypete_bot.

Please see https://github.com/ciex/diary-peter for additional information about
the bot.
"""

import os

from telegram.ext import Updater, CommandHandler

__author__ = "Vincent Ahrend"
__copyright__ = "Copyright 2015, Vincent Ahrend"
__version__ = "1.0.0"
__maintainer__ = "Vincent Ahrend"
__email__ = "mail@vincentahrend.com"
__status__ = "Development"


def start(bot, update):
    bot.sendMessage(update.message.chat_id, text='Hello World!')

def hello(bot, update):
    bot.sendMessage(update.message.chat_id,
                    text='Hello {0}'.format(update.message.from_user.first_name))

token = os.environ.get("TG_TOKEN", False)
if not token:
    print("TG_TOKEN environment variable not set")
    quit()

updater = Updater(token)

updater.dispatcher.addHandler(CommandHandler('start', start))
updater.dispatcher.addHandler(CommandHandler('hello', hello))

updater.start_polling()
updater.idle()
