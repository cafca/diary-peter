#!/usr/bin/env python
"""Tests for the bot's dispatchers."""

from diary_peter.dispatchers import start


class TestConfig:
    """Test configuration dispatchers."""

    def test_start(self, bot, update):
        """Test initial setup."""
        messages = start(bot, update)

        assert len(messages) > 0
