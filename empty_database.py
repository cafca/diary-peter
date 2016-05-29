#!/usr/bin/env/python

"""Initial database setup. Destructive!."""

import peewee

from logging import info, INFO, warning, basicConfig
from diary_peter.models import db, Job, Record, User

if __name__ == '__main__':
    basicConfig(format='%(levelname)s\t%(message)s', level=INFO)

    info("Deleting database...")
    db.connect()
    try:
        for m in [Job, Record, User]:
            m.drop_table()
    except peewee.OperationalError as e:
        warning("Oopsie.")
        warning(e)
    else:
        info("Done.")