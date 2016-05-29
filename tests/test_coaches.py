#!/usr/bin/env python
"""Tests for all coaches."""

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

import pytest
import telegram
import peewee

from playhouse.test_utils import test_database
from telegram.emoji import Emoji

from conftest import custom_update, inline_query
from diary_peter.coaches import Setup, Coach, Menu, Gratitude
from diary_peter.models import db, User, Record, Job


class TestBaseCoach:
    """Test base class."""

    def test_init(self, bot, tguser, test_db, updater):
        """Test initialization of the base coach class."""
        with test_database(test_db, [User], fail_silently=True):
            coach = Coach(bot, test_db, tguser, updater.job_queue)

            assert isinstance(coach.bot, telegram.Bot)
            assert isinstance(coach.db, peewee.Database)
            assert isinstance(coach.user, User)
            assert isinstance(coach.tguser, telegram.user.User)


class TestMenu:
    """Test menu coach."""

    @pytest.fixture(params=[
        (Menu.START, Menu.AWAITING_DIARY_ENTRY, ""),
        (Menu.START, Menu.AWAITING_DIARY_ENTRY, "Test"),
        (Menu.AWAITING_DIARY_ENTRY, Menu.AWAITING_DIARY_ENTRY, "Test diary entry."),
    ])
    def menu_update(self, request):
        """Return custom updates for testing state transition and message handling.

        Parameters:
            Integer: Incoming state
            Integer: Expected outgoing state
            String: Message to pass
        """
        rv = custom_update(msg=request.param[2])
        rv.states = request.param[:2]
        return rv

    def test_handle(self, bot, menu_update, test_db, tguser, updater):
        """Test display of main menu."""
        with test_database(test_db, [User, Record], fail_silently=True):
            with db.transaction():
                user, created = User.tg_get_or_create(tguser)
                user.state = menu_update.states[0]
                user.save()

            coach = Menu(bot, db, tguser, updater.job_queue)
            msgs = coach.handle(menu_update)

            assert len(msgs) > 0

    def test_diary_entry(self, bot, test_db, tguser, updater):
        """Test diary entry from main menu."""
        diary_entry = "My secret diary."

        with test_database(test_db, [User, Record], fail_silently=True):
            with db.transaction():
                user, created = User.tg_get_or_create(tguser)
                user.state = Menu.AWAITING_DIARY_ENTRY
                user.save()

            coach = Menu(bot, db, tguser, updater.job_queue)
            msgs = coach.handle(custom_update(msg=diary_entry))

            assert len(msgs) == 1

            rec = Record.get(Record.content == diary_entry)
            assert isinstance(rec, Record)


class TestSetup:
    """Test setup coach."""

    @pytest.fixture(params=[
        (Setup.START, Setup.AWAITING_NAME, ""),
        (Setup.AWAITING_NAME, Setup.AWAITING_WAKE_TIME, "Max"),
        (Setup.AWAITING_WAKE_TIME, Setup.AWAITING_SELECTION_CONFIRMATION, "9am"),
        (Setup.AWAITING_WAKE_TIME, Setup.AWAITING_WAKE_TIME, "Man, I don't know."),
        (Setup.AWAITING_SELECTION_CONFIRMATION, Menu.START, Emoji.THUMBS_DOWN_SIGN),
        (Setup.AWAITING_SELECTION_CONFIRMATION, Setup.AWAITING_COACH_SELECTION, Emoji.THUMBS_UP_SIGN),
    ])
    def setup_update(self, request):
        """Return custom updates for testing state transition and message handling.

        Parameters:
            Integer: Incoming state
            Integer: Expected outgoing state
            String: Message to pass
        """
        rv = custom_update(msg=request.param[2])
        rv.states = request.param[:2]
        return rv

    def test_handle(self, bot, setup_update, test_db, updater):
        """Test setup handler."""
        with test_database(test_db, [User], fail_silently=True):
            with db.transaction():
                user, created = User.tg_get_or_create(
                    setup_update.message.from_user)
                user.state = setup_update.states[0]
                user.save()

            coach = Setup(bot, test_db, setup_update.message.from_user, updater.job_queue)
            messages = coach.handle(setup_update)

            user, created = User.tg_get_or_create(
                setup_update.message.from_user)

            assert len(messages) > 0
            assert user.state == setup_update.states[1]

    @pytest.fixture(params=[
        (Setup.AWAITING_COACH_SELECTION, Setup.AWAITING_COACH_SELECTION, "grateful"),
        (Setup.AWAITING_COACH_SELECTION, Menu.START, "continue"),
        (Setup.AWAITING_COACH_SELECTION, Setup.AWAITING_COACH_SELECTION, "notacoach")
    ])
    def coach_query(self, request):
        """Return custom updates for testing state transition and message handling.

        Parameters:
            Integer: Incoming state
            Integer: Expected outgoing state
            String:  Message to pass
            Boolean: Whether to send as inline query
        """
        rv = inline_query(data=request.param[2])
        rv.states = request.param[:2]
        return rv

    def test_handle_inline(self, bot, coach_query, test_db, updater):
        """Test setup handler."""
        query = coach_query.callback_query
        with test_database(test_db, [User], fail_silently=True):
            with db.transaction():
                user, created = User.get_or_create(
                    telegram_id=query.message.from_user.id,
                    name='Pepe',
                    chat_id=query.message.from_user.id)
                user.state = coach_query.states[0]
                user.save()

            coach = Setup(bot, test_db, query.message.from_user, updater.job_queue)
            messages = coach.handle(coach_query)

            user = User.get(User.telegram_id == user.telegram_id)

            assert len(messages) > 0
            assert user.state == coach_query.states[1]


