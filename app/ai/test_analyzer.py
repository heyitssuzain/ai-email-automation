from app.ai.analyzer import analyze_email


def main():
    result = analyze_email(
        sender="hr@example.com",
        subject="Python Developer Job Opportunity",
        body=(
            "Hello, we reviewed your profile and would "
            "like to discuss a Python Developer position. "
            "Please reply with your availability for an interview."
        ),
    )

    print()
    print("=" * 60)
    print("AI EMAIL ANALYSIS")
    print("=" * 60)

    print("Category       :", result.category)
    print("Priority       :", result.priority)
    print("Intent         :", result.intent)
    print("Summary        :", result.summary)
    print("Requires Reply :", result.requires_reply)

    print("=" * 60)


if __name__ == "__main__":
    main()