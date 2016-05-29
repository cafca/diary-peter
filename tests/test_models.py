#!/usr/bin/env python

"""Tests for Diary Peter models."""

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
