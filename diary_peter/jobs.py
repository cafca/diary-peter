#!/usr/bin/env python
"""They took our Jerbs."""

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

import logging

from datetime import datetime, timedelta
from diary_peter.models import db, Job

logger = logging.getLogger(__name__)


def restore_jobs(job_queue):
    """Load and queue jobs from database."""
    for job in Job.select():
        jobfunc = lambda bot: generic_job(bot, job.id)
        interval = 24 * 60 * 60

        scheduled = datetime.combine(datetime.today(), job.scheduled_at)
        scheduled_remaining = scheduled - datetime.now() - timedelta(hours=6)
        if scheduled_remaining < timedelta(seconds=0):
            scheduled_remaining = scheduled_remaining + timedelta(days=1)

        job_queue.put(jobfunc, interval,
            next_t=scheduled_remaining.seconds)
        logger.info("{} - {} remaining".format(job, scheduled_remaining))
    logger.info("All jobs restored")


def generic_job(bot, id):
    """Generic bot that initiates a coach."""
    with db.transaction():
        job = Job.get(id=id)
        job.user.state = job.state
        job.user.active_coach = job.coach
        job.user.save()
        bot.sendMessage(job.user.telegram_id, text=job.text)
