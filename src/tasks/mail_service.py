from celery_app import celery_app
from helpers.config import get_settings
from time import sleep
import logging
from datetime import datetime
import asyncio

logger = logging.getLogger("celery.task")

@celery_app.task(bind=True, name = "tasks.mail_service.send_email_report")
def send_email_report(self, mail_wait_seconds: int):

    #return await _send_email_report(self, mail_wait_seconds)
    return asyncio.run(_send_email_report(self, mail_wait_seconds))


async def _send_email_report(task_instance, mail_wait_seconds: int):

    started_at = str(datetime.now())
    task_instance.update_state(
        state= "PROGRESS",
        meta={
            "started_at": started_at
        }
    )
    # ===== START ====== send reports
    for i in range(15):
        logger.info(f"Send email to user: {i}")
        await asyncio.sleep(mail_wait_seconds)

    # ===== END ====== send reports

    return {
        "no_emails": 15,
        "end_at": str(datetime.now())
    }
