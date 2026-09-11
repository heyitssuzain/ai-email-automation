from datetime import datetime, timezone

from app.database.database import SessionLocal
from app.database.models import ReplyDraft

def get_due_follow_ups():
    db = SessionLocal()

    try:
        now = datetime.now(timezone.utc)

        drafts = (
            db.query(ReplyDraft)
            .filter(
                ReplyDraft.status == "sent",
                ReplyDraft.follow_up_status == "pending",
                ReplyDraft.follow_up_at.is_not(None),
                ReplyDraft.follow_up_at <= now,
            )
            .order_by(
                ReplyDraft.follow_up_at.asc()
            )
            .all()
        )

        print("=" * 70)
        print("DUE FOLLOW-UPS")
        print("=" * 70)
        print(
            f"Due follow-ups found: {len(drafts)}"
        )
        print("=" * 70)

        for draft in drafts:
            print(
                f"Draft ID : {draft.id}\n"
                f"Email ID : {draft.email_id}\n"
                f"Due at   : {draft.follow_up_at}\n"
                f"Status   : {draft.follow_up_status}"
            )
            print("-" * 70)

        return drafts

    finally:
        db.close()


def mark_follow_up_required(draft_id: int):
    db = SessionLocal()

    try:
        draft = (
            db.query(ReplyDraft)
            .filter(
                ReplyDraft.id == draft_id
            )
            .first()
        )

        if not draft:
            raise ValueError(
                f"Reply draft {draft_id} not found."
            )

        if draft.status != "sent":
            raise ValueError(
                f"Draft {draft_id} is not in sent status."
            )

        if draft.follow_up_status != "due":
            raise ValueError(
                f"Draft {draft_id} is not marked as due."
            )

        draft.follow_up_status = "follow_up_required"

        db.commit()
        db.refresh(draft)

        print(
            "=" * 70
        )
        print(
            "FOLLOW-UP REQUIRED"
        )
        print(
            "=" * 70
        )
        print(
            f"Draft ID : {draft.id}"
        )
        print(
            f"Email ID : {draft.email_id}"
        )
        print(
            f"Status   : {draft.follow_up_status}"
        )
        print(
            "=" * 70
        )

        return draft

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    get_due_follow_ups()
