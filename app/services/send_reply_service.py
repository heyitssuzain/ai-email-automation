from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone

from app.database.database import SessionLocal
from app.database.models import Email, ReplyDraft
from app.gmail.send_email import send_email


# ============================================================
# LOGGER
# ============================================================

logger = logging.getLogger(__name__)


# ============================================================
# SEND APPROVED REPLY
# ============================================================

def send_approved_reply(
    draft_id: int,
):
    """
    Send an approved reply draft safely.

    Safety rules:
        1. Draft must exist.
        2. Draft must be 'approved'.
        3. Already-sent drafts cannot be sent again.
        4. Original email must exist.
        5. Database is updated only after Gmail confirms send.
        6. Sending failures are logged with traceback.
    """

    db = SessionLocal()

    try:

        # ====================================================
        # LOAD DRAFT
        # ====================================================

        draft = (
            db.query(ReplyDraft)
            .filter(
                ReplyDraft.id == draft_id
            )
            .first()
        )

        if not draft:

            logger.warning(
                "Reply draft not found | "
                "draft_id=%s",
                draft_id,
            )

            raise ValueError(
                f"Reply draft {draft_id} not found."
            )

        logger.info(
            "Preparing approved reply | "
            "draft_id=%s | "
            "email_id=%s | "
            "status=%s",
            draft.id,
            draft.email_id,
            draft.status,
        )

        # ====================================================
        # DUPLICATE SEND PROTECTION
        # ====================================================

        if draft.status == "sent":

            logger.warning(
                "Duplicate send prevented | "
                "draft_id=%s | "
                "email_id=%s",
                draft.id,
                draft.email_id,
            )

            raise ValueError(
                f"Draft {draft_id} has already been sent. "
                "Duplicate sending is blocked."
            )

        # ====================================================
        # APPROVAL SAFETY GUARD
        # ====================================================

        if draft.status != "approved":

            logger.warning(
                "Unauthorized send attempt blocked | "
                "draft_id=%s | "
                "status=%s",
                draft.id,
                draft.status,
            )

            raise ValueError(
                f"Draft {draft_id} cannot be sent because "
                f"its status is '{draft.status}'. "
                "Only 'approved' drafts can be sent."
            )

        # ====================================================
        # LOAD ORIGINAL EMAIL
        # ====================================================

        email = (
            db.query(Email)
            .filter(
                Email.id == draft.email_id
            )
            .first()
        )

        if not email:

            logger.error(
                "Original email not found | "
                "draft_id=%s | "
                "email_id=%s",
                draft.id,
                draft.email_id,
            )

            raise ValueError(
                f"Original email "
                f"{draft.email_id} not found."
            )

        # ====================================================
        # FINAL SEND SAFETY CHECK
        # ====================================================

        if not draft.draft_text.strip():

            logger.warning(
                "Empty reply blocked | "
                "draft_id=%s",
                draft.id,
            )

            raise ValueError(
                f"Draft {draft_id} contains an empty reply."
            )

        # ====================================================
        # SEND THROUGH GMAIL
        # ====================================================

        logger.info(
            "Sending approved reply through Gmail | "
            "draft_id=%s | "
            "email_id=%s | "
            "recipient=%s",
            draft.id,
            email.id,
            email.sender,
        )

        sent_message = send_email(
            recipient=email.sender,
            subject=f"Re: {email.subject}",
            body=draft.draft_text,
            thread_id=None,
        )

        # ====================================================
        # VERIFY GMAIL RESPONSE
        # ====================================================

        gmail_message_id = (
            sent_message.get("id")
            if sent_message
            else None
        )

        if not gmail_message_id:

            logger.error(
                "Gmail send returned no message ID | "
                "draft_id=%s | "
                "email_id=%s",
                draft.id,
                email.id,
            )

            raise RuntimeError(
                "Gmail send did not return a message ID."
            )

        # ====================================================
        # UPDATE DATABASE AFTER SUCCESSFUL SEND
        # ====================================================

        sent_at = datetime.now(
            timezone.utc
        )

        draft.status = "sent"

        draft.sent_at = sent_at

        # Schedule follow-up for 3 days later.
        draft.follow_up_at = (
            sent_at
            + timedelta(days=3)
        )

        draft.follow_up_status = "pending"

        email.status = "replied"

        db.commit()

        db.refresh(draft)

        # ====================================================
        # SUCCESS LOG
        # ====================================================

        logger.info(
            "Reply sent successfully | "
            "draft_id=%s | "
            "email_id=%s | "
            "recipient=%s | "
            "gmail_message_id=%s",
            draft.id,
            email.id,
            email.sender,
            gmail_message_id,
        )

        # ====================================================
        # CONSOLE OUTPUT
        # ====================================================

        print("=" * 70)
        print("REPLY SENT SUCCESSFULLY")
        print("=" * 70)

        print(
            "Draft ID :",
            draft.id,
        )

        print(
            "Email ID :",
            email.id,
        )

        print(
            "Recipient:",
            email.sender,
        )

        print(
            "Status   :",
            draft.status,
        )

        print(
            "Sent at  :",
            draft.sent_at,
        )

        print(
            "Gmail ID :",
            gmail_message_id,
        )

        print("=" * 70)

        return draft

    except Exception:

        # ====================================================
        # DATABASE ROLLBACK
        # ====================================================

        db.rollback()

        logger.exception(
            "Reply sending failed | "
            "draft_id=%s",
            draft_id,
        )

        raise

    finally:

        db.close()

        logger.info(
            "Reply sending database session closed | "
            "draft_id=%s",
            draft_id,
        )