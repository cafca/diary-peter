#!/usr/bin/env python
"""Coaches lead users through each of their own diary programs."""

import datetime

from diary_peter import keyboards
from diary_peter.models import User


class Config:
    """Configuration conversations."""

    @staticmethod
    def new_user(bot, update, db):
        """Setup a user account by asking some basic questions."""
        out = []

        with db.transaction():
            user = User.get_or_create(user=update.message.from_user)
            user.state_module = "setup"

        START, AWAITING_WAKE_TIME, AWAITING_SELECTION_CONFIRMATION = range(3)

        if user.state == START:
            out.append(bot.sendMessage(update.message.chat_id,
                text="Just a quick question to get an idea of your daily rhythm: *When do you usually get up?* \n\nYou can always change this later by typing */setup*",
                reply_markup=keyboards.morning_hours))

            with db.transaction():
                user.state = AWAITING_WAKE_TIME

        elif user.state == AWAITING_WAKE_TIME:
            wake_time_resp = update.message.text
            wake_time = datetime.time(hour=int(wake_time_resp[:-3]))
            if wake_time_resp[-2:] == "pm":
                wake_time = wake_time + datetime.timedelta(hours=12)

            msg = "Ok, {}. I have a number of coaching ideas that can assist you with more specific goals like becoming conscious of your nutrition, sleep&dreams or reading habits. Are you interested in the selection?".format(wake_time_resp)
            out.append(bot.sendMessage(update.message.chat_id, text=msg, reply_markup=keyboards.thumbs))

            with db.transaction():
                user.wake_time = wake_time
                user.state = AWAITING_SELECTION_CONFIRMATION

        return out
