#!/usr/bin/env python
"""Coaches lead users through each of their own diary programs."""

import telegram
import logging
import peewee as pw

from telegram.emoji import Emoji
from datetime import datetime, time, timedelta

from diary_peter.keyboards import keyboard, inline_keyboard
from diary_peter.models import User, Job, Record
from diary_peter.jobs import generic_job

logger = logging.getLogger(__name__)


def select(db, tguser):
    """Return active coach for a telegram user."""
    with db.transaction():
        user, created = User.tg_get_or_create(tguser)
        if created:
            logger.info("Created new user {}".format(user))
        return user.active_coach


class Coach(object):
    """Baseclass for coaches."""

    NAME = "Coach"

    def __init__(self, bot, db, tguser, job_queue):
        """Init coach object."""
        self.bot = bot
        self.db = db
        self.tguser = tguser
        self.job_queue = job_queue

        with db.transaction():
            user, created = User.tg_get_or_create(tguser)
            self.user = user


class Menu(Coach):
    """Main menu conversation."""

    NAME = "Menu"

    # Possible states for this coach
    START, AWAITING_DIARY_ENTRY = range(2)

    def handle(self, update):
        """Main menu shows primary interaction affordances."""
        out = []

        if self.user.state == self.AWAITING_DIARY_ENTRY:
            with self.db.transaction():
                rec = self.user.create_record("text", update.message.text)
                rec.save()

            out.append(self.bot.sendMessage(self.tguser.id,
                text="Ok, added."))

        elif self.user.state == self.START:
            # msg = "Just hit me up if you need anything."
            msg = "Just send me a message whenever you want to add something to today's diary."
            out.append(self.bot.sendMessage(self.tguser.id,
                text=msg, reply_markup=telegram.ReplyKeyboardHide()))

            # msg2 = "Or send me a message whenever you want to add something to today's diary."
            # options = {
            #     "coaches": "Change your coaches",
            #     "setup": "Edit settings",
            #     "discover": "Discover more"
            # }
            # out.append(self.bot.sendMessage(self.tguser.id,
            #     text=msg2
            #     reply_markup=inline_keyboard(options)
            # ))

            self.user.state = self.AWAITING_DIARY_ENTRY
            with self.db.transaction():
                self.user.save()
        return out


