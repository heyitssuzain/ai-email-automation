from __future__ import annotations

import logging
import time
from datetime import datetime, timedelta, timezone

from app.ai.analyzer import analyze_email
from app.database.database import SessionLocal
from app.database.models import Email, Attachment


# ============================================================
# LOGGER
# ============================================================

logger = logging.getLogger(__name__)


# ============================================================
# GEMINI FREE-TIER SAFETY SETTINGS
# ============================================================

# Space requests so we don't aggressively hit rate limits.
REQUEST_SPACING_SECONDS = 30

# Maximum retries for transient Gemini errors.
MAX_RETRIES = 4

# Exponential backoff configuration.
BASE_BACKOFF_SECONDS = 30
BACKOFF_MULTIPLIER = 2
MAX_BACKOFF_SECONDS = 180


# ============================================================
# TRANSIENT ERROR DETECTION
# ============================================================

def _is_transient_gemini_error(
    exc: Exception,
) -> bool:
    """
    Determine whether a Gemini error is temporary
    and therefore safe to retry.

    Retryable:
        429
        500
        502
        503
        504

    Also detects common textual versions of these
    transient errors.
    """

    code = getattr(exc, "code", None)

    if code in (
        429,
        500,
        502,
        503,
        504,
    ):
        return True

    message = str(exc).lower()

    transient_errors = (
        "429",
        "resource_exhausted",
        "deadline_exceeded",
        "deadline expired",
        "gateway timeout",
        "service unavailable",
        "temporarily unavailable",
    )

    return any(
        error in message
        for error in transient_errors
    )


# ============================================================
# GEMINI ANALYSIS WITH RETRY
# ============================================================

def analyze_email_with_retry(
    email: Email,
    db,
):
    """
    Analyze one email with Gemini.

    Features:
        - Free-tier-friendly request spacing
        - Attachment-aware analysis
        - Exponential backoff
        - Bounded retries
        - Detailed logging
        - Exceptions are propagated to caller
    """

    attempt = 0
    backoff = BASE_BACKOFF_SECONDS

    while True:

        try:

            # ------------------------------------------------
            # REQUEST SPACING
            # ------------------------------------------------

            logger.info(
                "Preparing Gemini analysis | "
                "email_id=%s | attempt=%s",
                email.id,
                attempt + 1,
            )

            time.sleep(
                REQUEST_SPACING_SECONDS
            )

            # ------------------------------------------------
            # LOAD ATTACHMENTS
            # ------------------------------------------------

            attachments = (
                db.query(Attachment)
                .filter(
                    Attachment.email_id == email.id
                )
                .all()
            )

            logger.info(
                "Loaded attachments | "
                "email_id=%s | count=%s",
                email.id,
                len(attachments),
            )

            # ------------------------------------------------
            # COLLECT EXTRACTED ATTACHMENT TEXT
            # ------------------------------------------------

            attachment_text_parts = []

            for attachment in attachments:

                if attachment.extracted_text:

                    attachment_text_parts.append(
                        f"Attachment: "
                        f"{attachment.filename}\n"
                        f"{attachment.extracted_text}"
                    )

            attachment_text = "\n\n".join(
                attachment_text_parts
            )

            # ------------------------------------------------
            # SEND EMAIL TO GEMINI
            # ------------------------------------------------

            logger.info(
                "Sending email to Gemini | "
                "email_id=%s",
                email.id,
            )

            analysis = analyze_email(
                sender=email.sender,
                subject=email.subject,
                body=email.body,
                attachment_text=attachment_text,
            )

            logger.info(
                "Gemini analysis successful | "
                "email_id=%s | "
                "category=%s | "
                "priority=%s",
                email.id,
                analysis.category,
                analysis.priority,
            )

            return analysis

        except Exception as exc:

            # ------------------------------------------------
            # TRANSIENT ERROR
            # ------------------------------------------------

            if (
                _is_transient_gemini_error(exc)
                and attempt < MAX_RETRIES
            ):

                wait = min(
                    backoff,
                    MAX_BACKOFF_SECONDS,
                )

                logger.warning(
                    "Transient Gemini error | "
                    "email_id=%s | "
                    "retry=%s/%s | "
                    "wait=%ss | "
                    "error=%s",
                    email.id,
                    attempt + 1,
                    MAX_RETRIES,
                    wait,
                    exc,
                )

                print(
                    f"[RETRY] email id={email.id} | "
                    f"Retry {attempt + 1}/"
                    f"{MAX_RETRIES} in {wait}s"
                )

                time.sleep(wait)

                backoff *= BACKOFF_MULTIPLIER
                attempt += 1

                continue

            # ------------------------------------------------
            # RETRIES EXHAUSTED / NON-TRANSIENT ERROR
            # ------------------------------------------------

            logger.exception(
                "Gemini analysis failed | "
                "email_id=%s | "
                "attempts=%s | "
                "error=%s",
                email.id,
                attempt + 1,
                exc,
            )

            raise


# ============================================================
# ANALYZE UNPROCESSED EMAILS
# ============================================================

