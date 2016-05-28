#!/usr/bin/env python
"""Test fixtures and utilities."""

import os
import pytest
import telegram

from peewee import SqliteDatabase
from random import randint

from diary_peter.models import User

user_data = {
    'id': 4325497,
    'first_name': "Finz",
    'last_name': "Nilly",
    'username': "ululu",
    'type': "private"
}


@pytest.fixture(scope="module")
def test_db():
    """Provide an in-memory database for testing."""
    return SqliteDatabase(':memory:')


@pytest.fixture
def bot():
    """Fixture that returns a Telegram for Python bot object."""
    return telegram.Bot(os.environ.get('TG_TOKEN', None))


@pytest.fixture
def tguser():
    """Fixture that returns a Telegram user object."""
    return telegram.User.de_json(user_data)


@pytest.fixture
def update():
    """Return a Telegram update object."""
    return custom_update()


def custom_update(msg="Lol I just ate a whole tuna."):
    """Return a custom update."""
    json = {
        'message_id': randint(40000, 50000),
        'from': user_data,
        'chat': user_data,
        'date': 1464350198,
        'text': msg
    }

    rv = telegram.Update.de_json({
        'update_id': randint(100000000, 200000000),
        'message': json
    })
    return rv


def create_users(num=10):
    """Utility func for creating users."""
    rv = []
    for i in range(num):
        rv.append(User.create(
            telegram_id=100 + i,
            name="User-{}".format(i),
            chat_id="Chat-{}".format(i)
        ))
    return rv
