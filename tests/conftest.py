#!/usr/bin/env python
"""Test fixtures and utilities."""

import os
import pytest
import telegram

from peewee import SqliteDatabase
from random import randint
from telegram.ext import Updater

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
def updater(request, scope="module"):
    """Fixture that returns a Telegram Bot updater object."""
    updater = Updater(os.environ.get("TG_TOKEN", False))

    def stop_updater():
        updater.stop()
    request.addfinalizer(stop_updater)

    return updater


@pytest.fixture
def tguser():
    """Fixture that returns a Telegram user object."""
    return telegram.User.de_json(user_data)


@pytest.fixture
def update():
    """Return a Telegram update object."""
    return custom_update()


@pytest.fixture
def user():
    """Return a single user object."""
    return create_users(num=1)[0]


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


def inline_query(data):
    """Return a custom inline query."""
    iq = {
        'id': randint(40000, 50000),
        'from': user_data,
        'chat': user_data,
        'offset': 'a',
        'query': data
    }

    cq = {
        'id': randint(40000, 50000),
        'from': user_data,
        'message': {
            'message_id': randint(40000, 50000),
            'from': user_data,
            'chat': user_data,
            'date': 1464350198,
            'text': 'cq message text'
        },
        'data': data
    }

    rv = telegram.Update.de_json({
        'update_id': randint(100000000, 200000000),
        'inline_query': iq,
        'callback_query': cq
    })
    return rv


def create_users(num=10):
    """Utility func for creating users."""
    rv = []
    for i in range(num):
        rv.append(User.create_or_get(
            telegram_id=4325497 + i,
            name="User-{}".format(i),
            chat_id=4325497 + i
        )[0])
    return rv
