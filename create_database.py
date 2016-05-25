#!/usr/bin/env/python

"""Initial database setup. Destructive!."""

from diary_peter.models import db, Goal, Record, User

if __name__ == '__main__':
    print("Creating database...")
    db.connect()
    db.create_tables([Goal, Record, User])
    print("Done.")
