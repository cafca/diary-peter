#!/usr/bin/env/python

"""Initial database setup. Destructive!."""

import peewee

from logging import info, INFO, warning, basicConfig
from diary_peter.models import db, CoachSetup, Record, User

if __name__ == '__main__':
    basicConfig(format='%(levelname)s\t%(message)s', level=INFO)

    info("Creating database...")
    db.connect()
    try:
        db.create_tables([CoachSetup, Record, User])
    except peewee.OperationalError as e:
        warning("Oopsie.")
        warning(e)
    else:
        info("Done.")
