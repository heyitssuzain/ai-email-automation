from datetime import datetime, timezone

from app.database.database import SessionLocal
from app.database.models import Email, ReplyDraft
from app.gmail.client import get_gmail_service


def customer_replied(draft_id: int) -> bool:
    db = SessionLocal()

    try:
        draft = (
            db.query(ReplyDraft)
            .filter(ReplyDraft.id == draft_id)
            .first()
        )

        if not draft:
            raise ValueError(f"Reply draft {draft_id} not found.")

        if draft.status != "sent":
            return False

        original_email = (
            db.query(Email)
            .filter(Email.id == draft.email_id)
            .first()
        )

        if not original_email:
            raise ValueError(
                f"Original email {draft.email_id} not found."
            )

        service = get_gmail_service()

        sender = original_email.sender

        sent_at = draft.sent_at

        if sent_at is None:
            return False

        sent_timestamp = int(
            sent_at.timestamp()
        )

        query = (
            f"from:{sender} "
            f"after:{sent_timestamp}"
        )

        response = (
            service.users()
            .messages()
            .list(
                userId="me",
                q=query,
            )
            .execute()
        )

        messages = response.get("messages", [])

        return len(messages) > 0

    finally:
        db.close()


def check_customer_reply(draft_id: int):
    db = SessionLocal()

    try:
        draft = (
            db.query(ReplyDraft)
            .filter(ReplyDraft.id == draft_id)
            .first()
        )

        if not draft:
            raise ValueError(
                f"Reply draft {draft_id} not found."
            )

        replied = customer_replied(draft_id)

        if replied:
            draft.follow_up_status = "replied"

            print(
                f"[CUSTOMER REPLIED] Draft ID: {draft.id}"
            )

        else:
            draft.follow_up_status = "due"

            print(
                f"[FOLLOW-UP REQUIRED] Draft ID: {draft.id}"
            )

        db.commit()

        return replied

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    check_customer_reply(2)