class Setup(Coach):
    """Configuration conversations."""

    NAME = "Setup"

    # Possible states for this coach
    START, AWAITING_NAME, AWAITING_WAKE_TIME, AWAITING_SELECTION_CONFIRMATION, \
        AWAITING_COACH_SELECTION = range(5)

    AVAILABLE_COACHES = {
        "Gratitude": "Gratitude"
    }

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
                out.append(self.bot.sendMessage(self.tguser.id, text=m,
                    reply_markup=telegram.ReplyKeyboardHide()))

            with self.db.transaction():
                self.user.state = self.AWAITING_NAME
                self.user.save()

        elif self.user.state == self.AWAITING_NAME:
            name = update.message.text
            out.append(self.bot.sendMessage(self.tguser.id,
                text="Sweet, {}! Now just a quick question to get an idea of your daily rhythm: *When do you usually get up?* \n\nYou can always change this later by typing */start*".format(name),
                reply_markup=keyboard('morning_hours'),
                parse_mode=telegram.ParseMode.MARKDOWN))

            with self.db.transaction():
                self.user.name = name
                self.user.state = self.AWAITING_WAKE_TIME
                self.user.save()

        elif self.user.state == self.AWAITING_WAKE_TIME:
            wake_time_resp = update.message.text
            try:
                wake_time = time(hour=int(wake_time_resp[:-2]))
            except ValueError:
                msg = "Please enter a wake time such as '9am'."
                out.append(self.bot.sendMessage(self.tguser.id,
                text=msg, reply_markup=keyboard('morning_hours')))
            else:
                if wake_time_resp[-2:] == "pm":
                    wake_time = wake_time + timedelta(hours=12)

                msg = "Ok, {}. I have a number of coaching ideas that can assist you with more specific goals like becoming conscious of your nutrition, sleep&dreams or reading habits. Are you interested in the selection?".format(wake_time_resp)
                out.append(self.bot.sendMessage(self.tguser.id,
                    text=msg, reply_markup=keyboard('thumbs')))

                with self.db.transaction():
                    self.user.wake_time = wake_time
                    self.user.state = self.AWAITING_SELECTION_CONFIRMATION
                    self.user.save()

        elif self.user.state in(self.AWAITING_SELECTION_CONFIRMATION, self.AWAITING_COACH_SELECTION):
            out.append(self.handle_coach_selection(update))

        return out

    def handle_coach_selection(self, update):
        """Handle selection of coaches.

        This method is called from the `handle` method.
        """
        out = []

        if self.user.state == self.AWAITING_SELECTION_CONFIRMATION:
            if update.message.text == Emoji.THUMBS_UP_SIGN:
                msgs = [
                    # "*nutrition*: I will ask you in the morning, afternoon and evening what you ate. Answer with a short description or snap a picture.",
                    # "*weight*: If you’d like I can also record your weight every morning.",
                    "*gratitude*: Every evening I will ask you to tell me three things that you were grateful for today. A study has shown that being mindful of the small good things in this way increases happiness for a long time!",
                    # "*sleep*: Would you like to sleep more regularly? I can give you a heads-up in time and then remind you to hit the sheets. In the morning I will ask you for how long you actually slept so you can see how your rest time improves after a while.",
                    # "*dream*: Additionally, I can ask you to tell me your dreams and keep these memories for you. Recording dreams this way will make you remember them more often and more clearly.",
                    # "*reading*: Do you like to read? Or would you? Write down what you read, what was interesting and gather a collection of insights and inspirations."
                ]

                out.append([self.bot.sendMessage(self.tguser.id,
                    text=m,
                    parse_mode=telegram.ParseMode.MARKDOWN,
                    reply_markup=telegram.ReplyKeyboardHide()) for m in msgs])

                kb = self.AVAILABLE_COACHES.copy()
                kb['continue'] = "Continue to main menu"

                out.append(self.bot.sendMessage(self.tguser.id,
                    text="Click a coach to add it now.",
                    reply_markup=inline_keyboard(kb)))

                with self.db.transaction():
                    self.user.state = self.AWAITING_COACH_SELECTION
                    self.user.save()
            else:
                out.append(self.bot.sendMessage(self.tguser.id,
                    parse_mode=telegram.ParseMode.MARKDOWN,
                    text="You can always change your selection later by typing */start*."))

                with self.db.transaction():
                    self.user.intro_seen = True
                    self.user.coach = "Menu"
                    self.user.state = Menu.START
                    self.user.save()

                menu = Menu(self.bot, self.db, self.tguser, self.job_queue)
                out.append(menu.handle(update))

        elif self.user.state == self.AWAITING_COACH_SELECTION:
            query = update.callback_query
            if not query:
                out.append(self.bot.sendMessage(self.tguser.id,
                    text="Please use the bottons above to select coaches to add or click continue to return to the main menu."))
                return out

            coach_name = query.data

            if coach_name == "continue":
                self.bot.answerCallbackQuery(query.id)
                out.append(self.bot.sendMessage(query.message.chat_id,
                    parse_mode=telegram.ParseMode.MARKDOWN,
                    text="You can always see the selection of available coaches later by typing */coaches*."))

                with self.db.transaction():
                    self.user.intro_seen = True
                    self.user.coach = "Menu"
                    self.user.state = Menu.START
                    self.user.save()

                menu = Menu(self.bot, self.db, self.tguser, self.job_queue)
                out.append(menu.handle(update))

            elif coach_name in self.AVAILABLE_COACHES:
                self.bot.answerCallbackQuery(query.id, text="Loading {} coach".format(coach_name))

                try:
                    Job.get(coach=coach_name, user=self.user)
                except pw.DoesNotExist:
                    out.append(self.bot.sendMessage(query.message.chat_id,
                        text="Now adding the {} coach.".format(coach_name)))
                    coach_cls = globals()[coach_name]
                    coach_cls.setup(self)
                    out.append(self.bot.sendMessage(query.message.chat_id,
                        text="Add another coach or click 'continue' above to finish.."))
                else:
                    out.append(self.bot.sendMessage(query.message.chat_id,
                        text="You have already added the {} coach".format(coach_name)))
            else:
                out.append(self.bot.sendMessage(query.message.chat_id,
                    text="That is not a coach here."))
        return out


