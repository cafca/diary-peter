#!/usr/bin/env python
"""Tests for the bot's dispatchers."""

import pytest

from playhouse.test_utils import test_database

from conftest import custom_update
from diary_peter.dispatchers import start
from diary_peter.coaches import Config
from diary_peter.models import db, User


@pytest.fixture(params=[
    (Config.START, Config.AWAITING_WAKE_TIME, ""),
    (Config.AWAITING_WAKE_TIME, Config.AWAITING_SELECTION_CONFIRMATION, "9am"),
    (Config.AWAITING_WAKE_TIME, Config.AWAITING_WAKE_TIME, "Man, I don't know.")
])
def config_update(request):
    """Return three custom updates for testing the initial setup.

    Parameters:
        Integer: Incoming state
        Integer: Expected outgoing state
        String: Message to pass
    """
    rv = custom_update(msg=request.param[2])
    rv.states = request.param[:2]
    return rv


class TestConfig:
    """Test configuration dispatchers."""

    def test_start(self, bot, config_update, test_db):
        """Test initial setup."""
        with test_database(test_db, [User]):
            with db.transaction():
                user, created = User.tg_get_or_create(
                    config_update.message.from_user)
                user.state = config_update.states[0]
                user.save()

            messages = start(bot, config_update)

            user, created = User.tg_get_or_create(
                config_update.message.from_user)

            assert len(messages) > 0
            assert user.state == config_update.states[1]
