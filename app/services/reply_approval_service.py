from datetime import datetime, timezone

from app.database.database import SessionLocal
from app.database.models import ReplyDraft


def approve_reply_draft(draft_id: int):
    db = SessionLocal()

    try:
        draft = (
            db.query(ReplyDraft)
            .filter(ReplyDraft.id == draft_id)
            .first()
        )

        if not draft:
            raise ValueError(
                f"Reply draft with id={draft_id} was not found."
            )

        if draft.status != "pending":
            raise ValueError(
                f"Draft id={draft_id} cannot be approved "
                f"because its status is '{draft.status}'."
            )

        draft.status = "approved"
        draft.approved_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(draft)

        print()
        print("=" * 70)
        print("REPLY DRAFT APPROVED")
        print("=" * 70)
        print("Draft ID :", draft.id)
        print("Email ID :", draft.email_id)
        print("Status   :", draft.status)
        print("Approved :", draft.approved_at)
        print("=" * 70)

        return draft

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


def reject_reply_draft(draft_id: int):
    db = SessionLocal()

    try:
        draft = (
            db.query(ReplyDraft)
            .filter(ReplyDraft.id == draft_id)
            .first()
        )

        if not draft:
            raise ValueError(
                f"Reply draft with id={draft_id} was not found."
            )

        if draft.status != "pending":
            raise ValueError(
                f"Draft id={draft_id} cannot be rejected "
                f"because its status is '{draft.status}'."
            )

        draft.status = "rejected"

        db.commit()
        db.refresh(draft)

        print()
        print("=" * 70)
        print("REPLY DRAFT REJECTED")
        print("=" * 70)
        print("Draft ID :", draft.id)
        print("Email ID :", draft.email_id)
        print("Status   :", draft.status)
        print("=" * 70)

        return draft

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()