class Gratitude(Coach):
    """Coach that teaches users to become grateful for the small things."""

    NAME = "Gratitude"
    MAIN, AWAITING_GRATITUDE, AWAITING_REASONS = range(3)

    collector = []

    def __init__(self, bot, db, tguser, job_queue):
        """Init and load collected items from past 24hours."""
        super().__init__(bot, db, tguser, job_queue)

        self.collector = list(self.user.records.select().where(
            Record.created >= datetime.now() - timedelta(hours=24)))

    @staticmethod
    def setup(setup_coach):
        """Setup this coach."""
        scheduled_dt = datetime.combine(
            datetime.today(), setup_coach.user.wake_time) - timedelta(hours=10)
        if scheduled_dt < datetime.now():
            scheduled_dt = scheduled_dt + timedelta(days=1)
        scheduled_remaining = scheduled_dt - datetime.now()
        # scheduled_remaining = timedelta(seconds=5)

        job, created = Job.get_or_create(
            coach=Gratitude.NAME,
            user=setup_coach.user,
            state=Gratitude.AWAITING_GRATITUDE,
            scheduled_at=datetime.time(scheduled_dt),
            text="Hey {name}, how was your day? Please send me three things that happened today that you are grateful for.".format(name=setup_coach.user.name)
        )
        with setup_coach.db.transaction():
            job.save()

        def jobfunc(bot):
            return generic_job(bot, job.id)

        interval = 24 * 60 * 60
        setup_coach.job_queue.put(jobfunc, interval,
            next_t=scheduled_remaining.seconds)

        logger.info("Saved {} and scheduled first run in {} hours".format(job, (scheduled_remaining.seconds/3600)))
        setup_coach.bot.sendMessage(setup_coach.user.telegram_id,
            text="Good choice! I will ask you every day at {time} to tell me three things you were grateful for in that day.".format(
                time=scheduled_dt.strftime("%-I %p")))

    def handle(self, update):
        """Handle updates from user."""
        n_things = len(self.collector)
        n_reasons = len([r for r in self.collector if r.reaction])
        start_menu = False

        if self.user.state == self.AWAITING_GRATITUDE:
            if n_things == 0:
                self.collector.append(
                    self.user.create_record(self.NAME, update.message.text))
                self.bot.sendMessage(self.tguser.id,
                    text="Ok. Two more!")

            elif n_things == 1:
                self.collector.append(
                    self.user.create_record(self.NAME, update.message.text))
                self.bot.sendMessage(self.tguser.id,
                    text="One left.")

            elif n_things == 2:
                self.collector.append(
                    self.user.create_record(self.NAME, update.message.text))
                self.bot.sendMessage(self.tguser.id,
                    parse_mode=telegram.ParseMode.MARKDOWN,
                    text="Nice! Now, about that first one:\n\n_{}_\n\n".format(
                        self.collector[0].content))
                self.bot.sendMessage(self.tguser.id,
                    text="Now tell me, what do you think why this particular good thing happened to you?")

                self.user.state = self.AWAITING_REASONS
                with self.db.transaction():
                    self.user.save()

        elif self.user.state == self.AWAITING_REASONS:
            if n_reasons == 0:
                self.collector[n_reasons].reaction = update.message.text
                self.bot.sendMessage(self.tguser.id,
                    parse_mode=telegram.ParseMode.MARKDOWN,
                    text="The second thing, why did that happen?\n\n_{}_".format(
                        self.collector[n_reasons + 1].content))
            elif n_reasons == 1:
                self.collector[n_reasons].reaction = update.message.text
                self.bot.sendMessage(self.tguser.id,
                    parse_mode=telegram.ParseMode.MARKDOWN,
                    text="And the third, how did that get to happen to you?\n\n_{}_".format(
                        self.collector[n_reasons + 1].content))
            elif n_reasons == 2:
                self.collector[n_reasons].reaction = update.message.text
                self.bot.sendMessage(self.tguser.id,
                    text="Good. I'll be back tomorrow.")

                start_menu = True

        with self.db.transaction():
            for r in self.collector:
                r.save()

        if start_menu:
            self.user.active_coach = Menu.NAME
            self.user.state = Menu.START
            with self.db.transaction():
                self.user.save()

            menu = Menu(self.bot, self.db, self.tguser, self.job_queue)
            menu.handle(update)
