#!/usr/bin/env python

"""Tests for Diary Peter models."""

from playhouse.test_utils import test_database
from telegram.emoji import Emoji

from diary_peter.models import User, Record

from conftest import create_users


class TestUser():
    """Tests for the user model."""

    def test_gen(self, test_db):
        """Test creating users and retrieving them from the db."""
        with test_database(test_db, [User], fail_silently=True):
            users = create_users(test_db)
            for u in users:
                u.save()

            user = User.get(User.id == users[0].id)
            assert isinstance(user, User)
            assert user == users[0]

    def test_get_or_create(self, test_db, tguser):
        """Test get_or_create shortcut."""
        with test_database(test_db, [User], fail_silently=True):
            user, created = User.tg_get_or_create(tguser)
            user.save()

            assert isinstance(user, User)

            user1 = User.get(User.id == user.id)
            assert user1 == user


class TestRecords():
    """Tests for the Record model."""

    def test_gen(self, test_db):
        """Test creating of records."""
        with test_database(test_db, [User, Record], fail_silently=True):
            user = create_users(test_db, 1)[0]
            records = []
            for i in range(10):
                records.append(
                    user.create_record("diary", Emoji.HOT_BEVERAGE,
                    "Wow, I had {} coffee today.".format(i))
                )

            assert len(records) == 10
            assert isinstance(records[0], Record)
            assert records[0].user == user
