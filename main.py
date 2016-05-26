#!/usr/bin/env python

"""Diary Peter is a bot that helps become more conscious of your every day life.

Diary Peter was built for the telegram platform and is available for usage
via http://telegram.me/diarypete_bot.

Please see https://github.com/ciex/diary-peter for additional information about
the bot.
"""

import datetime
import logging
import os

from telegram.ext import Updater, CommandHandler

from diary_peter import keyboards
from diary_peter.models import User, db

__author__ = "Vincent Ahrend"
__copyright__ = "Copyright 2016, Vincent Ahrend"
__version__ = "1.0.0"
__maintainer__ = "Vincent Ahrend"
__email__ = "mail@vincentahrend.com"
__status__ = "Development"


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)
logger = logging.getLogger(__name__)


def setup(bot, update, db):
    """Setup a user account by asking some basic questions."""
    with db.transaction():
        user = User.get_or_create(user=update.message.from_user)
        user.state_module = "setup"

    START, AWAITING_WAKE_TIME, AWAITING_SELECTION_CONFIRMATION = range(3)

    if user.state == START:
        bot.sendMessage(update.message.chat_id,
            text="Just a quick question to get an idea of your daily rhythm: *When do you usually get up?* \n\nYou can always change this later by typing */setup*",
            reply_markup=keyboards.morning_hours)

        with db.transaction():
            user.state = AWAITING_WAKE_TIME

    elif user.state == AWAITING_WAKE_TIME:
        wake_time_resp = update.message.text
        wake_time = datetime.time(hour=int(wake_time_resp[:-3]))
        if wake_time_resp[-2:] == "pm":
            wake_time = wake_time + datetime.timedelta(hours=12)

        msg = "Ok, {}. I have a number of coaching ideas that can assist you with more specific goals like becoming conscious of your nutrition, sleep&dreams or reading habits. Are you interested in the selection?".format(wake_time_resp)
        bot.sendMessage(update.message.chat_id, text=msg, reply_markup=keyboards.thumbs)

        with db.transaction():
            user.wake_time = wake_time
            user.state = AWAITING_SELECTION_CONFIRMATION


def start(bot, update):
    user = User.get_or_create(user=update.message.from_user)
    db.connect()

    messages = [
        "Hello {}".format(update.message.from_user.first_name),
        "I am Diary Peter, and I can help you become more conscious of your day-to-day.",
        "Every evening, I will ask you about your day. After some time you can look back and remember all the nice things."
    ]

    for m in messages:
        bot.sendMessage(update.message.chat_id, text=m)

    if user.intro_seen is False:
        setup(bot, update, db)

    db.close()


def hello(bot, update):
    bot.sendMessage(update.message.chat_id,
                    text='Hello {0}'.format(update.message.from_user.first_name))


def error(bot, update, error):
    """Catch errors from dispatcher."""
    logger.warn('Update "%s" caused error "%s"' % (update, error))


def main():
    """Main loop."""
    token = os.environ.get("TG_TOKEN", False)
    if not token:
        print("TG_TOKEN environment variable not set")
        quit()

    updater = Updater(token)
    dp = updater.dispatcher

    dp.addHandler(CommandHandler('start', start))
    dp.addHandler(CommandHandler('hello', hello))

    # dp.add_error_handler(error)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
