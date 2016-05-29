#!/usr/bin/env/python

"""Initial database setup. Destructive!."""

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

import peewee

from logging import info, INFO, warning, basicConfig
from diary_peter.models import db, Job, Record, User

if __name__ == '__main__':
    basicConfig(format='%(levelname)s\t%(message)s', level=INFO)

    info("Creating database...")
    db.connect()
    try:
        db.create_tables([Job, Record, User])
    except peewee.OperationalError as e:
        warning("Oopsie.")
        warning(e)
    else:
        info("Done.")
