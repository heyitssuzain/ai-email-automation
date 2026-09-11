from app.database.database import SessionLocal
from app.database.models import Email
from app.services.ai_email_service import analyze_email_with_retry


def main():
    db = SessionLocal()

    try:
        email = (
            db.query(Email)
            .filter(Email.id == 14)
            .first()
        )

        if not email:
            raise ValueError("Email ID 14 not found.")

        print()
        print("=" * 70)
        print("ATTACHMENT-AWARE AI ANALYSIS")
        print("=" * 70)
        print("Email ID:", email.id)
        print("Subject:", email.subject)
        print("=" * 70)

        analysis = analyze_email_with_retry(
            email,
            db,
        )

        email.category = analysis.category
        email.priority = analysis.priority
        email.intent = analysis.intent
        email.summary = analysis.summary
        email.requires_reply = analysis.requires_reply

        db.commit()
        db.refresh(email)

        print()
        print("=" * 70)
        print("ANALYSIS SAVED")
        print("=" * 70)
        print("Category       :", email.category)
        print("Priority       :", email.priority)
        print("Intent         :", email.intent)
        print("Summary        :", email.summary)
        print("Requires Reply :", email.requires_reply)
        print("=" * 70)

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()