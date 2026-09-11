from app.database.database import SessionLocal
from app.database.models import Email


def main():
    db = SessionLocal()

    try:
        test_email = Email(
            provider_message_id="TEST_REPLY_FLOW_001",
            thread_id="TEST_THREAD_001",
            sender="recruiter@example.com",
            recipient="you@example.com",
            subject="Python Developer Interview",
            body=(
                "Hi, we reviewed your application for the Python "
                "Developer position. We would like to schedule an "
                "interview. Please let us know your availability "
                "this week."
            ),
            category="Job Inquiry",
            priority="MEDIUM",
            intent="Schedule a Python Developer interview.",
            summary=(
                "The recruiter wants to schedule an interview "
                "and is asking for availability."
            ),
            requires_reply=True,
            status="received",
        )

        db.add(test_email)
        db.commit()

        print()
        print("=" * 70)
        print("TEST EMAIL CREATED")
        print("=" * 70)
        print("Email ID:", test_email.id)
        print("Subject :", test_email.subject)
        print("Reply   :", test_email.requires_reply)
        print("=" * 70)

    finally:
        db.close()


if __name__ == "__main__":
    main()