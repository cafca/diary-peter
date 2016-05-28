#!/usr/bin/env python
"""Coaches lead users through each of their own diary programs."""

import datetime
import logging
import telegram

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.emoji import Emoji

from diary_peter.keyboards import keyboard
from diary_peter.models import User


class Coach(object):
    """Baseclass for coaches."""

    NAME = "Coach"

    def __init__(self, bot, db, tguser):
        """Init coach object."""
        self.bot = bot
        self.db = db
        self.tguser = tguser

        with db.transaction():
            user, created = User.tg_get_or_create(tguser)
            self.user = user

    @staticmethod
    def select(db, tguser):
        """Return active coach for a telegram user."""
        with db.transaction():
            user, created = User.tg_get_or_create(tguser)
            if created:
                logging.info("Created new user {} in database".format(user))
            return user.active_coach


class Menu(Coach):
    """Main menu conversation."""

    NAME = "Menu"

    # Possible states for this coach
    START, AWAITING_DIARY_ENTRY = range(2)

    def menu_keyboard(self):
        """Return an inline keyboard listing options for user's main menu."""
        options = {
            "coaches": "Change your coaches",
            "setup": "Edit settings",
            "discover": "Discover more"
        }
        rv = InlineKeyboardMarkup(
            [[InlineKeyboardButton(v, callback_data=k)]
            for k, v in options.items()])
        return rv

    def handle(self, update):
        """Main menu shows primary interaction affordances."""
        out = []

        if self.user.state == self.AWAITING_DIARY_ENTRY:
            with self.db.transaction():
                rec = self.user.create_record("text", update.message.text)
                rec.save()

            out.append(self.bot.sendMessage(update.message.chat_id,
                text="Ok, added."))

        elif self.user.state == self.START:
            msg = "Just hit me up if you need anything or send me a message to add it to your diary."
            out.append(self.bot.sendMessage(update.message.chat_id,
                text=msg, reply_markup=self.menu_keyboard()))

            with self.db.transaction():
                self.user.state = self.AWAITING_DIARY_ENTRY
        return out


class Setup(Coach):
    """Configuration conversations."""

    NAME = "Setup"

    # Possible states for this coach
    START, AWAITING_NAME, AWAITING_WAKE_TIME, AWAITING_SELECTION_CONFIRMATION, \
        AWAITING_COACH_SELECTION = range(5)

    def handle(self, update):
        """Setup a user account by asking some basic questions."""
        out = []

        with self.db.transaction():
            self.user.active_coach = self.NAME
            self.user.save()

        if self.user.state == self.START:
            messages = [
                "Hello there!",
                "I am Diary Peter, and I will increase your awareness of your every day",
                "Every evening, I will ask you about your day. After some time, you can look back and remember all the nice things.",
                "I am trying to keep this as anonymous as possible, so I will not store your telegram nickname anywhere. \n\nWhat name may I call you by instead?"
            ]

            for m in messages:
                out.append(self.bot.sendMessage(update.message.chat_id, text=m,
                    reply_markup=telegram.ReplyKeyboardHide()))

            with self.db.transaction():
                self.user.state = self.AWAITING_NAME
                self.user.save()

        elif self.user.state == self.AWAITING_NAME:
            name = update.message.text
            out.append(self.bot.sendMessage(update.message.chat_id,
                text="Sweet, {}! Now just a quick question to get an idea of your daily rhythm: *When do you usually get up?* \n\nYou can always change this later by typing */setup*".format(name),
                reply_markup=keyboard('morning_hours'),
                parse_mode=telegram.ParseMode.MARKDOWN))

            with self.db.transaction():
                self.user.name = name
                self.user.state = self.AWAITING_WAKE_TIME
                self.user.save()

        elif self.user.state == self.AWAITING_WAKE_TIME:
            wake_time_resp = update.message.text
            try:
                wake_time = datetime.time(hour=int(wake_time_resp[:-2]))
            except ValueError:
                msg = "Please enter a wake time such as '9am'."
                out.append(self.bot.sendMessage(update.message.chat_id,
                text=msg, reply_markup=keyboard('morning_hours')))
            else:
                if wake_time_resp[-2:] == "pm":
                    wake_time = wake_time + datetime.timedelta(hours=12)

                msg = "Ok, {}. I have a number of coaching ideas that can assist you with more specific goals like becoming conscious of your nutrition, sleep&dreams or reading habits. Are you interested in the selection?".format(wake_time_resp)
                out.append(self.bot.sendMessage(update.message.chat_id,
                    text=msg, reply_markup=keyboard('thumbs')))

                with self.db.transaction():
                    self.user.wake_time = wake_time
                    self.user.state = self.AWAITING_SELECTION_CONFIRMATION
                    self.user.save()

        elif self.user.state == self.AWAITING_SELECTION_CONFIRMATION:
            if update.message.text == Emoji.THUMBS_UP_SIGN:
                msgs = ["*nutrition*: I will ask you in the morning, afternoon and evening what you ate. Answer with a short description or snap a picture.",
                    "*weight*: If you’d like I can also record your weight every morning.",
                    "*grateful*: Every evening I will ask you for three things that you were grateful for today. A study by [name] has shown that being mindful of the small good things in this way increases happiness for a long time!",
                    "*sleep*: Would you like to sleep more regularly? I can give you a heads-up in time and then remind you to hit the sheets. In the morning I will ask you for how long you actually slept so you can see how your rest time improves after a while.",
                    "*dream*: Additionally, I can ask you to tell me your dreams and keep these memories for you. Recording dreams this way will make you remember them more often and more clearly.",
                    "*reading*: Do you like to read? Or would you? Write down what you read, what was interesting and gather a collection of insights and inspirations.",
                    "Just type the name of a program to add it now. You can see these later again by typing */coaches*"]
                out.append([self.bot.sendMessage(update.message.chat_id,
                    text=m,
                    parse_mode=telegram.ParseMode.MARKDOWN,
                    reply_markup=telegram.ReplyKeyboardHide()) for m in msgs])

                with self.db.transaction():
                    self.user.state = self.AWAITING_COACH_SELECTION
                    self.user.save()
            else:
                out.append(self.bot.sendMessage(update.message.chat_id,
                    parse_mode=telegram.ParseMode.MARKDOWN,
                    text="You can always see the selection of available coaches later by typing */coaches*."))

                with self.db.transaction():
                    self.user.intro_seen = True
                    self.user.state = Menu.START
                    self.user.save()

                menu = Menu(self.bot, self.db, self.tguser)
                out.append(menu.handle(update))

        return out
