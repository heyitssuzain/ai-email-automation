from app.services.ai_email_service import (
    analyze_unprocessed_emails,
)


def main():
    analyze_unprocessed_emails(
        limit=10
    )


if __name__ == "__main__":
    main()