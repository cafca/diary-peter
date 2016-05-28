#!/usr/bin/env python
"""Tests for all coaches."""

import pytest
import telegram
import peewee

from playhouse.test_utils import test_database
from telegram.emoji import Emoji

from conftest import custom_update
from diary_peter.coaches import Setup, Coach, Menu
from diary_peter.models import db, User, Record


class TestBaseCoach:
    """Test base class."""

    def test_init(self, bot, tguser, test_db):
        """Test initialization of the base coach class."""
        with test_database(test_db, [User]):
            coach = Coach(bot, test_db, tguser)

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

    def test_handle(self, bot, menu_update, test_db, tguser):
        """Test display of main menu."""
        with test_database(test_db, [User, Record]):
            with db.transaction():
                user, created = User.tg_get_or_create(tguser)
                user.state = menu_update.states[0]
                user.save()

            coach = Menu(bot, db, tguser)
            msgs = coach.handle(menu_update)

            assert len(msgs) == 1

    def test_diary_entry(self, bot, test_db, tguser):
        """Test diary entry from main menu."""
        diary_entry = "My secret diary."

        with test_database(test_db, [User, Record]):
            with db.transaction():
                user, created = User.tg_get_or_create(tguser)
                user.state = Menu.AWAITING_DIARY_ENTRY
                user.save()

            coach = Menu(bot, db, tguser)
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
        (Setup.AWAITING_SELECTION_CONFIRMATION, Setup.AWAITING_COACH_SELECTION, Emoji.THUMBS_UP_SIGN),
        (Setup.AWAITING_SELECTION_CONFIRMATION, Menu.START, Emoji.THUMBS_DOWN_SIGN)
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

    def test_handle(self, bot, setup_update, test_db):
        """Test setup handler."""
        with test_database(test_db, [User]):
            with db.transaction():
                user, created = User.tg_get_or_create(
                    setup_update.message.from_user)
                user.state = setup_update.states[0]
                user.save()

            coach = Setup(bot, test_db, setup_update.message.from_user)
            messages = coach.handle(setup_update)

            user, created = User.tg_get_or_create(
                setup_update.message.from_user)

            assert len(messages) > 0
            assert user.state == setup_update.states[1]
