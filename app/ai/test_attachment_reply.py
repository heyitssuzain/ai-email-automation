from app.database.database import SessionLocal
from app.database.models import Email, Attachment


def main():
    db = SessionLocal()

    try:
        email = Email(
            provider_message_id="TEST_ATTACHMENT_REPLY_001",
            thread_id="TEST_ATTACHMENT_REPLY_THREAD_001",
            sender="billing@example.com",
            recipient="you@example.com",
            subject="Invoice Verification Request",
            body=(
                "Hello,\n\n"
                "Please review the attached document and "
                "confirm whether you received it.\n\n"
                "Thanks."
            ),
            category="Invoice",
            priority="MEDIUM",
            intent="Confirm receipt of the attached document.",
            summary=(
                "The sender wants confirmation that "
                "the attached document was received."
            ),
            requires_reply=True,
            status="received",
        )

        db.add(email)
        db.flush()

        source_attachment = (
            db.query(Attachment)
            .filter(Attachment.email_id == 14)
            .first()
        )

        if not source_attachment:
            raise ValueError(
                "Attachment from email ID 14 was not found."
            )

        test_attachment = Attachment(
            email_id=email.id,
            filename=source_attachment.filename,
            mime_type=source_attachment.mime_type,
            storage_path=source_attachment.storage_path,
            extracted_text=source_attachment.extracted_text,
        )

        db.add(test_attachment)
        db.commit()

        print()
        print("=" * 70)
        print("TEST REPLY EMAIL CREATED")
        print("=" * 70)
        print("Email ID:", email.id)
        print("Subject:", email.subject)
        print("Requires reply:", email.requires_reply)
        print("Attachment:", test_attachment.filename)
        print(
            "Attachment text:",
            len(test_attachment.extracted_text or ""),
            "characters",
        )
        print("=" * 70)

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()