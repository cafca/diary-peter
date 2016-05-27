#!/usr/bin/env python

"""Diary Peter is a bot that helps become more conscious of your every day life.

Diary Peter was built for the telegram platform and is available for usage
via http://telegram.me/diarypete_bot.

Please see https://github.com/ciex/diary-peter for additional information about
the bot.
"""

import logging
import os

from telegram.ext import Updater, CommandHandler
from diary_peter.dispatchers import start, hello

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

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
