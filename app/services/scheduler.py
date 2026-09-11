import logging

from apscheduler.schedulers.blocking import BlockingScheduler

from app.services.email_pipeline import run_email_pipeline
from app.services.follow_up_service import (
    get_due_follow_ups,
    mark_follow_up_required,
)
from app.services.customer_reply_service import check_customer_reply


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger(__name__)


def scheduled_email_pipeline():
    logger.info(
        "Starting scheduled email pipeline..."
    )

    try:
        run_email_pipeline()

        logger.info(
            "Scheduled email pipeline finished successfully."
        )

    except Exception:
        logger.exception(
            "Scheduled email pipeline failed."
        )


def scheduled_follow_up_check():
    logger.info(
        "Checking for due follow-ups..."
    )

    try:
        due_follow_ups = get_due_follow_ups()

        logger.info(
            "Due follow-ups found: %d",
            len(due_follow_ups),
        )

        for draft in due_follow_ups:

            try:
                replied = check_customer_reply(
                    draft.id
                )

                if not replied:
                    mark_follow_up_required(
                        draft.id
                    )

            except Exception:
                logger.exception(
                    "Follow-up processing failed "
                    "for draft ID %s.",
                    draft.id,
                )

    except Exception:
        logger.exception(
            "Follow-up check failed."
        )


def main():
    scheduler = BlockingScheduler()

    # ---------------------------------------------------------
    # Main email automation pipeline
    # ---------------------------------------------------------

    scheduler.add_job(
        scheduled_email_pipeline,
        "interval",
        minutes=5,
        id="email_automation_pipeline",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )

    # ---------------------------------------------------------
    # Follow-up checker
    # ---------------------------------------------------------

    scheduler.add_job(
        scheduled_follow_up_check,
        "interval",
        minutes=5,
        id="follow_up_checker",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )

    logger.info(
        "AI Email Automation Scheduler started."
    )

    logger.info(
        "Email pipeline will run every 5 minutes."
    )

    logger.info(
        "Follow-up checker will run every 5 minutes."
    )

    logger.info(
        "Automatic sending is NOT enabled."
    )

    # ---------------------------------------------------------
    # Run both jobs once immediately
    # ---------------------------------------------------------

    scheduled_email_pipeline()

    scheduled_follow_up_check()

    # ---------------------------------------------------------
    # Start scheduler
    # ---------------------------------------------------------

    try:
        scheduler.start()

    except (KeyboardInterrupt, SystemExit):
        logger.info(
            "Scheduler stopped."
        )


if __name__ == "__main__":
    main()
