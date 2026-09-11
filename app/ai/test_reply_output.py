from app.database.database import SessionLocal
from app.database.models import ReplyDraft


def main():
    db = SessionLocal()

    try:
        draft = (
            db.query(ReplyDraft)
            .filter(ReplyDraft.email_id == 17)
            .order_by(ReplyDraft.id.desc())
            .first()
        )

        if not draft:
            raise ValueError("No reply draft found for email ID 17.")

        print("=" * 70)
        print("AI GENERATED REPLY")
        print("=" * 70)
        print("Draft ID:", draft.id)
        print("Email ID:", draft.email_id)
        print("Status:", draft.status)
        print("-" * 70)
        print(draft.draft_text)
        print("=" * 70)

    finally:
        db.close()


if __name__ == "__main__":
    main()