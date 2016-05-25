#!/usr/bin/env python

"""models.py: Provides database models for diary-pete, mapped by peewee."""

import datetime
import peewee as pw

from uuid import uuid4
# from playhouse.pool import PooledSqliteDatabase


db = pw.SqliteDatabase('test.db')


class User(pw.Model):
    """Model a Telegram user."""

    id = pw.CharField(primary_key=True, unique=True)
    first_name = pw.CharField()
    last_name = pw.CharField()
    username = pw.CharField()
    active = pw.BooleanField(default=True)

    intro_seen = pw.BooleanField(default=False)
    ask_mood = pw.BooleanField(default=True)
    ask_good_things = pw.BooleanField(default=True)
    ask_diary = pw.BooleanField(default=True)

    chat_id = pw.CharField(unique=True)
    state_module = pw.CharField(default="setup")
    state = pw.IntegerField(default=0)

    wake_time = pw.TimeField(default=lambda: datetime.time(hour=9))
    diary_time = pw.TimeField(default=lambda: datetime.time(hour=22))

    class Meta:
        """Metadata for user model."""

        database = db

    @classmethod
    def get_or_create(cls, user):
        """Return the user record for username or return a new record."""
        record = cls.select().where(cls.username == user.username).get()
        if record is None:
            record = User(
                id=uuid4().hex,
                first_name=user.first_name,
                last_name=user.last_name,
                username=user.username,
            )
        return record


class Record(pw.Model):
    """Model a single record in a user's diary."""

    id = pw.UUIDField(default=uuid4, primary_key=True, unique=True)
    kind = pw.CharField()
    user = pw.ForeignKeyField(User, related_name="records")
    created = pw.DateTimeField(default=datetime.datetime.now)
    reaction = pw.CharField()
    content = pw.CharField()

    class Meta:
        """Metadata for record model."""

        database = db


class Goal(pw.Model):
    """Model goals set by a user."""

    id = pw.UUIDField(default=uuid4, primary_key=True, unique=True)
    user = pw.ForeignKeyField(User, related_name="goals")
    name = pw.CharField()
    reminder_interval = pw.IntegerField(default=(24 * 60 * 60))
    reminder_start = pw.DateTimeField()
    record_count = pw.IntegerField(default=0)

    class Meta:
        """Metadata for goal model."""

        database = db
