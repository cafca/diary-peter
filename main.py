import os
from telegram.ext import Updater, CommandHandler


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
