#!/usr/bin/env python
"""They took our Jerbs."""

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
        if scheduled < datetime.now():
            scheduled = scheduled + timedelta(days=1)
        scheduled_remaining = scheduled - datetime.now() - timedelta(hours=6)

        job_queue.put(jobfunc, interval,
            next_t=scheduled_remaining.seconds)
        logger.info(job)
    logger.info("All jobs restored")


def generic_job(bot, id):
    """Generic bot that initiates a coach."""
    with db.transaction():
        job = Job.get(id=id)
        job.user.state = job.state
        job.user.active_coach = job.coach
        job.user.save()
        bot.sendMessage(job.user.telegram_id, text=job.text)