def analyze_unprocessed_emails(
    limit: int = 10,
) -> dict:
    """
    Analyze emails that have not been AI processed.

    Each email is processed independently.

    Success:
        - AI fields are saved.
        - Retry timestamp is cleared.

    Failure:
        - Failed transaction is rolled back.
        - Retry is scheduled.
        - Other emails continue processing.

    Returns:
        Summary dictionary.
    """

    db = SessionLocal()

    succeeded = 0
    failed = 0

    emails = []

    try:

        # ====================================================
        # FIND EMAILS READY FOR ANALYSIS
        # ====================================================

        now = datetime.now(
            timezone.utc
        )

        emails = (
            db.query(Email)
            .filter(
                Email.category.is_(None),
                (
                    Email.next_analysis_retry_at.is_(None)
                    | (
                        Email.next_analysis_retry_at
                        <= now
                    )
                ),
            )
            .limit(limit)
            .all()
        )

        logger.info(
            "AI analysis batch started | "
            "emails_found=%s | limit=%s",
            len(emails),
            limit,
        )

        print()
        print("=" * 70)
        print("AI EMAIL PROCESSING")
        print("=" * 70)
        print(
            f"Emails found for analysis: "
            f"{len(emails)}"
        )
        print("=" * 70)

        # ====================================================
        # PROCESS EACH EMAIL INDEPENDENTLY
        # ====================================================

        for email in emails:

            logger.info(
                "Starting email analysis | "
                "email_id=%s | subject=%r",
                email.id,
                email.subject,
            )

            try:

                # ------------------------------------------------
                # TRACK ANALYSIS ATTEMPT
                # ------------------------------------------------

                email.analysis_attempts += 1

                email.last_analysis_attempt_at = (
                    datetime.now(timezone.utc)
                )

                db.commit()

                logger.info(
                    "Analysis attempt recorded | "
                    "email_id=%s | attempt=%s",
                    email.id,
                    email.analysis_attempts,
                )

                # ------------------------------------------------
                # CALL GEMINI
                # ------------------------------------------------

                analysis = analyze_email_with_retry(
                    email,
                    db,
                )

                # ------------------------------------------------
                # SAVE AI ANALYSIS
                # ------------------------------------------------

                email.category = (
                    analysis.category
                )

                email.priority = (
                    analysis.priority
                )

                email.intent = (
                    analysis.intent
                )

                email.summary = (
                    analysis.summary
                )

                email.requires_reply = (
                    analysis.requires_reply
                )

                # Successful analysis means
                # no retry is currently required.
                email.next_analysis_retry_at = None

                db.commit()

                succeeded += 1

                logger.info(
                    "Email analysis saved successfully | "
                    "email_id=%s | "
                    "category=%s | "
                    "priority=%s | "
                    "requires_reply=%s",
                    email.id,
                    analysis.category,
                    analysis.priority,
                    analysis.requires_reply,
                )

                print(
                    f"[OK] id={email.id} | "
                    f"{analysis.category} | "
                    f"{analysis.priority} | "
                    f"{email.subject[:60]}"
                )

            except Exception as exc:

                # ------------------------------------------------
                # ROLLBACK FAILED TRANSACTION
                # ------------------------------------------------

                db.rollback()

                # ------------------------------------------------
                # CALCULATE RETRY DELAY
                # ------------------------------------------------

                retry_delay = min(
                    5
                    * (
                        2
                        ** (
                            email.analysis_attempts
                            - 1
                        )
                    ),
                    60,
                )

                # ------------------------------------------------
                # SCHEDULE NEXT RETRY
                # ------------------------------------------------

                email.next_analysis_retry_at = (
                    datetime.now(timezone.utc)
                    + timedelta(
                        minutes=retry_delay
                    )
                )

                db.commit()

                failed += 1

                # ------------------------------------------------
                # DETAILED ERROR LOG + TRACEBACK
                # ------------------------------------------------

                logger.exception(
                    "Email analysis failed | "
                    "email_id=%s | "
                    "subject=%r | "
                    "attempt=%s | "
                    "retry_in=%s_minutes",
                    email.id,
                    email.subject,
                    email.analysis_attempts,
                    retry_delay,
                )

                print(
                    f"[FAIL] id={email.id} | "
                    f"{email.subject[:60]} "
                    f"-> retry scheduled in "
                    f"{retry_delay} minutes"
                )

                # IMPORTANT:
                # Continue with the next email.
                continue

        # ====================================================
        # TOTAL ANALYZED COUNT
        # ====================================================

        total_analyzed = (
            db.query(Email)
            .filter(
                Email.category.is_not(None)
            )
            .count()
        )

        logger.info(
            "AI analysis batch completed | "
            "processed=%s | "
            "succeeded=%s | "
            "failed=%s | "
            "total_analyzed=%s",
            succeeded + failed,
            succeeded,
            failed,
            total_analyzed,
        )

    except Exception:

        # ====================================================
        # BATCH-LEVEL UNEXPECTED ERROR
        # ====================================================

        db.rollback()

        logger.exception(
            "Unexpected batch-level error "
            "during AI email analysis."
        )

        raise

    finally:

        db.close()

        logger.info(
            "AI analysis database session closed."
        )

    # ========================================================
    # FINAL REPORT
    # ========================================================

    print()
    print("-" * 70)

    print(
        f"Processed this run      : "
        f"{succeeded + failed}"
    )

    print(
        f"Successfully analyzed   : "
        f"{succeeded}"
    )

    print(
        f"Failed (retryable)      : "
        f"{failed}"
    )

    print(
        f"Skipped (this run)      : "
        f"0"
    )

    print(
        f"Total analyzed in DB    : "
        f"{total_analyzed}"
    )

    print("-" * 70)

    return {
        "found": len(emails),
        "succeeded": succeeded,
        "failed": failed,
        "skipped": 0,
        "total_analyzed_in_db": total_analyzed,
    }