from app.services.reply_draft_service import generate_reply_drafts


def main():
    generate_reply_drafts(limit=10)


if __name__ == "__main__":
    main()