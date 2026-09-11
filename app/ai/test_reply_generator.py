from app.ai.reply_generator import generate_reply


def main():
    reply = generate_reply(
        sender="recruiter@example.com",
        subject="Python Developer Interview",
        body=(
            "Hi, we reviewed your profile for our Python Developer "
            "position. Please let us know your availability for an interview."
        ),
        category="Job Inquiry",
        priority="MEDIUM",
        intent="Schedule an interview for a Python Developer position.",
        summary=(
            "The sender wants to schedule an interview and is asking "
            "for the recipient's availability."
        ),
    )

    print()
    print("=" * 70)
    print("AI REPLY DRAFT")
    print("=" * 70)
    print(reply)
    print("=" * 70)


if __name__ == "__main__":
    main()