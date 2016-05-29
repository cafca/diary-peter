#!/usr/bin/env python

"""models.py: Provides database models for diary-pete, mapped by peewee."""

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

import os
import datetime
import peewee as pw

# from playhouse.pool import PooledSqliteDatabase


if os.environ.get("PG_PASS", False):
    db = pw.PostgresqlDatabase(
        'peter',  # Required by Peewee.
        user='peter',  # Will be passed directly to psycopg2.
        password=os.environ.get("PG_PASS", False),  # Ditto.
        host='localhost',  # Ditto.
    )
else:
    db = pw.SqliteDatabase('test.db')


class User(pw.Model):
    """Model a Telegram user."""

    telegram_id = pw.IntegerField(unique=True)
    name = pw.CharField(null=True)
    active = pw.BooleanField(default=True)

    # Did the user complete the intro script
    intro_seen = pw.BooleanField(default=False)

    # Does the user want to be asked for their mood?
    ask_mood = pw.BooleanField(default=True)

    # Does the user want to be asked to record good things?
    ask_good_things = pw.BooleanField(default=True)

    # Does the user want to be asked to complete a regular diary?
    ask_diary = pw.BooleanField(default=True)

    # --- State machine data
    # Current chat id with which the user is participating
    chat_id = pw.CharField(unique=True)

    # Which coach is currently active in the user's chat session?
    active_coach = pw.CharField(default="Setup")

    # In which state is this module?
    state = pw.IntegerField(default=0)

    # What is the time at which the user usually wakes up?
    wake_time = pw.TimeField(default=lambda: datetime.time(hour=9))

    class Meta:
        """Metadata for user model."""

        database = db

    @staticmethod
    def tg_get_or_create(tguser):
        """Get or create based on a Telegram user object."""
        return User.get_or_create(
            telegram_id=tguser.id,
            chat_id=tguser.id
        )

    def create_record(self, kind, content, reaction=None):
        """Return a new record in this user's diary."""
        with db.transaction():
            rv = Record(
                kind=kind,
                user=self,
                reaction=reaction,
                content=content
            )
        return rv


class Record(pw.Model):
    """Model a single record in a user's diary."""

    kind = pw.CharField()
    user = pw.ForeignKeyField(User, related_name="records")
    created = pw.DateTimeField(default=datetime.datetime.now)
    reaction = pw.CharField(null=True)
    content = pw.CharField()

    def __repr__(self):
        """Return readable representation."""
        return "{} #{} of User-{} ({})".format(
            self.kind,
            self.id,
            self.user.id,
            self.created.strftime("%B %d, %Y"))

    class Meta:
        """Metadata for record model."""

        database = db
        order_by = ('created',)


class Job(pw.Model):
    """Coach setup for a user."""

    user = pw.ForeignKeyField(User, related_name="goals")
    coach = pw.CharField()
    state = pw.IntegerField(default=0)
    scheduled_at = pw.TimeField(default=lambda: datetime.time(hour=22))
    text = pw.CharField()

    def __repr__(self):
        """Readable representation."""
        return "{} job of user {} scheduled at {}".format(
            self.coach, self.user.id, self.scheduled_at)

    class Meta:
        """Metadata for goal model."""

        database = db

        # Create a unique index
        indexes = (
            (('user', 'coach', 'state'), True),
        )
