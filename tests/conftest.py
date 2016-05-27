#!/usr/bin/env python
"""Test fixtures and utilities."""

import os
import pytest
import telegram

from peewee import SqliteDatabase
from random import randint

from diary_peter.models import User


@pytest.fixture
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
    json = {
        'id': 12345678,
        'first_name': "Theodore",
        'last_name': "Phoenix",
        'username': "tphox",
        'type': "private"
    }
    return telegram.User.de_json(json)


@pytest.fixture
def update():
    """Return a Telegram update object."""
    json = {
        'message_id': randint(40000, 50000),
        'from': {
            'id': 4325497,
            'first_name': "Finz",
            'last_name': "Nilly",
            'username': "ululu",
            'type': "private"
        },
        'chat': {
            'id': 4325497,
            'first_name': "Finz",
            'last_name': "Nilly",
            'username': "ululu",
            'type': "private"
        },
        'date': 1464350198,
        'text': "Lol I just ate a whole tuna."
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
            id="UserID-{}".format(i),
            username="User-{}".format(i),
            first_name="Max",
            last_name="Schmatz",
            chat_id="Chat-{}".format(i)
        ))
    return rv
