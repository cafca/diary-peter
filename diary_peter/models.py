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

    # Which module is currently active in the user's chat session?
    state_module = pw.CharField(default="setup")

    # In which state is this module?
    state = pw.IntegerField(default=0)

    # What is the time at which the user usually wakes up?
    wake_time = pw.TimeField(default=lambda: datetime.time(hour=9))

    # What is the time at which the user wants to be asked for their daily diary?
    diary_time = pw.TimeField(default=lambda: datetime.time(hour=22))

    class Meta:
        """Metadata for user model."""

        database = db

    @classmethod
    def get_or_create(cls, user):
        """Return the user record for username or return a new record."""
        try:
            record = cls.select().where(cls.username == user.username).get()
        except:
            record = User(
                id=uuid4().hex,
                first_name=user.first_name,
                last_name=user.last_name,
                username=user.username,
            )
        return record

    def create_record(self, kind, reaction, content):
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
