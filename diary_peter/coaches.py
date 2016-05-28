#!/usr/bin/env python
"""Coaches lead users through each of their own diary programs."""

import datetime
import logging
import telegram

from diary_peter.keyboards import keyboard
from diary_peter.models import User


class Config:
    """Configuration conversations."""

    NAME = "Config"

    # Possible states for this coach
    START, AWAITING_WAKE_TIME, AWAITING_SELECTION_CONFIRMATION = range(3)

    @staticmethod
    def new_user(bot, update, db):
        """Setup a user account by asking some basic questions."""
        out = []

        with db.transaction():
            user, created = User.tg_get_or_create(update.message.from_user)
            user.state_module = Config.NAME
            user.save()

        if user.state == Config.START:
            out.append(bot.sendMessage(update.message.chat_id,
                text="Just a quick question to get an idea of your daily rhythm: *When do you usually get up?* \n\nYou can always change this later by typing */setup*",
                reply_markup=keyboard('morning_hours'),
                parse_mode=telegram.ParseMode.MARKDOWN))

            with db.transaction():
                user.state = Config.AWAITING_WAKE_TIME
                user.save()

        elif user.state == Config.AWAITING_WAKE_TIME:
            wake_time_resp = update.message.text
            try:
                wake_time = datetime.time(hour=int(wake_time_resp[:-2]))
            except ValueError:
                msg = "Please enter a wake time such as '9am'."
                out.append(bot.sendMessage(update.message.chat_id,
                text=msg, reply_markup=keyboard('morning_hours')))
            else:
                if wake_time_resp[-2:] == "pm":
                    wake_time = wake_time + datetime.timedelta(hours=12)

                msg = "Ok, {}. I have a number of coaching ideas that can assist you with more specific goals like becoming conscious of your nutrition, sleep&dreams or reading habits. Are you interested in the selection?".format(wake_time_resp)
                out.append(bot.sendMessage(update.message.chat_id,
                    text=msg, reply_markup=keyboard('thumbs')))

                with db.transaction():
                    user.wake_time = wake_time
                    user.state = Config.AWAITING_SELECTION_CONFIRMATION
                    user.save()

        return out
