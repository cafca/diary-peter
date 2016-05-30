#!/usr/bin/env python

"""Diary Peter is a bot that helps become more conscious of your every day life.

Diary Peter was built for the telegram platform and is available for usage
via http://telegram.me/diarypete_bot.

Please see https://github.com/ciex/diary-peter for additional information about
the bot.
"""

# Copyright 2016 Vincent Ahrend

#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at

#      http://www.apache.org/licenses/LICENSE-2.0

#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import os
import logging

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, \
    CallbackQueryHandler

from diary_peter import coaches
from diary_peter.models import db
from diary_peter.jobs import restore_jobs

__author__ = "Vincent Ahrend"
__copyright__ = "Copyright 2016, Vincent Ahrend"
__version__ = "1.0.0"
__maintainer__ = "Vincent Ahrend"
__email__ = "mail@vincentahrend.com"
__status__ = "Development"

job_queue = None

logging.basicConfig(
    format='%(asctime)s %(levelname) 8s\t%(name) 25s\t%(message)s',
    level=logging.DEBUG,
    filename="../peter.log")
logger = logging.getLogger(__name__)


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
    restore_jobs(job_queue)

    dp.add_handler(CommandHandler('start', update_handler))
    dp.add_handler(MessageHandler([Filters.text], update_handler))
    dp.add_handler(CallbackQueryHandler(update_handler))

    updater.start_polling()
    logger.info("Polling started")

    updater.idle()

if __name__ == '__main__':
    main()
