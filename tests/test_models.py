#!/usr/bin/env python

"""Tests for Diary Peter models."""

import os
import pytest
import telegram

from peewee import SqliteDatabase
from playhouse.test_utils import test_database
from telegram.emoji import Emoji

from diary_peter.models import User, Goal, Record

test_db = SqliteDatabase(':memory:')


@pytest.fixture
def bot():
    """Fixture that returns a Telegram for Python bot object."""
    return telegram.Bot(os.environ.get('TG_TOKEN', None))


@pytest.fixture
def tguser():
    """Fixture that returns a Telegram user object."""
    json = {
        'id': 12345678,
        'first_name': "Theodore",
        'last_name': "Phoenix",
        'username': "tphox",
        'type': "private"
    }
    return telegram.User.de_json(json)


def create_users(num=10):
    """Utility func for creating users."""
    rv = []
    for i in range(num):
        rv.append(User.create(
            id="UserID-{}".format(i),
            username="User-{}".format(i),
            first_name="Max",
            last_name="Schmatz",
            chat_id="Chat-{}".format(i)
        ))
    return rv


class TestUser():
    """Tests for the user model."""

    def test_gen(self):
        """Test creating users and retrieving them from the db."""
        with test_database(test_db, [User, Goal, Record]):
            create_users()

            user = User.get(User.username == "User-1")
        assert isinstance(user, User)

    def test_get_or_create(self, tguser):
        """Test get_or_create shortcut."""
        with test_database(test_db, [User, Goal, Record]):
            user = User.get_or_create(tguser)

        assert isinstance(user, User)


class TestRecords():
    """Tests for the Record model."""

    def test_gen(self):
        """Test creating of records."""
        with test_database(test_db, [User, Goal, Record]):
            user = create_users(1)[0]
            records = []
            for i in range(10):
                records.append(
                    user.create_record("diary", Emoji.HOT_BEVERAGE,
                    "Wow, I had {} coffee today.".format(i))
                )
        assert len(records) == 10
        assert isinstance(records[0], Record)
        assert records[0].user == user