class TestGratitude:
    """Tests for the gratitude coach."""

    @pytest.fixture(params=range(4))
    def gratitudes(self, request, user):
        """Return gratitude records."""
        rv = []
        for i in range(request.param):
            rv.append(user.create_record(Gratitude.NAME,
                "Record {}".format(i),
                "Reaction {}".format(i)
            ))
        return rv

    def test_init(self, gratitudes, bot, tguser, test_db, updater):
        """Test that current gratitudes are collected in init."""
        with test_database(test_db, [User, Record], fail_silently=True):
            for g in gratitudes:
                g.save()
            gc = Gratitude(bot, db, tguser, updater.job_queue)

            assert len(gc.collector) == len(gratitudes)

    def test_setup(self, user, bot, test_db, tguser, updater):
        """Test the setup method."""
        with test_database(test_db, [User, Record, Job], fail_silently=True):
            sc = Setup(bot, test_db, tguser, updater.job_queue)
            Gratitude.setup(sc)

            assert not updater.job_queue.queue.empty()

    @pytest.fixture(params=[Gratitude.AWAITING_GRATITUDE, Gratitude.AWAITING_REASONS])
    def gratitude_states(self, request, gratitudes):
        """Return a set of gratitudes for each of the handler states."""
        return (request.param, gratitudes)

    def test_handle(self, bot, test_db, tguser, updater, update, gratitude_states):
        """Test the handle that collects records from the user."""
        with test_database(test_db, [User, Record, Job], fail_silently=True):
            user, created = User.tg_get_or_create(tguser)
            user.active_coach = Gratitude.NAME
            user.state = gratitude_states[0]

            if user.state == Gratitude.AWAITING_REASONS:
                # If no gratitude exists, no reaction can be recorded
                if len(gratitude_states[1]) == 0:
                    return

                # Last gratitude must always miss the reaction in 2nd state
                gratitude_states[1][-1].reaction = None

            with test_db.transaction():
                for g in gratitude_states[1]:
                    g.save()
                user.save()

            g = Gratitude(bot, test_db, tguser, updater.job_queue)
            g.handle(update)

            # Reload from disk
            g = Gratitude(bot, test_db, tguser, updater.job_queue)
            user = User.get(User.id == g.user.id)

            if user.state == Gratitude.AWAITING_GRATITUDE:
                if len(gratitude_states[1]) < 3:
                    assert len(g.collector) == len(gratitude_states[1]) + 1
            # else:
            #     assert g.collector[-1].reaction is not None

            # elif gratitude_states[0] == Gratitude.AWAITING_GRATITUDE and len(g.collector) == 3:
            #     assert user.state == Gratitude.AWAITING_REASONS

            # elif gratitude_states[0] == Gratitude.AWAITING_REASONS and len(g.collector) == 3:
            #     assert user.state == Menu.START
            #     assert user.active_coach == Menu.NAME
