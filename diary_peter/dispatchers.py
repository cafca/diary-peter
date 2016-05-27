#!/usr/bin/env python
"""Dispatchers for handling incoming messages."""

from diary_peter.models import db, User
from diary_peter.coaches import Config


def start(bot, update):
    """Initial message for new users."""
    out = []
    user = User.get_or_create(user=update.message.from_user)
    db.connect()

    messages = [
        "Hello {}".format(update.message.from_user.first_name),
        "I am Diary Peter, and I can help you become more conscious of your day-to-day.",
        "Every evening, I will ask you about your day. After some time, you can look back and remember all the nice things."
    ]

    for m in messages:
        out.append(bot.sendMessage(update.message.chat_id, text=m))

    if user.intro_seen is False:
        out.append(Config.new_user(bot, update, db))

    db.close()
    return out


def hello(bot, update):
    bot.sendMessage(update.message.chat_id,
                    text='Hello {0}: {}'.format(update.message.from_user.first_name, update.message.chat_id))
