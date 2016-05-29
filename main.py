#!/usr/bin/env python

"""Diary Peter is a bot that helps become more conscious of your every day life.

Diary Peter was built for the telegram platform and is available for usage
via http://telegram.me/diarypete_bot.

Please see https://github.com/ciex/diary-peter for additional information about
the bot.
"""

import logging
import os

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, \
    CallbackQueryHandler
from diary_peter import coaches
from diary_peter.models import db

__author__ = "Vincent Ahrend"
__copyright__ = "Copyright 2016, Vincent Ahrend"
__version__ = "1.0.0"
__maintainer__ = "Vincent Ahrend"
__email__ = "mail@vincentahrend.com"
__status__ = "Development"


logging.basicConfig(
    format='%(levelname)s\t%(name)s\t\t%(message)s',
    level=logging.INFO)
logger = logging.getLogger(__name__)

job_queue = None


def update_handler(bot, update):
    """Handle updates by routing them to the appropriate coach."""
    try:
        tguser = update.message.from_user
    except AttributeError:
        tguser = update.callback_query.from_user

    coach_name = coaches.select(db, tguser)
    coach_cls = getattr(coaches, coach_name)
    coach = coach_cls(bot, db, tguser, job_queue)

    logger.info("User {} entering {}:{}".format(
        tguser.id, coach_name, coach.user.state))
    coach.handle(update)


def main():
    """Main loop."""
    global job_queue

    token = os.environ.get("TG_TOKEN", False)
    if not token:
        print("TG_TOKEN environment variable not set")
        quit()

    updater = Updater(token)
    dp = updater.dispatcher

    job_queue = updater.job_queue

    dp.add_handler(CommandHandler('start', update_handler))
    dp.add_handler(MessageHandler([Filters.text], update_handler))
    dp.add_handler(CallbackQueryHandler(update_handler))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
