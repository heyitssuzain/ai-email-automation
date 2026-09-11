from app.services.reply_approval_service import approve_reply_draft


def main():
    draft_id = 1

    draft = approve_reply_draft(draft_id)

    print()
    print("Final status:", draft.status)


if __name__ == "__main__":
    main()