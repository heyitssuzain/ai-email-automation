from __future__ import annotations

import logging
from email.utils import parsedate_to_datetime

from sqlalchemy.exc import IntegrityError

from app.database.database import SessionLocal
from app.database.models import Email, Attachment
from app.gmail.attachments import download_attachment


# ============================================================
# LOGGER
# ============================================================

logger = logging.getLogger(__name__)


# ============================================================
# DATE PARSER
# ============================================================

def parse_received_date(
    date_string,
):
    """Convert a Gmail Date header into a datetime."""

    if not date_string:
        return None

    try:
        return parsedate_to_datetime(
            date_string
        )

    except (
        TypeError,
        ValueError,
        IndexError,
    ) as exc:

        logger.warning(
            "Could not parse Gmail date | "
            "date=%r | error=%s",
            date_string,
            exc,
        )

        return None


# ============================================================
# ATTACHMENT STORAGE
# ============================================================

def save_attachments(
    db,
    email,
    email_data,
):
    """
    Download and save attachments that are not already
    present for this email.

    Duplicate protection:
        filename is checked against existing attachments.
    """

    attachment_count = 0

    existing_attachments = {
        attachment.filename
        for attachment in email.attachments
    }

    for attachment_data in email_data.get(
        "attachments",
        [],
    ):

        filename = attachment_data.get(
            "filename",
            "",
        )

        attachment_id = attachment_data.get(
            "attachment_id"
        )

        if not filename or not attachment_id:

            logger.warning(
                "Skipping invalid attachment metadata | "
                "email_id=%s | filename=%r",
                email.id,
                filename,
            )

            continue

        # ----------------------------------------------------
        # DUPLICATE ATTACHMENT PROTECTION
        # ----------------------------------------------------

        if filename in existing_attachments:

            logger.info(
                "Duplicate attachment skipped | "
                "email_id=%s | filename=%r",
                email.id,
                filename,
            )

            continue

        # ----------------------------------------------------
        # DOWNLOAD ATTACHMENT
        # ----------------------------------------------------

        try:

            file_path = download_attachment(
                message_id=email.provider_message_id,
                attachment_id=attachment_id,
                filename=filename,
            )

            attachment = Attachment(
                email_id=email.id,
                filename=filename,
                mime_type=attachment_data.get(
                    "mime_type"
                ),
                storage_path=file_path,
            )

            db.add(attachment)

            existing_attachments.add(
                filename
            )

            attachment_count += 1

            logger.info(
                "Attachment saved | "
                "email_id=%s | filename=%r",
                email.id,
                filename,
            )

            print(
                f"[ATTACHMENT OK] "
                f"email_id={email.id} | "
                f"{filename}"
            )

        except Exception as exc:

            logger.exception(
                "Attachment download failed | "
                "email_id=%s | filename=%r",
                email.id,
                filename,
            )

            print(
                f"[ATTACHMENT FAILED] "
                f"email_id={email.id} | "
                f"{filename} | "
                f"{exc}"
            )

    return attachment_count


# ============================================================
# EMAIL STORAGE
# ============================================================

def save_emails_to_database(
    emails,
):
    """
    Save fetched Gmail emails to the database.

    Duplicate protection:
        provider_message_id is checked before insertion.

    Database-level protection:
        provider_message_id has a UNIQUE constraint.

    Existing emails:
        - email record is skipped
        - attachments are checked

    Each batch uses one transaction.
    """

    db = SessionLocal()

    saved_count = 0
    skipped_count = 0
    attachment_count = 0

    try:

        # ====================================================
        # PROCESS FETCHED EMAILS
        # ====================================================

        for email_data in emails:

            message_id = email_data.get(
                "message_id"
            )

            # ------------------------------------------------
            # VALIDATE MESSAGE ID
            # ------------------------------------------------

            if not message_id:

                logger.warning(
                    "Skipping email without "
                    "provider message ID."
                )

                continue

            # ------------------------------------------------
            # CHECK FOR EXISTING EMAIL
            # ------------------------------------------------

            existing_email = (
                db.query(Email)
                .filter(
                    Email.provider_message_id
                    == message_id
                )
                .first()
            )

            if existing_email:

                skipped_count += 1

                logger.info(
                    "Duplicate email skipped | "
                    "message_id=%s | "
                    "email_id=%s",
                    message_id,
                    existing_email.id,
                )

                # Existing email may have attachments
                # that were not downloaded previously.
                attachment_count += (
                    save_attachments(
                        db=db,
                        email=existing_email,
                        email_data=email_data,
                    )
                )

                continue

            # ------------------------------------------------
            # CREATE NEW EMAIL
            # ------------------------------------------------

            received_at = parse_received_date(
                email_data.get("date")
            )

            new_email = Email(
                provider_message_id=message_id,
                thread_id=email_data.get(
                    "thread_id"
                ),
                sender=email_data.get(
                    "sender",
                    "",
                ),
                recipient=email_data.get(
                    "recipient",
                    "",
                ),
                subject=email_data.get(
                    "subject",
                    "",
                ),
                body=email_data.get(
                    "body",
                    "",
                ),
                received_at=received_at,
                status="received",
            )

            db.add(new_email)

            # Flush so SQLAlchemy obtains
            # the new email ID before attachments.
            db.flush()

            logger.info(
                "New email inserted | "
                "email_id=%s | "
                "message_id=%s | "
                "subject=%r",
                new_email.id,
                message_id,
                new_email.subject,
            )

            # ------------------------------------------------
            # SAVE ATTACHMENTS
            # ------------------------------------------------

            attachment_count += (
                save_attachments(
                    db=db,
                    email=new_email,
                    email_data=email_data,
                )
            )

            saved_count += 1

        # ====================================================
        # COMMIT BATCH
        # ====================================================

        db.commit()

        logger.info(
            "Email storage batch committed | "
            "new=%s | duplicates=%s | "
            "attachments=%s",
            saved_count,
            skipped_count,
            attachment_count,
        )

    except IntegrityError:

        # ====================================================
        # DATABASE DUPLICATE / CONSTRAINT PROTECTION
        # ====================================================

        db.rollback()

        logger.exception(
            "Database integrity error while "
            "saving Gmail emails."
        )

        raise

    except Exception:

        # ====================================================
        # UNEXPECTED ERROR
        # ====================================================

        db.rollback()

        logger.exception(
            "Unexpected error while "
            "saving Gmail emails."
        )

        raise

    finally:

        db.close()

        logger.info(
            "Email storage database session closed."
        )

    # ========================================================
    # FINAL REPORT
    # ========================================================

    print()

    print("=" * 70)
    print("EMAIL STORAGE RESULT")
    print("=" * 70)

    print(
        f"New emails saved : "
        f"{saved_count}"
    )

    print(
        f"Duplicates       : "
        f"{skipped_count}"
    )

    print(
        f"Attachments saved: "
        f"{attachment_count}"
    )

    print("=" * 70)

    return (
        saved_count,
        skipped_count,
    )